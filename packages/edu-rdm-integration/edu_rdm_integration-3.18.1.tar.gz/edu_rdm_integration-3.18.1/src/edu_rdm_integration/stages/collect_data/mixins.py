from educommon.async_task.models import (
    AsyncTaskType,
)

from edu_rdm_integration.core.consts import (
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.core.helpers import (
    save_command_log_link,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataCommandProgress,
)
from edu_rdm_integration.stages.collect_data.operations import (
    BaseCollectModelsDataByGeneratingLogs,
)


class CollectCommandMixin:
    """Класс-примесь для запуска команды сборки моделей."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Сбор данных моделей РВД'
    task_type = AsyncTaskType.SYSTEM

    def get_collect_command(self, command_id: int) -> RDMCollectingDataCommandProgress:
        """Возвращает экземпляр модели команды запуска."""
        command = RDMCollectingDataCommandProgress.objects.get(id=command_id)

        return command

    def get_collect_models_class(self):
        """Возвращает класс для сбора данных."""
        return BaseCollectModelsDataByGeneratingLogs

    def run_collect_command(self, command) -> None:
        """Запуск команды сбора."""
        collect_models_data_class = self.get_collect_models_class()
        collect_models_data_class(
            models=(command.model_id,),
            logs_period_started_at=command.logs_period_started_at,
            logs_period_ended_at=command.logs_period_ended_at,
            command_id=command.id,
            institute_ids=tuple(command.institute_ids or ()),
        ).collect()

    def save_collect_command_logs(self, command_id: int, log_dir: str):
        """Сохранение ссылки на файл логов в команде."""
        try:
            command = self.get_collect_command(command_id)
        except RDMCollectingDataCommandProgress.DoesNotExist:
            command = None

        if command:
            save_command_log_link(command, log_dir)
