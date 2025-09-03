from abc import (
    ABCMeta,
)

from edu_rdm_integration.stages.collect_data.functions.base.functions import (
    BaseCollectingCalculatedDataFunction,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.helpers import (
    BaseCollectingCalculatedExportedDataFunctionHelper,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.results import (
    BaseCollectingCalculatedExportedDataFunctionResult,
)
from edu_rdm_integration.stages.collect_data.functions.calculated.base.validators import (
    BaseCollectingCalculatedExportedDataFunctionValidator,
)


class BaseCollectingCalculatedExportedDataFunction(BaseCollectingCalculatedDataFunction, metaclass=ABCMeta):
    """Базовый класс функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""

    def _prepare_helper_class(self) -> type[BaseCollectingCalculatedExportedDataFunctionHelper]:
        """Возвращает класс помощника функции."""
        return BaseCollectingCalculatedExportedDataFunctionHelper

    def _prepare_validator_class(self) -> type[BaseCollectingCalculatedExportedDataFunctionValidator]:
        """Возвращает класс валидатора функции."""
        return BaseCollectingCalculatedExportedDataFunctionValidator

    def _prepare_result_class(self) -> type[BaseCollectingCalculatedExportedDataFunctionResult]:
        """Возвращает класс результата функции."""
        return BaseCollectingCalculatedExportedDataFunctionResult
