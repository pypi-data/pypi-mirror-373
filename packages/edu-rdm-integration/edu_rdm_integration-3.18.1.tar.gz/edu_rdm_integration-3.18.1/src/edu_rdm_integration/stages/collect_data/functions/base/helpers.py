from edu_function_tools.helpers import (
    EduFunctionHelper,
    EduRunnerHelper,
)

from edu_rdm_integration.core.operations import (
    ALL_OPERATIONS,
    UPDATED_OPERATIONS,
)


class BaseCollectingDataRunnerHelper(EduRunnerHelper):
    """Базовый класс помощников ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingDataFunctionHelper(EduFunctionHelper):
    """Базовый класс помощников функций сбора данных для интеграции с "Региональная витрина данных"."""

    def get_filtered_operations(self, with_deleted: bool = False) -> tuple[int]:
        """Возвращает кортеж отфильтрованных операций."""
        return ALL_OPERATIONS if with_deleted else UPDATED_OPERATIONS
