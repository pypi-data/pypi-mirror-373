from typing import (
    Optional,
)

from edu_function_tools.strategies import (
    EduSyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.caches import (
    BaseCollectingExportedDataFunctionCacheStorage,
    BaseCollectingExportedDataRunnerCacheStorage,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.errors import (
    BaseCollectingExportedDataError,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.functions import (
    BaseCollectingExportedDataFunction,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.helpers import (
    BaseCollectingExportedDataFunctionHelper,
    BaseCollectingExportedDataRunnerHelper,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.managers import (
    BaseCollectingExportedDataRunnerManager,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.presenters import (
    BaseCollectingExportedDataResultPresenter,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.results import (
    BaseCollectingExportedDataFunctionResult,
    BaseCollectingExportedDataRunnerResult,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.runners import (
    BaseCollectingExportedDataRunner,
)
from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.validators import (
    BaseCollectingExportedDataFunctionValidator,
    BaseCollectingExportedDataRunnerValidator,
)


class CollectingExportedDataFunctionImplementationStrategy(
    EduSyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy,
):
    """Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение.

    Используется для функций сбора данных для выгрузки в "Региональная витрина данных".
    """

    @classmethod
    def _prepare_uuid(cls):
        """Получение UUID класса. Используется при регистрации сущности в базе данных.

        Если ничего не возвращает, то регистрация в БД не будет произведена.
        """
        return '475eb094-b7fc-422a-a8d2-6cf3e0859cae'

    @classmethod
    def _prepare_verbose_name(cls) -> str:
        """Полное наименование для дальнейшей регистрации и отображения пользователю."""
        return (
            'Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение '
            'функций сбора данных для выгрузки в "Региональная витрина данных"'
        )

    @classmethod
    def _prepare_tags(cls) -> list[str]:
        """Список тегов, по которым сущность можно будет осуществлять поиск."""
        return [REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA]

    @classmethod
    def _prepare_key(cls) -> str:
        """Возвращает уникальный идентификатор стратегии создания функции."""
        return 'REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA'

    @classmethod
    def _prepare_title(cls) -> str:
        """Возвращает название стратегии создания функции."""
        return (
            'Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение '
            'функций сбора данных для выгрузки в "Региональная витрина данных". Сохранение производится после удачной '
            'работы функции'
        )

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """Формирование названия шаблона создания функции."""
        return 'function_collect_data_template'

    def _prepare_manager_class(self):
        """Устанавливает класс менеджера."""
        self._manager_class = BaseCollectingExportedDataRunnerManager

    def _prepare_runner_class(self):
        """Устанавливает класс ранера."""
        self._runner_class = BaseCollectingExportedDataRunner

    def _prepare_function_class(self):
        """Устанавливает класс Функции."""
        self._function_class = BaseCollectingExportedDataFunction

    def _prepare_runner_helper_class(self):
        """Устанавливает класс помощника ранера."""
        self._runner_helper_class = BaseCollectingExportedDataRunnerHelper

    def _prepare_function_helper_class(self):
        """Устанавливает класс помощника функции."""
        self._function_helper_class = BaseCollectingExportedDataFunctionHelper

    def _prepare_runner_validator_class(self):
        """Устанавливает класс валидатора ранера."""
        self._runner_validator_class = BaseCollectingExportedDataRunnerValidator

    def _prepare_function_validator_class(self):
        """Устанавливает класс валидатора Функции."""
        self._function_validator_class = BaseCollectingExportedDataFunctionValidator

    def _prepare_runner_cache_storage_class(self):
        """Устанавливает класс хранилища кешей ранера."""
        self._runner_cache_storage_class = BaseCollectingExportedDataRunnerCacheStorage

    def _prepare_function_cache_storage_class(self):
        """Устанавливает класс хранилища кешей Функции."""
        self._function_cache_storage_class = BaseCollectingExportedDataFunctionCacheStorage

    def _prepare_error_class(self):
        """Устанавливает класс ошибки."""
        self._error_class = BaseCollectingExportedDataError

    def _prepare_runner_result_class(self):
        """Устанавливает класс результата."""
        self._runner_result_class = BaseCollectingExportedDataRunnerResult

    def _prepare_function_result_class(self):
        """Устанавливает класс результата."""
        self._function_result_class = BaseCollectingExportedDataFunctionResult

    def _prepare_result_presenter_class(self):
        """Устанавливает класс презентера результата."""
        self._result_presenter_class = BaseCollectingExportedDataResultPresenter
