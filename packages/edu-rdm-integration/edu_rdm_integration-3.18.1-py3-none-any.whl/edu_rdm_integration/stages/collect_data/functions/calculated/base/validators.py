from edu_function_tools.validators import (
    EduFunctionValidator,
    EduRunnerValidator,
)


class BaseCollectingCalculatedExportedDataRunnerValidator(EduRunnerValidator):
    """Базовый класс валидаторов ранеров функций сбора расчетных данных для интеграции с РВД."""

    def validate(self, runnable):
        """Расширение метода валидации."""
        super().validate(runnable=runnable)


class BaseCollectingCalculatedExportedDataFunctionValidator(EduFunctionValidator):
    """Базовый класс валидаторов функций сбора расчетных данных для интеграции с РВД."""

    def validate(self, runnable):
        """Расширение метода валидации."""
        super().validate(runnable=runnable)
