from typing import (
    Any,
    NamedTuple,
)

from django.db import (
    models,
)

from m3_db_utils.mixins import (
    BaseEnumRegisterMixin,
)
from m3_django_compat import (
    classproperty,
)

from edu_rdm_integration.core.typing import (
    MODEL_TYPE_VAR,
)
from edu_rdm_integration.core.utils import (
    camel_to_underscore,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)


class ModelEnumRegisterMixin(BaseEnumRegisterMixin):
    """Миксин, для регистрации модели в RegionalDataMartModelEnum."""

    enum = RDMModelEnum
    """Модель-перечисление в которую регистрируется модель."""

    creating_trigger_models: tuple[models.Model, ...] = ()
    """Перечень моделей по которым генерируются логи."""

    loggable_models: tuple[models.Model, ...] = ()
    """Перечень моделей по которым собираются логи."""

    @classproperty
    def key(self) -> str:
        """Ключ сущности в модели-перечислении RegionalDataMartEntityEnum."""
        return camel_to_underscore(self.__name__).upper()

    @classproperty
    def title(self):
        """Название сущности."""
        return self._meta.verbose_name

    @classmethod
    def get_register_params(cls) -> dict[str, Any]:
        """Параметры для регистрации сущности в модели перечислении RegionalDataMartEntityEnum."""
        register_params = super().get_register_params()
        register_params['model'] = cls
        register_params['creating_trigger_models'] = cls.creating_trigger_models
        register_params['loggable_models'] = cls.loggable_models

        return register_params


class FromNamedTupleMixin:
    """Миксин получения экземпляра модели из получаемого кэша значений."""

    @classmethod
    def from_namedtuple(cls: type[MODEL_TYPE_VAR], namedtuple: NamedTuple) -> MODEL_TYPE_VAR:
        """Создает экземпляр класса из NamedTuple."""
        return cls(**{field: getattr(namedtuple, field) for field in [f.column for f in cls._meta.get_fields()]})
