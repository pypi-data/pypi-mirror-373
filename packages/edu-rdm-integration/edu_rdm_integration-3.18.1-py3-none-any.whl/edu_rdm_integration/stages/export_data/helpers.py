import os
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
    Union,
)

from django.conf import (
    settings,
)
from django.db.models import (
    CharField,
    OuterRef,
    Subquery,
    Value,
)
from django.db.models.functions import (
    Cast,
    Coalesce,
    Least,
)
from django.db.transaction import (
    atomic,
)

from educommon import (
    logger,
)

from edu_rdm_integration.apps import (
    EduRDMIntegrationConfig,
)


if TYPE_CHECKING:
    from typing import (
        NamedTuple,
    )

    from django.db.models import (
        Model,
    )

    from edu_rdm_integration.rdm_models.models import (
        BaseRDMModel,
    )
    from edu_rdm_integration.stages.export_data.functions.base.managers import (
        BaseExportDataRunnerManager,
    )


@atomic
def set_failed_status_suspended_exporting_data_stages() -> dict[str, int]:
    """Установить статус 'Завершено с ошибками' для зависших этапов и подэтапов экспорта.

    Экспорт считается зависшим в случае если за определенное в параметре RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT время,
    отсутствуют изменения в связанных подэтапах. Параметр RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT определяется
    в настройках приложения.
    """
    from edu_rdm_integration.stages.export_data.models import (
        RDMExportingDataStage,
        RDMExportingDataStageStatus,
        RDMExportingDataSubStage,
        RDMExportingDataSubStageStatus,
    )

    changed_status_result = {
        'change_stage_count': 0,
        'change_sub_stage_count': 0,
    }

    current_datetime = datetime.now()
    suspended_time_at = current_datetime - timedelta(minutes=settings.RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT)

    suspended_stage_ids = set(
        RDMExportingDataStage.objects.annotate(
            last_sub_stage_started_at=Coalesce(
                Subquery(
                    RDMExportingDataSubStage.objects.filter(stage_id=OuterRef('pk'))
                    .values('started_at')
                    .order_by('-started_at')[:1]
                ),
                Value(datetime.combine(date.min, time.min)),
            )
        )
        .filter(
            last_sub_stage_started_at__lt=suspended_time_at,
            status__in=(
                RDMExportingDataStageStatus.CREATED.key,
                RDMExportingDataStageStatus.IN_PROGRESS.key,
            ),
        )
        .values_list('pk', flat=True)
    )

    if suspended_stage_ids:
        logger.info(f'find suspended ExportingDataStage: {", ".join(map(str, suspended_stage_ids))}..')

        change_stage_count = RDMExportingDataStage.objects.filter(
            pk__in=suspended_stage_ids,
        ).update(
            status=RDMExportingDataStageStatus.FAILED.key,
            ended_at=current_datetime,
        )

        change_sub_stage_count = RDMExportingDataSubStage.objects.filter(
            stage_id__in=suspended_stage_ids,
        ).update(
            status=RDMExportingDataSubStageStatus.FAILED.key,
            ended_at=current_datetime,
        )

        changed_status_result.update(
            {
                'change_stage_count': change_stage_count,
                'change_sub_stage_count': change_sub_stage_count,
            }
        )

    return changed_status_result


def get_exporting_managers_max_period_ended_dates(
    exporting_managers: Iterable['BaseExportDataRunnerManager'],
) -> dict[str, 'datetime']:
    """Возвращает дату и время последнего успешного этапа экспорта для менеджеров Функций экспорта."""
    from edu_rdm_integration.stages.export_data.models import (
        RDMExportingDataStage,
        RDMExportingDataStageStatus,
    )

    managers_last_period_ended = (
        RDMExportingDataStage.objects.filter(
            manager_id__in=[manager.uuid for manager in exporting_managers],
            id=Subquery(
                RDMExportingDataStage.objects.filter(
                    manager_id=OuterRef('manager_id'),
                    status_id=RDMExportingDataStageStatus.FINISHED.key,
                )
                .order_by('-id')
                .values('id')[:1]
            ),
        )
        .annotate(
            str_manager_id=Cast('manager_id', output_field=CharField()),
            last_period_ended_at=Least('period_ended_at', 'started_at'),
        )
        .values_list(
            'str_manager_id',
            'last_period_ended_at',
        )
    )

    return {manager_id: last_period_ended_at for manager_id, last_period_ended_at in managers_last_period_ended}


def get_exporting_data_stage_attachment_path(instance, filename):
    """Возвращает путь до файла-вложения в этап выгрузки данных сущности.

    Args:
        instance: объект ExportingDataStage
        filename: имя загружаемого файла

    Returns:
        Строковое представление пути
    """
    datetime_now = datetime.now()

    return os.path.join(
        settings.UPLOADS,
        EduRDMIntegrationConfig.label,
        datetime_now.strftime('%Y/%m/%d'),
        instance.exporting_data_sub_stage.__class__.__name__.lower(),
        str(instance.exporting_data_sub_stage_id),
        str(instance.operation),
        filename,
    )


def set_entity_field_by_model_object(
    entity: 'BaseRDMModel', model_object: Union['Model', 'NamedTuple'], mapping: dict[str, str]
) -> None:
    """Обновление значений полей сущности по измененным полям модели.

    Args:
        entity: Выгружаемая сущность;
        model_object: Объект модели с измененными полями;
        mapping: Словарь маппинга полей модели к полям сущности
    """
    for model_field, entity_field in mapping.items():
        if hasattr(model_object, model_field):
            setattr(entity, entity_field, getattr(model_object, model_field))


def get_isoformat_timezone():
    """Возвращает временную зонну в ISO представлении."""
    return datetime.now().astimezone().isoformat()[-6:]
