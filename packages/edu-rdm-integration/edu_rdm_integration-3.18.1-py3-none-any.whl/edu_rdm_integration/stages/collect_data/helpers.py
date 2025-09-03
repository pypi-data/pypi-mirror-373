from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
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

from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStage,
    RDMCollectingDataStageStatus,
    RDMCollectingDataSubStage,
    RDMCollectingDataSubStageStatus,
)


if TYPE_CHECKING:
    from edu_rdm_integration.rdm_models.models import (
        BaseRDMModel,
    )
    from edu_rdm_integration.stages.collect_data.functions.non_calculated.base.managers import (
        BaseCollectingExportedDataRunnerManager,
    )


@atomic
def set_failed_status_suspended_collecting_data_stages() -> dict[str, int]:
    """Установить статус 'Завершено с ошибками' для зависших этапов и подэтапов сбора.

    Сборка считается зависшей в случае если за определенное в параметре RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT время,
    отсутствуют изменения в связанных подэтапах. Параметр RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT определяется
    в настройках приложения.
    """
    changed_status_result = {
        'change_stage_count': 0,
        'change_sub_stage_count': 0,
    }

    current_datetime = datetime.now()
    suspended_time_at = current_datetime - timedelta(minutes=settings.RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT)

    suspended_stage_ids = set(
        RDMCollectingDataStage.objects.annotate(
            last_sub_stage_started_at=Coalesce(
                Subquery(
                    RDMCollectingDataSubStage.objects.filter(stage_id=OuterRef('pk'))
                    .values('started_at')
                    .order_by('-started_at')[:1]
                ),
                Value(datetime.combine(date.min, time.min)),
            )
        )
        .filter(
            last_sub_stage_started_at__lt=suspended_time_at,
            status__in=(
                RDMCollectingDataStageStatus.CREATED.key,
                RDMCollectingDataStageStatus.IN_PROGRESS.key,
            ),
        )
        .values_list('pk', flat=True)
    )

    if suspended_stage_ids:
        logger.info(f'find suspended CollectingDataStage: {", ".join(map(str, suspended_stage_ids))}..')

        change_stage_count = RDMCollectingDataStage.objects.filter(
            pk__in=suspended_stage_ids,
        ).update(
            status=RDMCollectingDataStageStatus.FAILED.key,
            ended_at=current_datetime,
        )

        change_sub_stage_count = RDMCollectingDataSubStage.objects.filter(
            stage_id__in=suspended_stage_ids,
        ).update(
            status=RDMCollectingDataSubStageStatus.FAILED.key,
            ended_at=current_datetime,
        )

        changed_status_result.update(
            {
                'change_stage_count': change_stage_count,
                'change_sub_stage_count': change_sub_stage_count,
            }
        )

    return changed_status_result


def get_collecting_managers_max_period_ended_dates(
    collecting_managers: Iterable['BaseCollectingExportedDataRunnerManager'],
) -> dict[str, 'datetime']:
    """Возвращает дату и время завершения последнего успешного этапа сбора для менеджеров Функций сбора."""
    managers_last_period_ended = (
        RDMCollectingDataStage.objects.filter(
            manager_id__in=[manager.uuid for manager in collecting_managers],
            id=Subquery(
                RDMCollectingDataStage.objects.filter(
                    manager_id=OuterRef('manager_id'),
                    status_id=RDMCollectingDataStageStatus.FINISHED.key,
                )
                .order_by('-id')
                .values('id')[:1]
            ),
        )
        .annotate(
            str_manager_id=Cast('manager_id', output_field=CharField()),
            last_period_ended_at=Least('logs_period_ended_at', 'started_at'),
        )
        .values_list(
            'str_manager_id',
            'last_period_ended_at',
        )
    )

    return {manager_id: last_period_ended_at for manager_id, last_period_ended_at in managers_last_period_ended}


def update_fields(entity: 'BaseRDMModel', field_values: dict[str, Any], mapping: dict[str, str]) -> None:
    """Обновление значений полей сущности по измененным полям модели.

    :param entity: Выгружаемая сущность
    :param field_values: Словарь с измененными данными модели
    :param mapping: Словарь маппинга полей модели к полям сущности
    """
    for model_field, entity_field in mapping.items():
        if model_field in field_values:
            setattr(entity, entity_field, field_values[model_field])
