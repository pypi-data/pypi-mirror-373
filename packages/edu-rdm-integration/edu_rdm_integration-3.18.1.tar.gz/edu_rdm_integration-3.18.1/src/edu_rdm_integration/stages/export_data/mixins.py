from educommon.async_task.models import (
    AsyncTaskType,
)

from edu_rdm_integration.core.consts import (
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.core.helpers import (
    save_command_log_link,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataCommandProgress,
)
from edu_rdm_integration.stages.export_data.operations import (
    ExportEntitiesData,
)


class ExportCommandMixin:
    """Класс-примесь для запуска команды выгрузки сущностей."""

    queue = TASK_QUEUE_NAME
    routing_key = TASK_QUEUE_NAME
    description = 'Экспорт данных сущностей РВД'
    task_type = AsyncTaskType.SYSTEM

    def get_export_command(self, command_id: int) -> RDMExportingDataCommandProgress:
        """Возвращает экземпляр модели команды запуска."""
        command = RDMExportingDataCommandProgress.objects.get(id=command_id)

        return command

    def run_export_command(self, command: RDMExportingDataCommandProgress) -> None:
        """Запуск команды выгрузки."""
        ExportEntitiesData(
            entities=(command.entity_id,),
            period_started_at=command.period_started_at,
            period_ended_at=command.period_ended_at,
            command_id=command.id,
        ).export()

    def save_export_command_logs(self, command_id: int, log_dir: str):
        """Сохранение ссылки на файл логов в команде."""
        try:
            command = self.get_export_command(command_id)
        except RDMExportingDataCommandProgress.DoesNotExist:
            command = None

        if command:
            save_command_log_link(command, log_dir)
