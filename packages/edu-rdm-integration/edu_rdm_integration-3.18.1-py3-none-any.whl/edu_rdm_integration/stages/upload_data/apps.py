from django.apps import (
    AppConfig,
)


class RDMUploadDataStageAppConfig(AppConfig):
    """Приложение для организации этапа выгрузки файлов в РВД."""

    name = 'edu_rdm_integration.stages.upload_data'
    label = 'edu_rdm_integration_upload_data_stage'
    verbose_name = 'Этап выгрузки файлов в РВД'

    def ready(self):
        """Готовность приложения."""
        if self.name == 'edu_rdm_integration.stages.upload_data':
            # ruff: noqa: F401
            from . import (
                tasks,
            )
