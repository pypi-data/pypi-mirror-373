from abc import (
    abstractmethod,
)
from collections import (
    defaultdict,
)
from typing import (
    Union,
)

from edu_function_tools.caches import (
    EduFunctionCacheStorage,
    EduRunnerCacheStorage,
)
from educommon.utils.conversion import (
    int_or_none,
)

from edu_rdm_integration.stages.collect_data.functions.base.mixins import (
    ReformatLogsMixin,
)


class BaseCollectingCalculatedExportedDataRunnerCacheStorage(EduRunnerCacheStorage):
    """Базовый кеш помощников ранеров функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""


class BaseCollectingCalculatedExportedDataFunctionCacheStorage(ReformatLogsMixin, EduFunctionCacheStorage):
    """Базовый кеш помощников функций сбора расчетных данных для интеграции с "Региональная витрина данных"."""

    def __init__(self, raw_logs, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Необработанные логи как есть.
        self.raw_logs = raw_logs

        # Подготовленные логи в виде:
        # {
        #     'person.person': {
        #         48939: [(1, {'surname': 'Иванов', 'snils': '157-283-394 92'...}), (2, {...})],
        #         44281: [(2, {...}), (2, {...}), ...],
        #         12600: [(3, {...})],
        #     },
        #     'schoolchild.schoolchild': {
        #         ...
        #     },
        # }
        self.logs = defaultdict(lambda: defaultdict(list))

    def _ignore_logs(self):
        """Исключение логов из обработки на основании описанных правил."""

    def _prepare_logs(self):
        """Подготовка логов для дальнейшей работы."""
        self._reformat_logs()
        self._ignore_logs()

    @staticmethod
    def _add_id_to_set(ids: set, object_id: Union[int, str, None]) -> None:
        """Добавление значения id во множество ids."""
        object_id = int_or_none(object_id)
        if object_id:
            ids.add(object_id)

    @abstractmethod
    def _collect_product_model_ids(self):
        """Собирает идентификаторы записей моделей продукта с упором на логи."""

    @abstractmethod
    def _prepare_caches(self):
        """Формирование кэшей."""

    def _prepare(self, *args, **kwargs):
        """Запускает формирование кэша помощника Функции."""
        self._prepare_logs()
        self._collect_product_model_ids()
        self._prepare_caches()
