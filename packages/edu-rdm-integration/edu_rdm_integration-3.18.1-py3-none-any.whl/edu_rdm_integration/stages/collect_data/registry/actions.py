from functools import (
    partial,
)

from django.conf import (
    settings,
)
from django.db.models import (
    F,
    Func,
    OuterRef,
    Q,
    Subquery,
)
from django.db.transaction import (
    atomic,
)
from m3.actions.exceptions import (
    ApplicationLogicException,
)

from educommon.async_task.actions import (
    RevokeAsyncTaskAction,
)
from educommon.async_task.models import (
    AsyncTaskStatus,
)
from educommon.utils.conversion import (
    int_or_none,
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
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)
from edu_rdm_integration.stages.collect_data.generators import (
    FirstCollectModelsDataCommandsGenerator,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataCommandProgress,
    RDMCollectingDataStageStatus,
    RDMCollectingDataSubStage,
    RDMCollectingDataSubStageStatus,
)
from edu_rdm_integration.stages.collect_data.registry.ui import (
    CreateCollectCommandWindow,
    DetailCollectCommandWindow,
)


class BaseCollectingDataProgressPack(BaseCommandProgressPack):
    """Базовый пак команд сбора данных моделей РВД."""

    title = 'Сбор данных моделей РВД'
    model = RDMCollectingDataCommandProgress

    add_window = CreateCollectCommandWindow
    edit_window = DetailCollectCommandWindow

    need_check_permission = True

    select_related = ['task', 'task__status']

    list_sort_order = ('-created', 'model__order_number', 'generation_id')
    date_filter = partial(DatetimeFilterCreator, model)

    columns = [
        {
            'data_index': 'model.pk',
            'header': 'Модель',
            'sortable': True,
            'filter': ChoicesFilter(
                choices=[(key, key) for key in RDMModelEnum.get_model_enum_keys()],
                parser=str,
                lookup=lambda key: Q(model=key) if key else Q(),
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
            'data_index': 'ready_to_export_sub_stages',
            'header': 'Подэтапов выполнено',
            'width': 50,
        },
        {
            'data_index': 'stage.status.key',
            'header': 'Статус сбора',
            'sortable': True,
            'filter': ChoicesFilter(
                choices=[(key, key) for key in RDMCollectingDataStageStatus.get_model_enum_keys()],
                parser=str,
                lookup=lambda key: Q(stage__status=key) if key else Q(),
            ),
            'width': 50,
        },
        {
            'data_index': 'stage.started_at',
            'header': 'Время начала сбора',
            'sortable': True,
            'filter': date_filter('stage__started_at').filter,
        },
        {
            'data_index': 'log_url',
            'header': 'Ссылка на логи',
            'width': 60,
        },
        {
            'data_index': 'logs_period_started_at',
            'header': 'Начало периода',
            'sortable': True,
            'filter': date_filter('logs_period_started_at').filter,
        },
        {
            'data_index': 'logs_period_ended_at',
            'header': 'Конец периода',
            'sortable': True,
            'filter': date_filter('logs_period_ended_at').filter,
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

        self.actions.extend(
            (
                self.start_task_action,
                self.revoke_task_action,
            )
        )

    def get_list_window_params(self, params, request, context):
        """Получает параметры окна списка."""
        params = super().get_list_window_params(params, request, context)

        params['start_task_url'] = self.start_task_action.get_absolute_url()
        params['revoke_url'] = self.revoke_task_action.get_absolute_url()

        return params

    def declare_context(self, action):
        """Объявление контекста."""
        context = super().declare_context(action)

        if action is self.save_action:
            context['logs_period_started_at'] = context['logs_period_ended_at'] = {'type': 'datetime'}
            context['split_by_quantity'] = context['batch_size'] = {'type': 'int_or_none', 'default': None}
            context['institute_count'] = {'type': 'int'}
            context['split_by'] = context['split_mode'] = {'type': 'str', 'default': None}
            context['by_institutes'] = {'type': 'boolean', 'default': False}
            context['institute_ids'] = {'type': 'int_list'}
        elif action is self.start_task_action:
            context['commands'] = {'type': 'int_list'}
            context['queue_level'] = {'type': int, 'default': None}
        elif action is self.revoke_task_action:
            context['async_task_ids'] = {'type': 'str', 'default': ''}

        return context

    def get_rows_query(self, request, context):
        """Возвращает выборку из БД для получения списка данных."""
        query = super().get_rows_query(request, context)

        # Необходимо также рассчитать прогресс сбора:
        query = query.annotate(
            ready_to_export_sub_stages=Subquery(
                RDMCollectingDataSubStage.objects.filter(
                    stage_id=OuterRef('stage_id'),
                    status_id=RDMCollectingDataSubStageStatus.READY_TO_EXPORT.key,
                )
                .annotate(ready_to_export_sub_stages=Func(F('id'), function='Count'))
                .values('ready_to_export_sub_stages')
            )
        )

        return query

    def prepare_row(self, obj, request, context):
        """Подготовка данных для отображения в реестре."""
        obj.log_url = make_download_link(obj.logs_link)

        return obj

    def _get_actual_institute_ids(self):
        """Возвращает кортеж из идентификаторов организаций, данные по которым можно собрать."""
        raise NotImplementedError

    @atomic
    def save_row(self, obj, create_new, request, context, *args, **kwargs):
        """Сохраняет объект.

        Переопределено, т.к. на основе полученных параметров от клиента,
        необходимо сформировать команды на сбор и их сохранить в модели.
        """
        batch_size = int_or_none(context.batch_size)
        if not context.split_by and not batch_size:
            raise ApplicationLogicException('Поле "Размер чанка" обязательно к заполнению')

        split_by_quantity = int_or_none(context.split_by_quantity)
        if context.split_by and not split_by_quantity:
            raise ApplicationLogicException('Поле "Размер подпериода" обязательно к заполнению')

        commands_to_save = FirstCollectModelsDataCommandsGenerator(
            models=[obj.model_id],
            split_by=context.split_by,
            split_mode=context.split_mode,
            split_by_quantity=context.split_by_quantity,
            logs_period_started_at=context.logs_period_started_at,
            logs_period_ended_at=context.logs_period_ended_at,
            batch_size=context.batch_size,
        ).generate_with_split(
            by_institutes=context.by_institutes,
            institute_ids=context.institute_ids,
            institute_count=context.institute_count,
            actual_institute_ids=self._get_actual_institute_ids(),
        )

        if not commands_to_save:
            raise ApplicationLogicException(
                f'Недостаточно данных для обработки модели "{obj.model_id}" '
                f'в указанный период с {context.logs_period_started_at} по {context.logs_period_ended_at}. '
                f'Проверьте наличие данных в указанном временном диапазоне.'
            )

        objs = [
            self.model(
                model_id=obj.model_id,
                logs_period_started_at=command['period_started_at'],
                logs_period_ended_at=command['period_ended_at'],
                generation_id=command['generation_id'],
                institute_ids=command['institute_ids'],
                type=CommandType.MANUAL,
            )
            for command in commands_to_save
        ]
        self.model.objects.bulk_create(objs, batch_size=settings.COLLECT_PROGRESS_BATCH_SIZE)
