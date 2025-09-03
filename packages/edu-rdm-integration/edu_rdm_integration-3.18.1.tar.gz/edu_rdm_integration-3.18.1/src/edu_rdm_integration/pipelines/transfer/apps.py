from django.apps import (
    AppConfig,
)


class RDMTransferPipelineAppConfig(AppConfig):
    """Приложение для организации процесса сбора, экспорта в файлы и отправки файлов в витрину."""

    name = 'edu_rdm_integration.pipelines.transfer'
    label = 'edu_rdm_integration_transfer_pipeline'
    verbose_name = 'Приложение для организации процесса сбора, экспорта в файлы и отправки файлов в витрину.'

    def ready(self):
        """Готовность приложения."""
        if self.name == 'edu_rdm_integration.pipelines.transfer':
            # ruff: noqa: F401
            from . import (
                tasks,
            )
