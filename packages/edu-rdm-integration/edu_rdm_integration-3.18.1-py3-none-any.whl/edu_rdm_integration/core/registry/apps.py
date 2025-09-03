from django.apps import (
    AppConfig,
)


class RDMCoreRegistryAppConfig(AppConfig):
    """Приложение с базовым функционалом для создания реестров РВД."""

    name = 'edu_rdm_integration.core.registry'
    label = 'edu_rdm_integration_core_registry'
    verbose_name = 'Базовая часть реестров РВД'
