from django.apps import (
    AppConfig,
)


class RDMCollectDataStageAppConfig(AppConfig):
    """Приложение для организации этапа сбора данных."""

    name = 'edu_rdm_integration.stages.collect_data'
    label = 'edu_rdm_integration_collect_data_stage'
    verbose_name = 'Сбор данных'
