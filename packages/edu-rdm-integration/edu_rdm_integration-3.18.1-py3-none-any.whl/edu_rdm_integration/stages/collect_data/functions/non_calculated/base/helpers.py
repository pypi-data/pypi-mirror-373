from edu_rdm_integration.stages.collect_data.functions.base.helpers import (
    BaseCollectingDataFunctionHelper,
    BaseCollectingDataRunnerHelper,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.caches import (
    BaseCollectingExportedDataFunctionCacheStorage,
    BaseCollectingExportedDataRunnerCacheStorage,
)


class BaseCollectingExportedDataRunnerHelper(BaseCollectingDataRunnerHelper):
    """Базовый класс помощников ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""

    def _prepare_cache_class(self) -> type[BaseCollectingExportedDataRunnerCacheStorage]:
        """Возвращает класс кеша помощника ранера."""
        return BaseCollectingExportedDataRunnerCacheStorage


class BaseCollectingExportedDataFunctionHelper(BaseCollectingDataFunctionHelper):
    """Базовый класс помощников функций сбора данных для интеграции с "Региональная витрина данных"."""

    def _prepare_cache_class(self) -> type[BaseCollectingExportedDataFunctionCacheStorage]:
        """Возвращает класс кеша помощника функции."""
        return BaseCollectingExportedDataFunctionCacheStorage
