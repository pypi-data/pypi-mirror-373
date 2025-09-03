from edu_function_tools.results import (
    EduFunctionResult,
    EduRunnerResult,
)


class BaseCollectingCalculatedExportedDataRunnerResult(EduRunnerResult):
    """Базовый класс результатов работы ранеров функций сбора расчетных данных для РВД."""


class BaseCollectingCalculatedExportedDataFunctionResult(EduFunctionResult):
    """Базовый класс результатов работы функций сбора расчетных данных для интеграции с РВД."""
