from edu_function_tools.results import (
    EduFunctionResult,
    EduRunnerResult,
)


class BaseExportDataRunnerResult(EduRunnerResult):
    """Базовый класс результата работы ранера функций выгрузки данных для интеграции с РВД."""


class BaseExportDataFunctionResult(EduFunctionResult):
    """Базовый класс результата функции выгрузки данных для интеграции с РВД."""
