import celery
from celery.schedules import (
    crontab,
)
from django.conf import (
    settings,
)
from django.core.cache import (
    cache,
)

from educommon.async_task.models import (
    AsyncTaskType,
)
from educommon.async_task.tasks import (
    UniquePeriodicAsyncTask,
)

from edu_rdm_integration.core.consts import (
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.stages.upload_data.enums import (
    FileUploadStatusEnum,
)
from edu_rdm_integration.stages.upload_data.helpers import (
    UploadStatusHelper,
)
from edu_rdm_integration.stages.upload_data.models import (
    RDMExportingDataSubStageUploaderClientLog,
)
from edu_rdm_integration.stages.upload_data.operations import (
    UploadData,
)
from edu_rdm_integration.stages.upload_data.queues import (
    RdmRedisSubStageAttachmentQueue,
)


class RDMCheckUploadStatus(UniquePeriodicAsyncTask):
    """Периодическая задача для сбора статусов по загрузке файла в витрину."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Сбор статусов загрузки данных в витрину "Региональная витрина данных"'
    lock_expire_seconds = settings.RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.UNKNOWN
    run_every = crontab(
        minute=settings.RDM_UPLOAD_STATUS_TASK_MINUTE,
        hour=settings.RDM_UPLOAD_STATUS_TASK_HOUR,
        day_of_week=settings.RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK,
    )

    def process(self, *args, **kwargs):
        """Выполнение."""
        super().process(*args, **kwargs)

        # Получаем незавершенные загрузки данных в витрину
        in_progress_uploads = RDMExportingDataSubStageUploaderClientLog.objects.filter(
            file_upload_status=FileUploadStatusEnum.IN_PROGRESS,
            is_emulation=False,
        ).select_related('attachment')

        UploadStatusHelper(in_progress_uploads, cache).run()


class UploadDataAsyncTask(UniquePeriodicAsyncTask):
    """Формирование очереди файлов и их отправка."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Отправка данных в витрину "Региональная витрина данных"'
    lock_expire_seconds = settings.RDM_UPLOAD_DATA_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.SYSTEM
    run_every = crontab(
        minute=settings.RDM_UPLOAD_DATA_TASK_MINUTE,
        hour=settings.RDM_UPLOAD_DATA_TASK_HOUR,
        day_of_week=settings.RDM_UPLOAD_DATA_TASK_DAY_OF_WEEK,
    )

    def process(self, *args, **kwargs):
        """Выполнение."""
        super().process(*args, **kwargs)

        queue = RdmRedisSubStageAttachmentQueue()
        upload_data = UploadData(
            data_cache=cache,
            queue=queue,
        )

        upload_result = upload_data.upload_data()

        task_result = {
            'Общий объем отправленных файлов': f'{upload_result["total_file_size"]}',
            'Очередь отправки переполнена': 'Да' if upload_result['queue_is_full'] else 'Нет',
            'Сущности, отправленные в витрину': upload_result['uploaded_entities'],
        }

        self.set_progress(values=task_result)


celery_app = celery.app.app_or_default()
celery_app.register_task(RDMCheckUploadStatus)
celery_app.register_task(UploadDataAsyncTask)
