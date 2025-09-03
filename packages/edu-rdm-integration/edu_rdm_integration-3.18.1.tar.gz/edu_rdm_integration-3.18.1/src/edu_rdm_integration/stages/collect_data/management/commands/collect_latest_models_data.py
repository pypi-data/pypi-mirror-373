from edu_rdm_integration.stages.collect_data.management.base import (
    BaseCollectModelDataCommand,
)
from edu_rdm_integration.stages.collect_data.operations import (
    BaseCollectLatestModelsData,
    BaseCollectModelsData,
)


class Command(BaseCollectModelDataCommand):
    """Команда для сбора на основе логов за период с последней сборки до указанной даты."""

    def _prepare_collect_models_data_class(self, *args, **kwargs) -> BaseCollectModelsData:
        return BaseCollectLatestModelsData(
            models=kwargs.get('models'),
            logs_period_started_at=kwargs.get('logs_period_started_at'),
            logs_period_ended_at=kwargs.get('logs_period_ended_at'),
        )
