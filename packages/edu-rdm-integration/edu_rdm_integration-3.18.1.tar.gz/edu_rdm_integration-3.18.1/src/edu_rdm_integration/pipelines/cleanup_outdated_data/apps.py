from django.apps import (
    AppConfig,
)


class RDMCleanupOutdatedDataAppConfig(AppConfig):
    """Приложение для организации процесса очистки устаревших данных РВД."""

    name = 'edu_rdm_integration.pipelines.cleanup_outdated_data'
    label = 'edu_rdm_integration_cleanup_outdated_data_pipeline'
    verbose_name = 'Приложение для организации процесса очистки устаревших данных РВД.'
