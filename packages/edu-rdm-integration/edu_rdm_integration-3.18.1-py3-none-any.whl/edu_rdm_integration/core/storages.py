from collections import (
    defaultdict,
)

from edu_function_tools.models import (
    EduEntityType,
)
from edu_function_tools.runners import (
    EduRunner,
)
from edu_function_tools.storages import (
    EduEntityStorage,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
)


class RegionalDataMartEntityStorage(EduEntityStorage):
    """Хранилище классов сущностей реализованных в системе.

    Собираются только те сущности, типы которых указаны в модели-перечислении
    edu_function_tools.models.EduEntityType. Расширение произведено в связи с необходимостью получения
    карт соответствия менеджеров и сущностей, функций и сущностей.
    """

    def _collect_runner_regional_data_mart_integration_entities(
        self,
        runner_class: type[EduRunner],
        runner_regional_data_mart_integration_entities: list[str],
    ):
        """Собирает и возвращает список сущностей."""
        for runnable_class in runner_class._prepare_runnable_classes():
            if hasattr(runnable_class, '_prepare_runnable_classes'):
                self._collect_runner_regional_data_mart_integration_entities(
                    runner_class=runnable_class,
                    runner_regional_data_mart_integration_entities=runner_regional_data_mart_integration_entities,
                )

                continue

            if hasattr(runnable_class, 'entities'):
                entities = getattr(runnable_class, 'entities')

                runner_regional_data_mart_integration_entities.extend(entities)

    def prepare_entities_map(
        self,
        entity_type: ModelEnumValue,
        tags: set[str],
        *args,
        **kwargs,
    ) -> dict[str, type[object]]:
        """Формирование карты соответствия сущности интеграции с РВД и сущности function_tools."""
        rdm_integration_function_tools_entities_map: dict[str, type[object]] = {}

        registered_function_tools_entities_classes = [
            entity['class']
            for entity in self.entities[entity_type.key].values()
            if not tags.difference(entity['class'].tags)
        ]

        for function_tools_entity_class in registered_function_tools_entities_classes:
            regional_data_mart_integration_entities = []

            if hasattr(function_tools_entity_class, 'runner_class'):
                runner_class = function_tools_entity_class.runner_class

                self._collect_runner_regional_data_mart_integration_entities(
                    runner_class=runner_class,
                    runner_regional_data_mart_integration_entities=regional_data_mart_integration_entities,
                )
            elif hasattr(function_tools_entity_class, 'entities'):
                regional_data_mart_integration_entities = function_tools_entity_class.entities

            for rdm_integration_entity in regional_data_mart_integration_entities:
                rdm_integration_function_tools_entities_map[rdm_integration_entity.key] = function_tools_entity_class

        return rdm_integration_function_tools_entities_map

    def prepare_entities_manager_map(self, tags: set[str]) -> dict[str, type[object]]:
        """Формирование карты соответствия сущности интеграции с "Региональная витрина данных" и менеджера Функции.

        Стоит учитывать, что в рамках одной Функции может производиться работа с несколькими сущностями.
        """
        return self.prepare_entities_map(
            entity_type=EduEntityType.MANAGER,
            tags=tags,
        )

    def prepare_manager_entities_map(self, tags: set[str]) -> dict[type[object], list[str]]:
        """Формирование карты соответствия менеджера Функции и сущности интеграции с "Региональная витрина данных".

        Стоит учитывать, что в рамках одной Функции может производиться работа с несколькими сущностями.
        """
        _manager_entities_map = defaultdict(set)
        exporting_entities_data_managers_map = self.prepare_entities_manager_map(tags=tags)

        for entity in exporting_entities_data_managers_map:
            _manager_entities_map[exporting_entities_data_managers_map[entity]].add(entity)

        return _manager_entities_map

    def prepare_entities_functions_map(self, tags: set[str]) -> dict[str, type[object]]:
        """Формирование карты соответствия сущности интеграции с "Региональная витрина данных" и функции.

        Стоит учитывать, что в рамках одной Функции может производиться работа с несколькими сущностями.
        """
        return self.prepare_entities_map(
            entity_type=EduEntityType.FUNCTION,
            tags=tags,
        )

    def prepare_exporting_collecting_functions_map(self) -> dict[str, str]:
        """Возвращает карту соответствия функций выгрузки и сбора данных.

        Returns:
            Возвращает словарь в качестве ключей и значений используются UUID-ы функций.
        """
        exporting_collecting_functions_map = {}

        exporting_entities_data_functions_map = self.prepare_entities_functions_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA},
        )
        collecting_entities_data_functions_map = self.prepare_entities_functions_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA},
        )

        for entity in exporting_entities_data_functions_map.keys():
            exporting_collecting_functions_map[exporting_entities_data_functions_map[entity].uuid] = (
                collecting_entities_data_functions_map[entity].uuid
            )

        return exporting_collecting_functions_map
