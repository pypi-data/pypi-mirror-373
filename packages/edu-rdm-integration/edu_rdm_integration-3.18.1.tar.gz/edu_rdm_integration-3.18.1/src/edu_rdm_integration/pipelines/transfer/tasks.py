from datetime import (
    datetime,
)
from typing import (
    TYPE_CHECKING,
    Optional,
)

import celery
from celery.schedules import (
    crontab,
)
from django.conf import (
    settings,
)
from django.utils import (
    timezone,
)

from educommon import (
    logger,
)
from educommon.async_task.models import (
    AsyncTaskType,
    RunningTask,
)
from educommon.async_task.tasks import (
    UniquePeriodicAsyncTask,
)
from educommon.django.db.mixins.validation import (
    QuerySet,
)
from educommon.utils.date import (
    get_today_min_datetime,
)

from edu_rdm_integration.core.consts import (
    FAST_TRANSFER_TASK_QUEUE_NAME,
    LONG_TRANSFER_TASK_QUEUE_NAME,
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.core.enums import (
    CommandType,
)
from edu_rdm_integration.core.helpers import (
    save_command_log_link,
)
from edu_rdm_integration.pipelines.transfer.enums import (
    EntityLevelQueueTypeEnum,
)
from edu_rdm_integration.pipelines.transfer.mixins import (
    BaseTransferLatestEntitiesDataMixin,
)
from edu_rdm_integration.pipelines.transfer.models import (
    TransferredEntity,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataCommandProgress,
)
from edu_rdm_integration.stages.collect_data.operations import (
    BaseCollectLatestModelsData,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataCommandProgress,
)
from edu_rdm_integration.stages.export_data.operations import (
    ExportLatestEntitiesData,
)


if TYPE_CHECKING:
    from django.db.models import (
        QuerySet,
    )


class BaseTransferLatestEntitiesDataPeriodicTask(BaseTransferLatestEntitiesDataMixin, UniquePeriodicAsyncTask):
    """Базовая периодическая задача сбора и выгрузки данных для переиспользования в разных очередях."""

    def __init__(self) -> None:
        super().__init__()

        self._period_ended_at: Optional[datetime] = None

    def _get_period_ended_at(self):
        """Определяет единую дату окончания периода сбора.

        Это нужно для исключения разного времени окончания сбора при явном запуске функции - чтобы
        избежать ошибки экспорта при недосборе данных.
        """
        if not self._period_ended_at:
            self._period_ended_at = timezone.now()

        return self._period_ended_at

    def _run_collect_model_data(self, model: str, task_id: str) -> None:
        """Запускает сбор данных модели РВД."""
        command = self._create_collect_command(model, task_id)
        collect_model_data = self._prepare_collect_model_data_class(command)
        collect_model_data.collect()

        command.refresh_from_db(fields=['stage_id'])
        save_command_log_link(command, settings.RDM_COLLECT_LOG_DIR)

    def _run_export_entity_data(self, entity: str, task_id: str) -> None:
        """Запускает экспорт данных сущности РВД."""
        command = self._create_export_command(entity, task_id)
        if command:
            export_entity_data = self._prepare_export_entity_data_class(command)
            export_entity_data.export()

            command.refresh_from_db(fields=['stage_id'])
            save_command_log_link(command, settings.RDM_EXPORT_LOG_DIR)

    def _create_collect_command(self, model: str, task_id: str) -> RDMCollectingDataCommandProgress:
        """Создает команду сбора данных моделей РВД."""
        manager = self._collecting_data_managers[model]
        manager_last_collected = (
            self._collecting_data_manager_to_logs_period_end.get(manager.uuid) or get_today_min_datetime()
        )

        period_started_at = manager_last_collected
        period_ended_at = self._get_period_ended_at()

        return RDMCollectingDataCommandProgress.objects.create(
            model_id=model,
            logs_period_started_at=period_started_at,
            logs_period_ended_at=period_ended_at,
            task_id=task_id,
            type=CommandType.AUTO,
        )

    def _create_export_command(self, entity: str, task_id: str) -> Optional[RDMExportingDataCommandProgress]:
        """Создает команду экспорта данных сущностей РВД."""
        manager = self._exporting_data_managers[entity]
        manager_last_exported = self._exporting_data_manager_to_period_end.get(manager.uuid)

        if manager_last_exported:
            period_started_at = manager_last_exported
            period_ended_at = timezone.now()

            return RDMExportingDataCommandProgress.objects.create(
                entity_id=entity,
                period_started_at=period_started_at,
                period_ended_at=period_ended_at,
                task_id=task_id,
                type=CommandType.AUTO,
            )

        return None

    def _prepare_collect_model_data_class(
        self, command: RDMCollectingDataCommandProgress
    ) -> BaseCollectLatestModelsData:
        """Подготавливает объект класса сбора данных моделей РВД."""
        return BaseCollectLatestModelsData(
            models=[command.model_id],
            logs_period_started_at=command.logs_period_started_at,
            logs_period_ended_at=command.logs_period_ended_at,
            command_id=command.id,
            use_times_limit=True,
        )

    def _prepare_export_entity_data_class(self, command: RDMExportingDataCommandProgress) -> ExportLatestEntitiesData:
        """Подготавливает объект класса экспорта данных сущностей РВД.

        При экспорте данных передаем параметр task_id для обновления поля "Описание"
        наименованиями выгруженных сущностей.
        """
        return ExportLatestEntitiesData(
            entities=[command.entity_id],
            period_started_at=command.period_started_at,
            period_ended_at=command.period_ended_at,
            command_id=command.id,
            task_id=self.request.id,
        )

    def process(self, *args, **kwargs):
        """Выполняет задачу."""
        super().process(*args, **kwargs)

        self._period_ended_at = None
        self.prepare_collect_export_managers()

        task_id = (
            RunningTask.objects.filter(
                pk=self.request.id,
            )
            .values_list('pk', flat=True)
            .first()
        )

        collected_entity_models = set()

        for entity_enum, export_enabled in sorted(
            self._transferred_entities, key=lambda entity: entity[0].order_number
        ):
            entity_models = self._entites_models_map.get(entity_enum.key, ())
            for model_enum_value in entity_models:
                if model_enum_value.key not in collected_entity_models:
                    collected_entity_models.add(model_enum_value.key)
                    try:
                        self._run_collect_model_data(model_enum_value.key, task_id)
                    except Exception as e:
                        logger.warning(e)

                        continue

            try:
                if export_enabled:
                    self._run_export_entity_data(entity_enum.key, task_id)
            except Exception as e:
                logger.warning(e)

                continue


class TransferLatestEntitiesDataPeriodicTask(BaseTransferLatestEntitiesDataPeriodicTask):
    """Периодическая задача сбора и выгрузки данных."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Периодическая задача сбора и экспорта данных РВД'
    lock_expire_seconds = settings.RDM_TRANSFER_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_TRANSFER_TASK_MINUTE,
        hour=settings.RDM_TRANSFER_TASK_HOUR,
        day_of_week=settings.RDM_TRANSFER_TASK_DAY_OF_WEEK,
    )

    def get_entity_qs(self) -> 'QuerySet[TransferredEntity]':
        """Возвращает QuerySet сущностей сбора и выгрузки."""
        return TransferredEntity.objects.filter(queue_level=EntityLevelQueueTypeEnum.BASE)


class TransferLatestEntitiesDataFastPeriodicTask(BaseTransferLatestEntitiesDataPeriodicTask):
    """Периодическая задача сбора и выгрузки данных для быстрого уровня очереди."""

    queue = FAST_TRANSFER_TASK_QUEUE_NAME
    routing_key = FAST_TRANSFER_TASK_QUEUE_NAME
    description = 'Периодическая задача сбора и экспорта данных РВД (быстрый уровень)'
    lock_expire_seconds = settings.RDM_FAST_TRANSFER_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_FAST_TRANSFER_TASK_MINUTE,
        hour=settings.RDM_FAST_TRANSFER_TASK_HOUR,
        day_of_week=settings.RDM_FAST_TRANSFER_TASK_DAY_OF_WEEK,
    )

    def get_entity_qs(self) -> 'QuerySet[TransferredEntity]':
        """Возвращает QuerySet сущностей сбора и выгрузки."""
        return TransferredEntity.objects.filter(queue_level=EntityLevelQueueTypeEnum.FAST)


class TransferLatestEntitiesDataLongPeriodicTask(BaseTransferLatestEntitiesDataPeriodicTask):
    """Периодическая задача сбора и выгрузки данных для долгого уровня очереди."""

    queue = LONG_TRANSFER_TASK_QUEUE_NAME
    routing_key = LONG_TRANSFER_TASK_QUEUE_NAME
    description = 'Периодическая задача сбора и экспорта данных РВД (долгий уровень)'
    lock_expire_seconds = settings.RDM_LONG_TRANSFER_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_LONG_TRANSFER_TASK_MINUTE,
        hour=settings.RDM_LONG_TRANSFER_TASK_HOUR,
        day_of_week=settings.RDM_LONG_TRANSFER_TASK_DAY_OF_WEEK,
    )

    def get_entity_qs(self) -> 'QuerySet[TransferredEntity]':
        """Возвращает QuerySet сущностей сбора и выгрузки."""
        return TransferredEntity.objects.filter(queue_level=EntityLevelQueueTypeEnum.LONG)


celery_app = celery.app.app_or_default()
celery_app.register_task(TransferLatestEntitiesDataPeriodicTask)
celery_app.register_task(TransferLatestEntitiesDataFastPeriodicTask)
celery_app.register_task(TransferLatestEntitiesDataLongPeriodicTask)
