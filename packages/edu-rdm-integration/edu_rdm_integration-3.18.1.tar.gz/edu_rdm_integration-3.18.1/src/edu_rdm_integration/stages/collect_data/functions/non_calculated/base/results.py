from edu_function_tools.results import (
    EduFunctionResult,
    EduRunnerResult,
)


class BaseCollectingExportedDataRunnerResult(EduRunnerResult):
    """Базовый класс результатов работы ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingExportedDataFunctionResult(EduFunctionResult):
    """Базовый класс результатов работы функций сбора данных для интеграции с "Региональная витрина данных"."""
