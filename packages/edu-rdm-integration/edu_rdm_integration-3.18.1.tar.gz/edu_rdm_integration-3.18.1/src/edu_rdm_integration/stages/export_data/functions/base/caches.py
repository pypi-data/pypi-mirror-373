from typing_extensions import (
    TYPE_CHECKING,
)

from edu_function_tools.caches import (
    EduFunctionCacheStorage,
    EduRunnerCacheStorage,
)


if TYPE_CHECKING:
    from educommon.integration_entities.entities import (
        BaseEntity,
    )


class BaseExportDataRunnerCacheStorage(EduRunnerCacheStorage):
    """Базовый кеш помощников ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""


class BaseExportDataFunctionCacheStorage(EduFunctionCacheStorage):
    """Базовый кеш помощников функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def _prepare_entity_instances(self, model_ids, *args, **kwargs) -> list['BaseEntity']:
        """Формирование списка объектов сущностей для дальнейшей выгрузки.

        Необходимо переопределить логику формирования объектов у потомков.
        """
        return []

    def __init__(self, *args, model_ids, entities, **kwargs):
        super().__init__(*args, **kwargs)

        self._entity_enum_value = entities[0]
        self._model_ids = model_ids

    def _prepare(self, *args, **kwargs):
        """Заполнение кеша данными."""
        self.entity_instances = self._prepare_entity_instances(model_ids=self._model_ids)
