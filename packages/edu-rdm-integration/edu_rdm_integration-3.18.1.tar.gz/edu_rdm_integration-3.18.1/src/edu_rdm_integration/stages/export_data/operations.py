import os
from collections import (
    defaultdict,
)
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
)

from django.conf import (
    settings,
)
from django.db.models import (
    F,
    Model,
    Value,
)
from django.db.models.base import (
    ModelBase,
)
from django.db.models.functions import (
    Concat,
    Substr,
)
from django.db.transaction import (
    atomic,
)
from django.utils import (
    timezone,
)
from django.utils.datastructures import (
    OrderedSet,
)

from educommon import (
    logger,
)
from educommon.async_task.models import (
    RunningTask,
)
from educommon.utils.date import (
    get_today_max_datetime,
)
from educommon.utils.seqtools import (
    make_chunks,
)
from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
)
from edu_rdm_integration.core.operations import (
    BaseOperationData,
)
from edu_rdm_integration.core.signals import (
    manager_created,
)
from edu_rdm_integration.core.storages import (
    RegionalDataMartEntityStorage,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)
from edu_rdm_integration.stages.export_data.helpers import (
    get_exporting_managers_max_period_ended_dates,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataStage,
    RDMExportingDataSubStageStatus,
)


if TYPE_CHECKING:
    from edu_function_tools.managers import (
        EduRunnerManager,
    )


class BaseExportEntitiesData(BaseOperationData):
    """Базовый класс экспорта сущностей РВД за указанных период."""

    def __init__(
        self,
        entities: Iterable[str],
        period_started_at=datetime.combine(date.today(), time.min),
        period_ended_at=datetime.combine(date.today(), time.min),
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Если сущности не указаны, берется значение по умолчанию - все сущности:
        entities = entities if entities else RDMEntityEnum.get_enum_data().keys()
        self.entities: list[ModelEnumValue] = [RDMEntityEnum.get_model_enum_value(entity) for entity in entities]

        self.period_started_at = period_started_at
        self.period_ended_at = period_ended_at

        # Классы менеджеров Функций, которые должны быть запущены для выгрузки данных
        self._exporting_data_managers: set[type['EduRunnerManager']] = set()

        # Результаты работы Функций выгрузки данных
        self._exporting_data_results = []

        # Карта соответствия manager_id сущности и его основной модели
        self.manager_main_model_map: dict[str, ModelBase] = {}

    @property
    def _log_file_path(self) -> str:
        """Путь до лог файла."""
        return os.path.join(settings.MEDIA_ROOT, settings.RDM_EXPORT_LOG_DIR, f'{self.command_id}.log')

    def _has_stage_created_or_in_progress(self, manager_id: str, entity: str) -> bool:
        """Проверяет есть ли готовый к работе stage или в работе для данной сущности."""
        stage_created_or_in_progress = RDMExportingDataStage.objects.filter(
            manager_id=manager_id,
            status_id__in=(RDMExportingDataSubStageStatus.CREATED.key, RDMExportingDataSubStageStatus.IN_PROGRESS.key),
        ).exists()

        if stage_created_or_in_progress:
            logger.info(f'entity {entity} is skipped because it is already created or in progress!')

        return stage_created_or_in_progress

    def _fill_manager_entities_map(self, entity_storage: RegionalDataMartEntityStorage) -> None:
        """Заполнение словаря данных с классами менеджеров и их сущностями."""

    def _find_exporting_entities_data_managers(self):
        """Поиск менеджеров Функций выгрузки данных по сущностям РВД."""
        logger.info('find exporting entities data manager..')

        entity_storage = RegionalDataMartEntityStorage()
        entity_storage.prepare()

        exporting_entities_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA},
        )
        self._fill_manager_entities_map(entity_storage)

        entities = filter(lambda entity: entity.order_number != DEFAULT_ORDER_NUMBER, self.entities)

        for entity_enum in entities:
            manager_class = exporting_entities_data_managers_map.get(entity_enum.key)

            if manager_class and not self._has_stage_created_or_in_progress(manager_class.uuid, entity_enum.key):
                self.manager_main_model_map[manager_class.uuid] = entity_enum.main_model_enum.model
                self._exporting_data_managers.add(manager_class)

        logger.info('finding exporting entities data manager finished.')

    def _export_entities_data(self, *args, **kwargs):
        """Выгрузка данных по указанным сущностям."""
        logger.info('start exporting entities data..')

        kwargs['period_started_at'] = self.period_started_at
        kwargs['period_ended_at'] = self.period_ended_at

        for manager_class in self._exporting_data_managers:
            manager = manager_class(*args, is_only_main_model=True, **kwargs)

            if self.command_id:
                # Подается сигнал, что менеджер создан:
                manager_created.send(sender=manager, command_id=self.command_id)

            manager.run()

            self._exporting_data_results.append(manager.result)

        logger.info('exporting entities data finished.')

    def _export(self, *args, **kwargs):
        """Выполнение действий команды."""
        logger.info(f'start exporting data of entities - {", ".join([entity.key for entity in self.entities])}..')

        self._find_exporting_entities_data_managers()
        self._export_entities_data(*args, **kwargs)

        logger.info('exporting entities data finished.')

    def export(self, *args, **kwargs):
        """Запускает экспорт данных."""
        try:
            self._export(*args, **kwargs)
        except Exception as err:
            logger.exception(err)
            raise err
        finally:
            self._remove_file_handler()


class BaseExportLatestEntitiesData(BaseExportEntitiesData):
    """Базовый класс выгрузки сущностей с момента последней успешной выгрузки."""

    def __init__(
        self,
        entities: Iterable[str],
        period_started_at=datetime.combine(date.today(), time.min),
        period_ended_at=datetime.combine(date.today(), time.min),
        update_modified: bool = True,
        **kwargs,
    ):
        super().__init__(entities, period_started_at, period_ended_at, **kwargs)

        self._exporting_data_managers: set[type['EduRunnerManager']] = OrderedSet()

        # Словарь данных с классами менеджеров и их сущностями
        self._manager_entities_map: dict[type[object], list[str]] = defaultdict(set)

        self.async_task = self._get_async_task()
        self.task_id = kwargs.get('task_id')

        self.update_modified = update_modified

    def _get_async_task(self) -> Model:
        """Возвращает модель асинхронной задачи."""
        raise NotImplementedError

    def _set_description_to_async_task(self, exported_entities: Iterable[str]) -> None:
        """Добавляет в описание асинхронной задачи список выгруженных сущностей."""
        if exported_entities and self.task_id:
            entities_str = ', '.join(exported_entities)

            self.async_task.objects.filter(pk=self.task_id).update(
                description=Substr(
                    Concat('description', Value(f': {entities_str}')),
                    1,
                    self.async_task._meta.get_field('description').max_length,
                )
            )

    def _fill_manager_entities_map(self, entity_storage: RegionalDataMartEntityStorage) -> None:
        """Заполнение словаря данных с классами менеджеров и их сущностями."""
        self._manager_entities_map = entity_storage.prepare_manager_entities_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA},
        )

    def _update_model_modified_field(self, manager_id: str, last_finished_export_data: datetime) -> None:
        """Обновляет поле modified у невыгруженных записей."""
        if not self.update_modified:
            return

        model = self.manager_main_model_map[manager_id]
        now = timezone.now()

        querysets_to_update = (
            # Не заполнен подэтап выгрузки и modified записи модели < левой границы периода команды latest:
            model.objects.filter(
                exporting_sub_stage_id__isnull=True,
                modified__lt=last_finished_export_data,
            ),
            # Подэтап выгрузки указанной в записи модели имеет статус FAILED
            # и modified записи > даты выгрузки указанной в записи модели сбора (ended_at подэтапа выгрузки)
            # и modified записи модели < левой границы периода команды latest (даты последней удачной выгрузки):
            model.objects.filter(
                exporting_sub_stage__ended_at__gt=now - timedelta(days=365),
                exporting_sub_stage__status_id=RDMExportingDataSubStageStatus.FAILED.key,
                modified__gt=F('exporting_sub_stage__ended_at'),
                modified__lt=last_finished_export_data,
            ),
        )

        for queryset in querysets_to_update:
            not_exported_model_ids = queryset.values_list('id', flat=True).iterator()

            with atomic():
                for model_ids in make_chunks(
                    iterable=not_exported_model_ids,
                    size=settings.RDM_UPDATE_NON_EXPORTED_CHUNK_SIZE,
                ):
                    queryset.filter(id__in=model_ids).update(modified=now)

    def _export_entities_data(self, *args, **kwargs) -> None:
        """Запуск Функций по для экспорта данных."""
        logger.info('export entities data..')

        # Массив с выгружаемыми сущностями для поля "Описание" в асинхронной задаче
        exported_entities = []

        managers_max_period_ended = get_exporting_managers_max_period_ended_dates(self._exporting_data_managers)

        for manager_class in self._exporting_data_managers:
            manager_last_exported = managers_max_period_ended.get(manager_class.uuid)

            kwargs['period_started_at'] = manager_last_exported or timezone.now()
            kwargs['period_ended_at'] = get_today_max_datetime()

            # Обновить поля modified у модели сущности:
            self._update_model_modified_field(
                manager_id=manager_class.uuid,
                last_finished_export_data=kwargs['period_started_at'],
            )

            manager = manager_class(*args, **kwargs)

            if self.command_id:
                # Подается сигнал, что менеджер создан:
                manager_created.send(sender=manager, command_id=self.command_id)

            manager.run()

            self._exporting_data_results.append(manager.result)

            # Если сущность была выгружена, то добавим ее в список exported_entities
            if manager.result.entities and self.task_id:
                exported_entities.extend(self._manager_entities_map.get(manager_class))

        self._set_description_to_async_task(exported_entities)

        logger.info('collecting entities data finished.')


class ExportEntitiesData(BaseExportEntitiesData):
    """Экспорт сущностей РВД за указанных период."""


class ExportLatestEntitiesData(BaseExportLatestEntitiesData):
    """Класс выгрузки сущностей с момента последней успешной выгрузки."""

    def _get_async_task(self) -> Model:
        """Возвращает модель асинхронной задачи."""
        return RunningTask
