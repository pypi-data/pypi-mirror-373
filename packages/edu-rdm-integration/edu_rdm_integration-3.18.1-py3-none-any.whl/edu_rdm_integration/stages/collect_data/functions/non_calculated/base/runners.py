from edu_rdm_integration.stages.collect_data.functions.base.runners import (
    BaseCollectingDataRunner,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.helpers import (
    BaseCollectingExportedDataRunnerHelper,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.results import (
    BaseCollectingExportedDataRunnerResult,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.validators import (
    BaseCollectingExportedDataRunnerValidator,
)


class BaseCollectingExportedDataRunner(BaseCollectingDataRunner):
    """Базовый класс ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""

    def _prepare_helper_class(self) -> type[BaseCollectingExportedDataRunnerHelper]:
        """Возвращает класс помощника ранера функции."""
        return BaseCollectingExportedDataRunnerHelper

    def _prepare_validator_class(self) -> type[BaseCollectingExportedDataRunnerValidator]:
        """Возвращает класс валидатора ранера функции."""
        return BaseCollectingExportedDataRunnerValidator

    def _prepare_result_class(self) -> type[BaseCollectingExportedDataRunnerResult]:
        """Возвращает класс результата ранера функции."""
        return BaseCollectingExportedDataRunnerResult
