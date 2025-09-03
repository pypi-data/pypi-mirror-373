from edu_rdm_integration.stages.collect_data.management.base import (
    BaseCollectModelDataCommand,
)
from edu_rdm_integration.stages.collect_data.operations import (
    BaseCollectModelsData,
    CollectModelsData,
)


class Command(BaseCollectModelDataCommand):
    """Команда для сбора данных моделей РВД за указанных период по существующим логам."""

    # flake8: noqa: A003
    help = 'Команда для сбора данных моделей РВД за указанных период по существующим логам.'

    def _prepare_collect_models_data_class(self, *args, **kwargs) -> BaseCollectModelsData:
        """Возвращает объект класса сбора данных моделей РВД."""
        return CollectModelsData(
            models=kwargs.get('models'),
            logs_period_started_at=kwargs.get('logs_period_started_at'),
            logs_period_ended_at=kwargs.get('logs_period_ended_at'),
        )
