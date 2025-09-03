from abc import (
    ABCMeta,
    abstractmethod,
)
from copy import (
    deepcopy,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Optional,
    Union,
)

from django.contrib.contenttypes.models import (
    ContentType,
)
from django.db.models import (
    Q,
)
from django.db.models.constants import (
    LOOKUP_SEP,
)

from educommon.audit_log.utils import (
    get_model_by_table,
)
from educommon.integration_entities.consts import (
    LOG_OPERATION_MAP,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from educommon.integration_entities.helpers import (
    EntitySaver,
)

from edu_rdm_integration.core.helpers import (
    Graph,
)
from edu_rdm_integration.core.mapping import (
    MODEL_FIELDS_LOG_FILTER,
)
from edu_rdm_integration.core.utils import (
    build_related_model_graph,
)
from edu_rdm_integration.stages.collect_data.functions.base.caches import (
    LogChange,
)
from edu_rdm_integration.stages.collect_data.functions.base.consts import (
    CACHED_OBJECTS_TYPE_MISMATCH_ERROR,
    NOT_SPECIFIED_QUEUE_TO_MODEL_ERROR,
)


if TYPE_CHECKING:
    from edu_function_tools.caches import (
        EduEntityCache,
    )

    from edu_rdm_integration.rdm_models.models import (
        BaseRDMModel,
    )
    from edu_rdm_integration.stages.collect_data.functions.base.caches import (
        IgnoreLogDependency,
    )


class ReformatLogsMixin:
    """Миксин для преобразования логов к удобному для работы виду в кешах помощников функций."""

    def _reformat_logs(self):
        """Производится преобразование логов к удобному для работы виду.

        Предполагается вложенные словари. На первом уровне ключом будет название
        модели, на втором идентификатор записи.
        """
        for log in self.raw_logs:
            model = get_model_by_table(log.table)._meta.label

            if getattr(self, '_log_only_models', None) and (model not in self._log_only_models):
                # Пропускаем, если модель не входит в список отслеживаемых
                continue

            operation = LOG_OPERATION_MAP[log.operation]

            if operation in EntityLogOperation.values:
                fields = log.transformed_data
            else:
                fields = {}

            # Если данных нет, то LogChange не формируем
            if not fields:
                continue

            log_change = LogChange(
                operation=operation,
                fields=fields,
            )

            if not self._filter_log(model, log_change):
                # Если модель не отслеживается, то запись лога не сохраняем
                continue

            if log_change.operation == EntityLogOperation.DELETE:
                self.logs[model][log.object_id] = [
                    log_change,
                ]
            else:
                self.logs[model][log.object_id].append(log_change)

    @staticmethod
    def _filter_log(model: str, log_change: LogChange) -> bool:
        """Производится проверка изменений на отслеживаемые поля."""
        is_filtered = False

        if model in MODEL_FIELDS_LOG_FILTER[log_change.operation]:
            filter_fields = MODEL_FIELDS_LOG_FILTER[log_change.operation][model]
            if filter_fields:
                # Если заданы конкретные поля, которые должны отслеживать
                for field in log_change.fields:
                    if field in filter_fields:
                        # Достаточно, чтобы хотя бы одно поле попало под фильтр
                        is_filtered = True
                        break
            else:
                # Модель отслеживается, но перечень фильтруемых полей не задан,
                # значит фильтруем все поля модели
                is_filtered = True

        return is_filtered


class BaseIgnoreLogMixin:
    """Миксин для исключения логов не подлежащих обработке.

    Позволяет указать зависимость логов от состояния вышестоящих зависимых объектов.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._graph = Graph()
        self._dependency: Optional['IgnoreLogDependency'] = None

    @staticmethod
    def _add_lookup_prefix(q_filter: Q, lookup_path_args: list[str]) -> Q:
        """Функция принимает Q-объект и добавляет префикс к каждому указанному полю."""
        new_q = Q(_negated=q_filter.negated, _connector=q_filter.connector)

        for child in q_filter.children:
            if isinstance(child, Q):
                new_child = BaseIgnoreLogMixin._add_lookup_prefix(child, lookup_path_args)
            else:
                field_name, lookup_value = child

                if isinstance(field_name, str):
                    field_name = LOOKUP_SEP.join((*lookup_path_args, field_name))
                elif isinstance(field_name, tuple):
                    field_name = (LOOKUP_SEP.join((*lookup_path_args, field_name[0])),) + field_name[1:]

                new_child = (field_name, lookup_value)

            new_q.add(new_child, q_filter.connector)

        return new_q

    def _build_filter(
        self,
        lookup_path_args: list[str],
        filter_params: Union[tuple[Q], dict[str, Any]],
        is_valid_lookup: bool = False,
    ) -> Q:
        """Построение фильтра."""
        # Всегда строим OR, так как соответствие любому из параметров фильтра будет однозначно свидетельствовать, что
        # данные являются некорректными и должны быть исключены из последующей обработки
        q_filter = Q(_connector=Q.OR)

        if is_valid_lookup:
            if isinstance(filter_params, dict):
                for field_name, value in filter_params.items():
                    q_filter.add((LOOKUP_SEP.join((*lookup_path_args, field_name)), value), Q.OR)
            else:
                for filter_param in filter_params:
                    if isinstance(filter_param, Q):
                        q_filter |= self._add_lookup_prefix(filter_param, lookup_path_args)
                    else:
                        raise ValueError('Please, check `DependencyFilter.filters`, incorrect value!')

        return q_filter

    def _exclude_logs(self, model_label: str, object_model_ids: Iterable[int]):
        """Исключаем логи из обработки."""
        for object_id in object_model_ids:
            if object_id in self.logs[model_label]:
                del self.logs[model_label][object_id]

    def _ignore_logs(self):
        """Исключение логов из обработки на основании описанных правил."""
        super()._ignore_logs()

        if not self._dependency:
            return

        model_label_separator = '.'

        for app_label, model_name in (model_label.split(model_label_separator) for model_label in self.logs):
            q_filter = Q(_connector=Q.OR)

            log_model = ContentType.objects.get(app_label=app_label.lower(), model=model_name.lower()).model_class()

            for dependency in self._dependency.dependency_filters:
                app_name, model_name = dependency.model_label.lower().split(model_label_separator)
                find_model = ContentType.objects.get(app_label=app_name, model=model_name).model_class()

                self._graph = build_related_model_graph(
                    self._graph, log_model, find_model, ignored_model_fields=self._dependency.ignore_model_fields
                )

                name_edges = self._graph.get_edges_between_vertices(
                    log_model._meta.model_name, find_model._meta.model_name
                )

                q_filter |= self._build_filter(
                    name_edges, dependency.filters, is_valid_lookup=bool(name_edges or find_model == log_model)
                )

            if q_filter:
                ignore_model_ids = log_model.objects.filter(
                    q_filter,
                    id__in=self.logs[log_model._meta.label],
                ).values_list('pk', flat=True)
                self._exclude_logs(log_model._meta.label, ignore_model_ids)


class FilteredSaveEntitiesFunctionMixin(metaclass=ABCMeta):
    """Миксин, реализующий фильтрацию объектов перед сохранением.

    Предназначен для использования в классах, которые занимаются сохранением сущностей, но при этом хотят исключить
    неизменённые объекты из операции записи, чтобы избежать лишних действий или запросов к базе данных.
    Для работы требует реализации абстрактного свойства `_model_to_cache_map` и `_model_to_save_queue_map`, которое
    определяет, какие сущности и с каким кешем нужно обработать.

    Attributes:
        _filtered_operations (tuple[EntityLogOperation]): : Операции, подлежащие фильтрации (по умолчанию только UPDATE)
        _saved_entities_to_cache_map (dict[type[BaseRDMModel], EduEntityCache]): Копия маппинга моделей на кэши,
            используемая для сравнения изменений
        _ignored_fields (dict[EntityLogOperation, tuple[str]]): Словарь полей, которые следует игнорировать при
            сравнении для каждой операции
    """

    _filtered_operations: tuple[EntityLogOperation, ...] = (EntityLogOperation.UPDATE,)
    _saved_entities_to_cache_map: dict[type['BaseRDMModel'], 'EduEntityCache'] = {}
    _ignored_fields = {
        EntityLogOperation.UPDATE: ('modified', 'operation', 'collecting_sub_stage', 'exporting_sub_stage'),
    }

    def _is_object_to_save(self, saved_object: 'BaseRDMModel', ignore_fields: Optional[Iterable[str]] = None) -> bool:
        """Проверяет, должен ли объект быть добавлен в очередь на сохранение.

        Args:
            saved_object ('BaseEntityModel'): Объект, который предполагается сохранить.
            ignore_fields (Optional[Iterable[str]]): Дополнительные поля, которые нужно игнорировать.

        Returns:
            bool: True, если объект был изменён и его нужно сохранить, иначе False.
        """
        save_object_type = type(saved_object)
        cache = self._saved_entities_to_cache_map.get(save_object_type)

        modified = True

        if cache and saved_object.pk:
            original_object = cache.get(id=saved_object.pk)

            if original_object:
                modified = self._is_save_object_modified(saved_object, original_object, ignore_fields)

        return modified

    def _is_save_object_modified(
        self,
        saved_object: 'BaseRDMModel',
        original_object: 'BaseRDMModel',
        ignore_fields: Optional[Iterable[str]] = None,
    ) -> bool:
        """Проверяет, были ли изменения в указанном объекте относительно оригинала.

        Args:
            saved_object ('BaseEntityModel'): Объект, который предполагается сохранить.
            original_object ('BaseEntityModel'): Оригинальное значение из кэша.
            ignore_fields (Optional[Iterable[str]]): Поля, которые следует игнорировать при сравнении.

        Returns:
            bool: True, если объект был изменён, иначе False.
        """
        if not isinstance(saved_object, type(original_object)):
            raise ValueError(CACHED_OBJECTS_TYPE_MISMATCH_ERROR)

        if saved_object.operation == EntityLogOperation.DELETE:
            return True

        if ignore_fields is None:
            ignore_fields = []

        # Сравниваем поля объектов
        for field in original_object._meta.fields:
            field_name = field.name

            # Пропускаем игнорируемые поля
            if field_name in ignore_fields:
                continue

            # Получаем текущее значение поля из измененного объекта
            current_value = getattr(saved_object, field_name)

            # Получаем оригинальное значение поля из кеша
            original_value = getattr(original_object, field_name)

            # Сравниваем значения
            if current_value != original_value:
                return True

        # Если все поля совпадают, объект не изменился
        return False

    def _before_prepare(self, *args, **kwargs):
        """Подготовительный этап перед началом обработки объектов.

        Сохраняет копию текущих сопоставлений объектов и кэшей, чтобы обеспечить чистое состояние для последующего
        сравнения.
        """
        self._saved_entities_to_cache_map = {
            model: deepcopy(cache) for model, cache in self._model_to_cache_map.items()
        }

        super()._before_prepare(*args, **kwargs)

    @property
    @abstractmethod
    def _model_to_cache_map(self) -> dict[type['BaseRDMModel'], 'EduEntityCache']:
        """Абстрактное свойство, возвращающее соответствие между типами моделей и их кэшами.

        Должно быть реализовано в дочернем классе. Используется для получения оригинальных данных объектов
        перед сравнением.

        Returns:
            dict[type[BaseRDMModel], EduEntityCache]: Словарь, где ключ — это тип модели, а значение —
                соответствующий кэш этой модели.
        """

    @property
    @abstractmethod
    def _model_to_save_queue_map(self) -> dict[type['BaseRDMModel'], dict]:
        """Абстрактное свойство, возвращающее соответствие между типами моделей и очередями сохранения.

        Должно быть реализовано в дочернем классе. Используется для определения, в какую очередь будет добавляться
        объект для сохранения.

        Returns:
            dict[type[BaseRDMModel], dict]: Словарь, где ключ — это тип модели, а значение — словарь, представляющий
                очередь сохранения для этой модели.
        """

    def _add_to_save_entities(
        self,
        save_object: 'BaseRDMModel',
        operation: EntityLogOperation,
    ):
        """Добавление в очередь сущности на сохранение."""
        try:
            to_save_queue: dict[EntityLogOperation, dict[int, 'BaseRDMModel']] = self._model_to_save_queue_map[
                type(save_object)
            ]
        except KeyError:
            raise KeyError(NOT_SPECIFIED_QUEUE_TO_MODEL_ERROR.format(save_object._meta.model_name))

        save_object.operation = operation
        save_object.collecting_sub_stage = self._sub_stage

        if operation == EntityLogOperation.CREATE:
            to_save_queue[EntityLogOperation.CREATE][save_object.id] = save_object
        elif operation in {EntityLogOperation.UPDATE, EntityLogOperation.DELETE}:
            if self._is_object_to_save(save_object, self._ignored_fields.get(operation)):
                to_save_queue[EntityLogOperation.UPDATE][save_object.id] = save_object

    def _get_entity_saver(self, model: 'BaseRDMModel') -> EntitySaver:
        """Возвращает экземпляр saver'а для указанной модели.

        Args:
            model (BaseRDMModel): Тип модели, для которой требуется получить saver.

        Returns:
            EntitySaver: Объект, отвечающий за сохранение сущностей указанного типа.
        """
        to_save_queue = self._model_to_save_queue_map[model]
        return EntitySaver(to_save_entities=to_save_queue, model=model)

    def _save_entities(self):
        """Выполняет сохранение всех отфильтрованных и подготовленных объектов.

        Перебирает все модели из `_model_to_save_queue_map` и вызывает соответствующий `EntitySaver`.
        """
        for model in self._model_to_save_queue_map:
            entity_saver = self._get_entity_saver(model)
            entity_saver()
