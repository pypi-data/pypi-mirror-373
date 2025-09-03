from abc import (
    abstractmethod,
)
from collections import (
    defaultdict,
)
from typing import (
    Union,
)

from edu_function_tools.caches import (
    EduFunctionCacheStorage,
    EduRunnerCacheStorage,
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
from educommon.utils.conversion import (
    int_or_none,
)

from edu_rdm_integration.core.mapping import (
    MODEL_FIELDS_LOG_FILTER,
)
from edu_rdm_integration.stages.collect_data.functions.base.caches import (
    LogChange,
)


class BaseCollectingExportedDataRunnerCacheStorage(EduRunnerCacheStorage):
    """Базовый кеш помощников ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingExportedDataFunctionCacheStorage(EduFunctionCacheStorage):
    """Базовый кеш помощников функций сбора данных для интеграции с "Региональная витрина данных"."""

    def __init__(self, raw_logs, is_merge_logs=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Необработанные логи как есть.
        self.raw_logs = raw_logs

        # TODO Перенести в базовый класс (https://jira.bars.group/browse/EDUSCHL-19991)
        # Необходимость объединения логов относящихся к одному объекту
        self.is_merge_logs = is_merge_logs

        # Подготовленные логи в виде:
        # {
        #     'person.person': {
        #         48939: [(1, {'surname': 'Иванов', 'snils': '157-283-394 92'...}), (2, {...})],
        #         44281: [(2, {...}), (2, {...}), ...],
        #         12600: [(3, {...})],
        #     },
        #     'schoolchild.schoolchild': {
        #         ...
        #     },
        # }
        self.logs: dict[str, dict[int, list[LogChange]]] = defaultdict(lambda: defaultdict(list))

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

    @staticmethod
    def _add_id_to_set(ids: set, _id: Union[int, str, None]) -> None:
        """Добавление значения id во множество ids."""
        _id = int_or_none(_id)
        if _id:
            ids.add(_id)

    def _reformat_logs(self):
        """Производится преобразование логов к удобному для работы виду.

        Предполагается вложенные словари. На первом уровне ключом будет название модели, на втором идентификатор записи.
        """
        for log in self.raw_logs:
            model = get_model_by_table(log.table)._meta.label
            operation = LOG_OPERATION_MAP[log.operation]

            if operation in (EntityLogOperation.CREATE, EntityLogOperation.DELETE):
                fields = log.transformed_data
            elif operation == EntityLogOperation.UPDATE:
                fields = log.transformed_changes
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
                if self.is_merge_logs:
                    self._merge_logs(self.logs[model][log.object_id], log_change)
                else:
                    self.logs[model][log.object_id].append(log_change)

    @staticmethod
    def _merge_logs(log_changes: list[LogChange], log_change: LogChange):
        """Производит объединение (накопление) изменений полей в рамках одного объекта."""
        if log_changes:
            log_changes[0].fields.update(log_change.fields)
        else:
            log_changes.append(log_change)

    def _ignore_logs(self):
        """Исключение логов из обработки на основании описанных правил."""

    def _prepare_logs(self):
        """Подготовка логов для дальнейшей работы."""
        self._reformat_logs()
        self._ignore_logs()

    @abstractmethod
    def _collect_product_model_ids(self):
        """Собирает идентификаторы записей моделей продукта с упором на логи."""

    @abstractmethod
    def _prepare_caches(self):
        """Формирование кэшей."""

    def _prepare(self, *args, **kwargs):
        """Запускает формирование кэша помощника Функции."""
        self._prepare_logs()
        self._collect_product_model_ids()
        self._prepare_caches()
