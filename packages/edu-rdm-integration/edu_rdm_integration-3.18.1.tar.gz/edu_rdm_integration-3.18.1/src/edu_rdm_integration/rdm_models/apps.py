from django.apps import (
    AppConfig,
)


class RDMModelsConfigApp(AppConfig):
    """Приложение для работы с моделями РВД."""

    name = 'edu_rdm_integration.rdm_models'
    label = 'edu_rdm_integration_models'
    verbose_name = 'Модели РВД'
