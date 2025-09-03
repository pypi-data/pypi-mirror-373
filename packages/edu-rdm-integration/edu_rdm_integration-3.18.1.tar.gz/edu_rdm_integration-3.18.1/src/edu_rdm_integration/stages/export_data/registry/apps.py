from django.apps import (
    AppConfig,
)


class RDMExportDataRegistryAppConfig(AppConfig):
    """Приложение для организации экспорта данных моделей РВД из интерфейса."""

    name = 'edu_rdm_integration.stages.export_data.registry'
    label = 'edu_rdm_integration_export_data_registry'
    verbose_name = 'Экспорт данных моделей РВД из интерфейса'
