from edu_function_tools.validators import (
    EduFunctionValidator,
    EduRunnerValidator,
)


class BaseCollectingExportedDataRunnerValidator(EduRunnerValidator):
    """Базовый класс валидаторов ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)


class BaseCollectingExportedDataFunctionValidator(EduFunctionValidator):
    """Базовый класс валидаторов функций сбора данных для интеграции с "Региональная витрина данных"."""

    def validate(self, runnable):
        """Выполнение валидации."""
        super().validate(runnable=runnable)
