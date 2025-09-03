from django.apps import (
    AppConfig,
)


class RDMExportDataStageAppConfig(AppConfig):
    """Приложение для организации этапа выгрузки собранных данных в файлы."""

    name = 'edu_rdm_integration.stages.export_data'
    label = 'edu_rdm_integration_export_data_stage'
    verbose_name = 'Этап выгрузки данных в файлы'
