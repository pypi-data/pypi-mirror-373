from django.apps import (
    apps,
)
from django.db import (
    models,
)

from edu_rdm_integration.core.utils import (
    register_classes,
)
from edu_rdm_integration.rdm_models.mixins import (
    ModelEnumRegisterMixin,
)


def is_register_model(model: models.Model) -> bool:
    """Проверяет, является ли класс регистрируемой моделью."""
    return issubclass(model, ModelEnumRegisterMixin)


def register_models() -> None:
    """Регистрирует модели в RegionalDataMartModelEnum."""
    register_classes([m for m in apps.get_models() if is_register_model(m)])
