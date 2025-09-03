from edu_function_tools.validators import (
    EduFunctionValidator,
    EduRunnerValidator,
)


class BaseExportDataRunnerValidator(EduRunnerValidator):
    """Базовый класс валидаторов ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)


class BaseExportDataFunctionValidator(EduFunctionValidator):
    """Базовый класс валидаторов функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)
