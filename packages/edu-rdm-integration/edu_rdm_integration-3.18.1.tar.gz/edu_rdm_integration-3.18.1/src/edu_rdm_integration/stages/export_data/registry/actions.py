from functools import (
    partial,
)

from django.db.models import (
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
)
from django.db.transaction import (
    atomic,
)
from m3.actions.results import (
    OperationResult,
)
from objectpack.actions import (
    BaseAction,
)

from educommon.async_task.actions import (
    RevokeAsyncTaskAction,
)
from educommon.async_task.models import (
    AsyncTaskStatus,
)
from educommon.utils.ui import (
    ChoicesFilter,
    DatetimeFilterCreator,
)

from edu_rdm_integration.core.enums import (
    CommandType,
)
from edu_rdm_integration.core.helpers import (
    make_download_link,
)
from edu_rdm_integration.core.registry.actions import (
    BaseCommandProgressPack,
    BaseStartTaskAction,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)
from edu_rdm_integration.stages.export_data.generators import (
    BaseFirstExportEntitiesDataCommandsGenerator,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataCommandProgress,
    RDMExportingDataStageStatus,
    RDMExportingDataSubStage,
    RDMExportingDataSubStageStatus,
)
from edu_rdm_integration.stages.export_data.registry.ui import (
    CreateExportCommandWindow,
    DetailExportCommandWindow,
    ExportCommandProgressListWindow,
)


class BaseExportingDataProgressPack(BaseCommandProgressPack):
    """Базовый пак команд экспорта данных сущностей РВД."""

    model = RDMExportingDataCommandProgress
    title = 'Экспорт данных сущностей РВД'

    add_window = CreateExportCommandWindow
    edit_window = DetailExportCommandWindow
    list_window = ExportCommandProgressListWindow

    need_check_permission = True

    select_related = ['task', 'task__status']

    list_sort_order = ('-created', 'entity__order_number', 'generation_id')
    date_filter = partial(DatetimeFilterCreator, model)

    columns = [
        {
            'data_index': 'entity.pk',
            'header': 'Сущность',
            'sortable': True,
            'filter': ChoicesFilter(
                choices=[(key, key) for key in RDMEntityEnum.get_model_enum_keys()],
                parser=str,
                lookup=lambda key: Q(entity=key) if key else Q(),
            ),
        },
        {
            'data_index': 'task.status.title',
            'header': 'Статус асинхронной задачи',
            'sortable': True,
            'filter': ChoicesFilter(
                choices=[(value.key, value.title) for value in AsyncTaskStatus.get_model_enum_values()],
                parser=str,
                lookup='task__status_id',
            ),
        },
        {
            'data_index': 'type',
            'header': 'Тип команды',
            'filter': ChoicesFilter(
                choices=CommandType.get_choices(),
                parser=int,
                lookup='type',
            ),
            'width': 60,
        },
        {
            'data_index': 'finished_sub_stages',
            'header': 'Подэтапов <br> выполнено',
            'width': 50,
        },
        {
            'data_index': 'ready_sub_stages',
            'header': 'Подэтапов <br> подготовлено <br> к выгрузке',
            'width': 50,
        },
        {
            'data_index': 'process_errors_sub_stages',
            'header': 'Подэтапов <br> с ошибкой <br> обработки <br> запроса',
            'width': 50,
        },
        {
            'data_index': 'stage.status.key',
            'header': 'Статус экспорта',
            'sortable': True,
            'filter': ChoicesFilter(
                choices=[(key, key) for key in RDMExportingDataStageStatus.get_model_enum_keys()],
                parser=str,
                lookup=lambda key: Q(stage__status=key) if key else Q(),
            ),
            'width': 50,
        },
        {
            'data_index': 'stage.started_at',
            'header': 'Время начала экспорта',
            'sortable': True,
            'filter': date_filter('stage__started_at').filter,
        },
        {
            'data_index': 'log_url',
            'header': 'Ссылка на логи',
            'width': 60,
        },
        {
            'data_index': 'period_started_at',
            'header': 'Начало периода',
            'sortable': True,
            'filter': date_filter('period_started_at').filter,
        },
        {
            'data_index': 'period_ended_at',
            'header': 'Конец периода',
            'sortable': True,
            'filter': date_filter('period_ended_at').filter,
        },
        {
            'data_index': 'generation_id',
            'header': 'ID генерации',
            'sortable': True,
        },
        {
            'data_index': 'created',
            'header': 'Дата создания',
            'sortable': True,
        },
    ]

    _start_task_action_cls: BaseStartTaskAction
    _revoke_task_action_cls: RevokeAsyncTaskAction

    def __init__(self):
        super().__init__()

        self.start_task_action = self._start_task_action_cls()
        self.revoke_task_action = self._revoke_task_action_cls()
        self.prepare_sub_stage_for_export_action = PrepareSubStageForExportAction()

        self.actions.extend((self.start_task_action, self.revoke_task_action, self.prepare_sub_stage_for_export_action))

    def get_list_window_params(self, params, request, context):
        """Получает параметры окна списка."""
        params = super().get_list_window_params(params, request, context)

        params['revoke_url'] = self.revoke_task_action.get_absolute_url()
        params['start_task_url'] = self.start_task_action.get_absolute_url()
        params['sub_stage_for_export_url'] = self.prepare_sub_stage_for_export_action.get_absolute_url()

        return params

    def declare_context(self, action):
        """Декларирует контекст экшна."""
        context = super().declare_context(action)

        if action is self.save_action:
            context['period_started_at'] = {'type': 'datetime'}
            context['period_ended_at'] = {'type': 'datetime'}
            context['batch_size'] = {'type': 'int'}
        elif action in (self.start_task_action, self.prepare_sub_stage_for_export_action):
            context['commands'] = {'type': 'int_list'}
            context['queue_level'] = {'type': int, 'default': None}
        elif action is self.revoke_task_action:
            context['async_task_ids'] = {'type': 'str', 'default': ''}

        return context

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных."""
        query = super().get_rows_query(request, context)

        return query.annotate(
            finished_sub_stages=Subquery(
                RDMExportingDataSubStage.objects.filter(
                    stage_id=OuterRef('stage_id'),
                    status=RDMExportingDataSubStageStatus.FINISHED.key,
                )
                .annotate(
                    finished_count=Func(F('id'), function='Count'),
                )
                .values('finished_count'),
            ),
            ready_sub_stages=Subquery(
                RDMExportingDataSubStage.objects.filter(
                    stage_id=OuterRef('stage_id'),
                    status=RDMExportingDataSubStageStatus.READY_FOR_EXPORT.key,
                )
                .annotate(
                    ready_count=Func(F('id'), function='Count', output_field=IntegerField()),
                )
                .values('ready_count'),
            ),
            process_errors_sub_stages=Subquery(
                RDMExportingDataSubStage.objects.filter(
                    stage_id=OuterRef('stage_id'),
                    status=RDMExportingDataSubStageStatus.PROCESS_ERROR.key,
                )
                .annotate(process_errors_count=Func(F('id'), function='Count', output_field=IntegerField()))
                .values('process_errors_count'),
            ),
        )

    def prepare_row(self, obj, request, context):
        """Подготовка данных для отображения в реестре."""
        obj.log_url = make_download_link(obj.logs_link)

        return obj

    @atomic
    def save_row(self, obj, create_new, request, context, *args, **kwargs):
        """Сохраняет объекты."""
        commands = BaseFirstExportEntitiesDataCommandsGenerator(
            entities=[obj.entity_id],
            period_started_at=context.period_started_at,
            period_ended_at=context.period_ended_at,
            batch_size=context.batch_size,
        ).generate()

        for command in commands:
            obj = self.model(
                entity_id=obj.entity_id,
                period_started_at=command['period_started_at'],
                period_ended_at=command['period_ended_at'],
                generation_id=command['generation_id'],
                type=CommandType.MANUAL,
            )
            super().save_row(obj, create_new, request, context, *args, **kwargs)


class PrepareSubStageForExportAction(BaseAction):
    """Смена статусов у подэтапов для переотправки."""

    def run(self, request, context):
        """Обновление статусов подэтапов не принятых витриной."""
        command_ids = context.commands
        stage_ids = RDMExportingDataCommandProgress.objects.filter(id__in=command_ids).values_list(
            'stage_id', flat=True
        )

        updated_count = RDMExportingDataSubStage.objects.filter(
            stage_id__in=stage_ids,
            status=RDMExportingDataSubStageStatus.PROCESS_ERROR.key,
        ).update(status=RDMExportingDataSubStageStatus.READY_FOR_EXPORT.key)
        if updated_count:
            message = f'Будет переотправлено {updated_count} подэтапов.'
        else:
            message = 'Подэтапов для переотправления не найдено.'

        return OperationResult(success=True, message=message)
