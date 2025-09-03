from edu_rdm_integration.stages.collect_data.functions.base.runners import (
    BaseCollectingDataRunner,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.helpers import (
    BaseCollectingCalculatedExportedDataRunnerHelper,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.results import (
    BaseCollectingCalculatedExportedDataRunnerResult,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.validators import (
    BaseCollectingCalculatedExportedDataRunnerValidator,
)


class BaseCollectingCalculatedExportedDataRunner(BaseCollectingDataRunner):
    """Базовый класс ранеров функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""

    def _prepare_helper_class(self) -> type[BaseCollectingCalculatedExportedDataRunnerHelper]:
        """Возвращает класс помощника ранера функции."""
        return BaseCollectingCalculatedExportedDataRunnerHelper

    def _prepare_validator_class(self) -> type[BaseCollectingCalculatedExportedDataRunnerValidator]:
        """Возвращает класс валидатора ранера функции."""
        return BaseCollectingCalculatedExportedDataRunnerValidator

    def _prepare_result_class(self) -> type[BaseCollectingCalculatedExportedDataRunnerResult]:
        """Возвращает класс результата ранера функции."""
        return BaseCollectingCalculatedExportedDataRunnerResult
