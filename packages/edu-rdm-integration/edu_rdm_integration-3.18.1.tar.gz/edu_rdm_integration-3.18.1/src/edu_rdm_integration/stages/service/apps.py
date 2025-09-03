from django.apps import (
    AppConfig,
)


class RDMServiceStageAppConfig(AppConfig):
    """Приложение для организации этапа сервисного обслуживания интеграции с РВД."""

    name = 'edu_rdm_integration.stages.service'
    label = 'edu_rdm_integration_service_stage'
    verbose_name = 'Этап сервисного обслуживания'

    def ready(self):
        """Готовность приложения."""
        if self.name == 'edu_rdm_integration.stages.service':
            # ruff: noqa: F401
            from . import (
                tasks,
            )
