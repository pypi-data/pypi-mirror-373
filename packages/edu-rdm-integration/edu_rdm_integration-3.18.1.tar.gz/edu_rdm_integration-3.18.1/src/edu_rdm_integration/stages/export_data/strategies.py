from typing import (
    Optional,
)

from edu_function_tools.strategies import (
    EduSyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
)
from edu_rdm_integration.stages.export_data.functions.base.caches import (
    BaseExportDataFunctionCacheStorage,
    BaseExportDataRunnerCacheStorage,
)
from edu_rdm_integration.stages.export_data.functions.base.errors import (
    BaseExportDataError,
)
from edu_rdm_integration.stages.export_data.functions.base.functions import (
    BaseExportDataFunction,
)
from edu_rdm_integration.stages.export_data.functions.base.helpers import (
    BaseExportDataFunctionHelper,
    BaseExportDataRunnerHelper,
)
from edu_rdm_integration.stages.export_data.functions.base.managers import (
    BaseExportDataRunnerManager,
)
from edu_rdm_integration.stages.export_data.functions.base.presenters import (
    BaseExportDataResultPresenter,
)
from edu_rdm_integration.stages.export_data.functions.base.results import (
    BaseExportDataFunctionResult,
    BaseExportDataRunnerResult,
)
from edu_rdm_integration.stages.export_data.functions.base.runners import (
    BaseExportDataRunner,
)
from edu_rdm_integration.stages.export_data.functions.base.validators import (
    BaseExportDataFunctionValidator,
    BaseExportDataRunnerValidator,
)


class ExportDataFunctionImplementationStrategy(
    EduSyncBaseRunnerLazySavingPredefinedQueueFunctionImplementationStrategy,
):
    """Стратегия создания функций выгрузки данных.

    Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение функций
    выгрузки данных для выгрузки в "Региональная витрина данных".
    """

    @classmethod
    def _prepare_uuid(cls):
        """Получение UUID класса. Используется при регистрации сущности в базе данных.

        Если ничего не возвращает, то регистрация в БД не будет произведена.
        """
        return '5f2f386c-4f02-4b4c-b17b-d475ef316916'

    @classmethod
    def _prepare_verbose_name(cls) -> str:
        """Полное наименование для дальнейшей регистрации и отображения пользователю."""
        return 'Стратегия создания функций выгрузки данных'

    @classmethod
    def _prepare_tags(cls) -> list[str]:
        """Список тегов, по которым сущность можно будет осуществлять поиск."""
        return [REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA]

    @classmethod
    def _prepare_key(cls) -> str:
        """Возвращает уникальный идентификатор стратегии создания функции."""
        return 'REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA'

    @classmethod
    def _prepare_title(cls) -> str:
        """Возвращает название стратегии создания функции."""
        return (
            'Стратегия создания функции с отложенным сохранением и предустановленной очередью объектов на сохранение '
            'функций выгрузки данных в "Региональная витрина данных". Сохранение производится после удачной работы '
            'функции'
        )

    @classmethod
    def _prepare_function_template_name(cls) -> Optional[str]:
        """Формирование названия шаблона создания функции."""
        return 'function_export_data_template'

    def _prepare_manager_class(self):
        """Устанавливает класс менеджера."""
        self._manager_class = BaseExportDataRunnerManager

    def _prepare_runner_class(self):
        """Устанавливает класс ранера."""
        self._runner_class = BaseExportDataRunner

    def _prepare_function_class(self):
        """Устанавливает класс Функции."""
        self._function_class = BaseExportDataFunction

    def _prepare_runner_helper_class(self):
        """Устанавливает класс помощника ранера."""
        self._runner_helper_class = BaseExportDataRunnerHelper

    def _prepare_function_helper_class(self):
        """Устанавливает класс помощника функции."""
        self._function_helper_class = BaseExportDataFunctionHelper

    def _prepare_runner_validator_class(self):
        """Устанавливает класс валидатора ранера."""
        self._runner_validator_class = BaseExportDataRunnerValidator

    def _prepare_function_validator_class(self):
        """Устанавливает класс валидатора Функции."""
        self._function_validator_class = BaseExportDataFunctionValidator

    def _prepare_runner_cache_storage_class(self):
        """Устанавливает класс хранилища кешей ранера."""
        self._runner_cache_storage_class = BaseExportDataRunnerCacheStorage

    def _prepare_function_cache_storage_class(self):
        """Устанавливает класс хранилища кешей Функции."""
        self._function_cache_storage_class = BaseExportDataFunctionCacheStorage

    def _prepare_error_class(self):
        """Устанавливает класс ошибки."""
        self._error_class = BaseExportDataError

    def _prepare_runner_result_class(self):
        """Устанавливает класс результата."""
        self._runner_result_class = BaseExportDataRunnerResult

    def _prepare_function_result_class(self):
        """Устанавливает класс результата."""
        self._function_result_class = BaseExportDataFunctionResult

    def _prepare_result_presenter_class(self):
        """Устанавливает класс презентера результата."""
        self._result_presenter_class = BaseExportDataResultPresenter
