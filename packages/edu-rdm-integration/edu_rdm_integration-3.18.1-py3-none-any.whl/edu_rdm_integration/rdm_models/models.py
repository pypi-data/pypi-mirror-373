from collections import (
    defaultdict,
)
from typing import (
    Optional,
    Type,
)

from django.db.models import (
    CASCADE,
    DateTimeField,
    ForeignKey,
    SmallIntegerField,
)
from m3.db import (
    BaseObjectModel,
)

from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from educommon.utils.seqtools import (
    topological_sort,
)
from m3_db_utils.models import (
    FictiveForeignKeyField,
    ModelEnumValue,
    TitledModelEnum,
)


class BaseRDMModel(ReprStrPreModelMixin, BaseObjectModel):
    """Базовая модель РВД."""

    created = DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True,
    )
    modified = DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['created', 'modified']

    class Meta:
        abstract = True


class BaseMainRDMModel(BaseRDMModel):
    """Абстрактная основная модель РВД.

    Является базовым классом для моделей РВД, которые являются основными для сущностей РВД.
    """

    collecting_sub_stage = ForeignKey(
        verbose_name='Подэтап сбора данных',
        to='edu_rdm_integration_collect_data_stage.RDMCollectingDataSubStage',
        on_delete=CASCADE,
    )
    exporting_sub_stage = ForeignKey(
        verbose_name='Подэтап выгрузки данных',
        to='edu_rdm_integration_export_data_stage.RDMExportingDataSubStage',
        blank=True,
        null=True,
        on_delete=CASCADE,
    )
    operation = SmallIntegerField(
        verbose_name='Действие',
        choices=EntityLogOperation.get_choices(),
    )

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['collecting_sub_stage', 'exporting_sub_stage', 'operation', 'created', 'modified']

    class Meta:
        abstract = True


class RDMModelEnum(TitledModelEnum):
    """Модель-перечисление моделей "Региональная витрина данных"."""

    is_strict_order_number = True
    """Флаг, указывающий на уникальность порядкового номера элементов модели-перечисления."""

    class Meta:
        db_table = 'rdm_model'
        extensible = True
        verbose_name = 'Модель-перечисление моделей "Региональной витрины данных"'
        verbose_name_plural = 'Модели-перечисления моделей "Региональной витрины данных"'

    @classmethod
    def _get_model_relations(cls, model: Type['BaseRDMModel']) -> dict[str, str]:
        """Получение списка связей модели РВД."""
        model_label_enum_data = cls.get_model_label_enum_data()
        model_relations = {}

        for field in model._meta.concrete_fields:
            if isinstance(field, FictiveForeignKeyField):
                model_label = field.to
            elif isinstance(field, ForeignKey):
                model_label = field.related_model._meta.label
            else:
                continue

            if model_label in model_label_enum_data:
                model_key = model_label_enum_data[model_label].key
                model_relations[field.attname] = model_key

        return model_relations

    @classmethod
    def _get_models_relations(cls) -> dict[str, dict[str, str]]:
        """Получение списка связей всех зарегистрированных моделей РВД."""
        model_label_enum_data = cls.get_model_label_enum_data()
        all_models = [model_enum_value.model for model_enum_value in model_label_enum_data.values()]

        models_relations = {}
        for model in all_models:
            model_key = model_label_enum_data[model._meta.label].key
            model_relations = cls._get_model_relations(model=model)

            if model_relations:
                models_relations[model_key] = model_relations

        return models_relations

    @classmethod
    def _sort_models_dependencies(cls, models_dependencies: list[tuple[str, str]]) -> list[str]:
        """Сортировка моделей РВД по зависимости друг от друга."""
        sorted_dependencies_models = topological_sort(models_dependencies)

        ordered_models = [*sorted_dependencies_models.cyclic, *reversed(sorted_dependencies_models.sorted)]

        return ordered_models

    @classmethod
    def _get_ordered_models(cls) -> list[str]:
        """Получение списка моделей РВД в порядке их зависимости.

        Есть возможность указать дополнительные модели, для которых совместно с зарегистрированными моделями РВД будет
        рассчитываться порядок.

        Returns:
            list[str]: список моделей РВД в порядке их зависимости
        """
        enum_keys = cls.get_model_enum_keys()
        models_relations = cls._get_models_relations()

        models_dependencies = []
        for model_key, model_relations in models_relations.items():
            for _, related_model_key in model_relations.items():
                models_dependencies.append((model_key, related_model_key))

        ordered_models = cls._sort_models_dependencies(models_dependencies=models_dependencies)

        without_dependencies = set(enum_keys).difference(set(ordered_models))

        ordered_models = [*without_dependencies, *ordered_models]

        return ordered_models

    @classmethod
    def _recalculate_order_numbers(cls, *args, **kwargs):
        """Перерасчет порядковых номеров элементов модели-перечисления.

        При добавлении новой модели РВД в модель-перечисление производится перерасчет порядковых номеров уже
        добавленных элементов. Порядок моделей РВД выстраивается по зависимости друг от друга. Зависимость определяется
        внешними ключами (ForeignKey) и фиктивными внешними ключами (FictiveForeignKey). Сначала идут модели не имеющие
        зависимостей, затем модели, которые зависят от других моделей. Сортировка моделей РВД происходит по алгоритму
        топологической сортировки.
        """
        ordered_model_keys = cls._get_ordered_models()

        for model_enum_value in cls._get_enum_data().values():
            if model_enum_value.is_manual_order_number:
                try:
                    manual_index_model_key = ordered_model_keys[model_enum_value.order_number - 1]
                except IndexError:
                    continue

                if manual_index_model_key != model_enum_value.key and cls.is_strict_order_number:
                    raise ValueError(
                        f'Order number "{model_enum_value.order_number}" is already in use in the "{cls.__name__}". '
                        f'Please choose a different one.'
                    )
            else:
                model_enum_value.order_number = ordered_model_keys.index(model_enum_value.key) + 1

    @classmethod
    def _calculate_tmp_order_number(cls) -> int:
        """Вычисление временного порядкового номера элемента модели-перечисления."""
        order_number_enum_data = cls._get_order_number_enum_data()

        order_numbers = order_number_enum_data.keys()
        tmp_order_number = max(order_numbers) + 1 if order_number_enum_data else 1

        return tmp_order_number

    @classmethod
    def _validate_manual_order_number(cls, order_number: int, model: Type['BaseRDMModel']):
        """Валидация пользовательского порядкового номера."""
        ordered_models = cls._get_ordered_models()

        try:
            manual_index_model = ordered_models[order_number - 1]
        except IndexError:
            return

        if manual_index_model != model._meta.label and cls.is_strict_order_number:
            raise ValueError(
                f'Order number "{order_number}" is already in use in the "{cls.__name__}". '
                f'Please choose a different one.'
            )

    @classmethod
    def _update_reverse_relations(cls):
        """Обновление обратных связей моделей РВД.

        У значения модели-перечисления
        """
        enum_data = cls._get_enum_data()
        # Обнуление обратных связей всех моделей
        for model_enum_value in enum_data.values():
            model_enum_value.reverse_relations = defaultdict(list)

        models_relations = cls._get_models_relations()

        for model_key, model_relations in models_relations.items():
            for field_name, related_model_key in model_relations.items():
                enum_data[related_model_key].reverse_relations[model_key].append(field_name)

    @classmethod
    def get_model_label_enum_data(cls) -> dict[str, Type['ModelEnumValue']]:
        """Получение словаря значений модели-перечисления с лейблом модели в качестве значения."""
        enum_data = cls._get_enum_data()

        model_label_enum_data = {model_value.model._meta.label: model_value for model_value in enum_data.values()}

        return model_label_enum_data

    @classmethod
    def extend(
        cls,
        key,
        model: Type['BaseRDMModel'] = None,
        title: str = '',
        creating_trigger_models: tuple = (),
        loggable_models: tuple = (),
        order_number: Optional[int] = None,
        *args,
        **kwargs,
    ):
        """Метод расширения модели-перечисления, например из плагина.

        Необходимо, чтобы сама модель-перечисление была расширяемой. Для этого необходимо, чтобы был установлен
        extensible = True в Meta.

        Args:
            key: ключ элемента перечисления, указывается заглавными буквами с разделителем нижнее подчеркивание
            title: название элемента перечисления
            model: модель, регистрируемая в модели-перечислении
            creating_trigger_models: модели продукта, которые инициируют создание записей модели РВД
            loggable_models: модели продукта, отслеживаемые в логах
            order_number: порядковый номер значения модели перечисления используемый при сортировке
            args: порядковые аргументы для модели-перечисления
            kwargs: именованные аргументы для модели-перечисления
        """
        if key.upper() in cls.get_model_enum_keys():
            raise ValueError('Model enum value with key "{key}" already exists.')

        if model is None:
            raise ValueError(f'Trying extend model "{cls.__name__}". Argument "model" is required.')

        is_manual_order_number = order_number is not None

        if order_number is None:
            order_number = cls._calculate_tmp_order_number()
        else:
            cls._validate_manual_order_number(order_number=order_number, model=model)

        model_enum_value = ModelEnumValue(
            key=key,
            model=model,
            title=title,
            creating_trigger_models=creating_trigger_models,
            loggable_models=loggable_models,
            order_number=order_number,
            is_manual_order_number=is_manual_order_number,
            reverse_relations=defaultdict(list),
            **kwargs,
        )
        setattr(cls, key, model_enum_value)

        cls._recalculate_order_numbers()
        cls._update_reverse_relations()
