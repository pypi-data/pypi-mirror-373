from django.apps import (
    AppConfig,
)


class RDMCollectDataRegistryAppConfig(AppConfig):
    """Приложение для организации сбора данных моделей РВД из интерфейса."""

    name = 'edu_rdm_integration.stages.collect_data.registry'
    label = 'edu_rdm_integration_collect_data_registry'
    verbose_name = 'Сбор данных моделей РВД из интерфейса'
