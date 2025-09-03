from collections import (
    defaultdict,
)
from typing import (
    TYPE_CHECKING,
)

from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
)
from edu_rdm_integration.core.storages import (
    RegionalDataMartEntityStorage,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)
from edu_rdm_integration.stages.collect_data.helpers import (
    get_collecting_managers_max_period_ended_dates,
)
from edu_rdm_integration.stages.export_data.helpers import (
    get_exporting_managers_max_period_ended_dates,
)


if TYPE_CHECKING:
    from datetime import (
        datetime,
    )

    from django.db.models import (
        QuerySet,
    )

    from edu_function_tools.managers import (
        EduRunnerManager,
    )

    from edu_rdm_integration.pipelines.transfer.models import (
        TransferredEntity,
    )


class BaseTransferLatestEntitiesDataMixin:
    """Миксин сбора и выгрузки данных."""

    def __init__(self) -> None:
        super().__init__()

        self._collecting_data_managers: dict[str, type['EduRunnerManager']] = {}
        self._collecting_data_manager_to_logs_period_end: dict[str, 'datetime'] = {}

        self._exporting_data_managers: dict[str, type['EduRunnerManager']] = {}
        self._exporting_data_manager_to_period_end: dict[str, 'datetime'] = {}

        self._transferred_entities = []
        self._entites_models_map = defaultdict(list)

    def get_entity_qs(self) -> 'QuerySet[TransferredEntity]':
        """Возвращает QuerySet сущностей сбора и выгрузки."""
        raise NotImplementedError

    def _collect_transferred_entities(self) -> None:
        """Собирает сущности РВД, по которым будет произведен сбор и экспорт данных."""
        self._transferred_entities = [
            (RDMEntityEnum.get_model_enum_value(key=entity), export_enabled)
            for entity, export_enabled in self.get_entity_qs().values_list('entity', 'export_enabled')
        ]

        # Собираем словарь по сущностям с моделями для сборки
        for entity, _ in self._transferred_entities:
            self._entites_models_map[entity.key].extend(
                (
                    model_enum
                    for model_enum in (*entity.additional_model_enums, entity.main_model_enum)
                    if model_enum.order_number != DEFAULT_ORDER_NUMBER
                )
            )

    def _collect_managers(self) -> None:
        """Собирает менеджеры Функций для сбора и выгрузки данных."""
        entity_storage = RegionalDataMartEntityStorage()
        entity_storage.prepare()

        collecting_models_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA},
        )
        exporting_entities_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA},
        )

        for entity_key, entity_models in self._entites_models_map.items():
            for entity_model in entity_models:
                collect_manager_class = collecting_models_data_managers_map.get(entity_model.key)
                if collect_manager_class:
                    self._collecting_data_managers[entity_model.key] = collect_manager_class

            export_manager_class = exporting_entities_data_managers_map.get(entity_key)
            if export_manager_class:
                self._exporting_data_managers[entity_key] = export_manager_class

    def _calculate_collecting_managers_logs_period_ended_at(self) -> None:
        """Определяет дату последнего успешного этапа сбора у менеджеров Функций сбора."""
        self._collecting_data_manager_to_logs_period_end = get_collecting_managers_max_period_ended_dates(
            self._collecting_data_managers.values()
        )

    def _calculate_exporting_managers_ended_at(self) -> None:
        """Определяет дату последнего успешного подэтапа экспорта у менеджеров Функций экспорта."""
        self._exporting_data_manager_to_period_end = get_exporting_managers_max_period_ended_dates(
            self._exporting_data_managers.values()
        )

    def prepare_collect_export_managers(self) -> None:
        """Подготовка менджеров сбора и экспорта."""
        self._collect_transferred_entities()
        self._collect_managers()
        self._calculate_collecting_managers_logs_period_ended_at()
        self._calculate_exporting_managers_ended_at()
