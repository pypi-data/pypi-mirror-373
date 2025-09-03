import celery
from celery.schedules import (
    crontab,
)
from django.conf import (
    settings,
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
from edu_rdm_integration.stages.collect_data.helpers import (
    set_failed_status_suspended_collecting_data_stages,
)
from edu_rdm_integration.stages.export_data.helpers import (
    set_failed_status_suspended_exporting_data_stages,
)


class CheckSuspendedExportedStagePeriodicTask(UniquePeriodicAsyncTask):
    """Периодическая задача поиска зависших этапов/подэтапов экспорта."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Поиск зависших этапов/подэтапов экспорта в "Региональная витрина данных"'
    lock_expire_seconds = settings.RDM_CHECK_SUSPEND_TASK_LOCK_EXPIRE_SECONDS
    task_type = AsyncTaskType.SYSTEM
    run_every = crontab(
        minute=settings.RDM_CHECK_SUSPEND_TASK_MINUTE,
        hour=settings.RDM_CHECK_SUSPEND_TASK_HOUR,
        day_of_week=settings.RDM_CHECK_SUSPEND_TASK_DAY_OF_WEEK,
    )

    def process(self, *args, **kwargs):
        """Выполнение задачи."""
        super().process(*args, **kwargs)

        change_status_collecting_result = set_failed_status_suspended_collecting_data_stages()
        change_status_exporting_result = set_failed_status_suspended_exporting_data_stages()

        task_result = {
            'Прервано сборок': (
                f'Этапов {change_status_collecting_result["change_stage_count"]}'
                f' и подэтапов {change_status_collecting_result["change_sub_stage_count"]}'
            ),
            'Прервано выгрузок': (
                f'Этапов {change_status_exporting_result["change_stage_count"]}'
                f' и подэтапов {change_status_exporting_result["change_sub_stage_count"]}'
            ),
        }

        self.set_progress(values=task_result)


celery_app = celery.app.app_or_default()
celery_app.register_task(CheckSuspendedExportedStagePeriodicTask)
