from edu_rdm_integration.stages.export_data.management.base import (
    BaseExportEntityDataCommand,
)
from edu_rdm_integration.stages.export_data.operations import (
    BaseExportEntitiesData,
    ExportLatestEntitiesData,
)


class Command(BaseExportEntityDataCommand):
    """Команда для экспорта данных за период с последней сборки до указанной даты."""

    # flake8: noqa: A003
    help = 'Команда для запуска функции экспорта данных для интеграции с "Региональная витрина данных"'

    def _prepare_export_entities_data_class(self, *args, **kwargs) -> BaseExportEntitiesData:
        """Возвращает объект класса экспорта данных сущностей РВД."""
        return ExportLatestEntitiesData(
            entities=kwargs.get('entities'),
            period_started_at=kwargs.get('period_started_at'),
            period_ended_at=kwargs.get('period_ended_at'),
            task_id=kwargs.get('task_id'),
            update_modified=kwargs.get('update_modified'),
        )
