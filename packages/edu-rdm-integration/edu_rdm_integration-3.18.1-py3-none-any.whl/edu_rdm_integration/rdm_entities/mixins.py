from typing import (
    Any,
    Optional,
)

from m3_db_utils.mixins import (
    BaseEnumRegisterMixin,
)
from m3_db_utils.models import (
    ModelEnumValue,
)
from m3_django_compat import (
    classproperty,
)

from edu_rdm_integration.core.utils import (
    camel_to_underscore,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)


class EntityEnumRegisterMixin(BaseEnumRegisterMixin):
    """Миксин, для регистрации сущности в RegionalDataMartEntityEnum."""

    enum = RDMEntityEnum
    """Модель-перечисление в которую регистрируется сущность."""

    main_model_enum: ModelEnumValue
    """Значение RegionalDataMartModelEnum,
    основной модели РВД для формирования сущности."""

    additional_model_enums: tuple[ModelEnumValue] = ()
    """Перечень дополнительных значений RegionalDataMartModelEnum,
    которые участвуют в формировании записей сущностей"""

    title: str
    """Расшифровка сущности модели-перечисления"""

    @classproperty
    def key(self) -> str:
        """Ключ сущности в модели-перечислении RegionalDataMartEntityEnum."""
        return camel_to_underscore(self.__name__.rsplit('Entity', 1)[0], upper=True)

    @classmethod
    def get_register_params(cls) -> dict[str, Any]:
        """Параметры для регистрации сущности в модели перечислении RegionalDataMartEntityEnum."""
        register_params = super().get_register_params()

        register_params['main_model_enum'] = getattr(cls, 'main_model_enum', None) or cls.get_main_model_enum()
        register_params['entity'] = cls
        register_params['additional_model_enums'] = cls.additional_model_enums or cls.get_additional_model_enums()

        return register_params

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_main_model_enum(cls) -> Optional[ModelEnumValue]:
        """Возвращает значение модели перечисление основной модели сущности.

        В классе определяется поле main_model_enum или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_additional_model_enums(cls) -> tuple[ModelEnumValue, ...]:
        """Возвращает кортеж значений модели-перечисления основной модели сущности.

        В классе определяется поле additional_model_enums или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return ()
