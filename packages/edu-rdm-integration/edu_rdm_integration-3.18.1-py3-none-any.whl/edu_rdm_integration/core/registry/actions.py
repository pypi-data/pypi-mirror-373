from django.conf import (
    settings,
)
from m3 import (
    OperationResult,
)
from m3_ext.ui.containers import (
    ExtGridCheckBoxSelModel,
)
from objectpack.actions import (
    BaseAction,
    BaseWindowAction,
    ObjectPack,
)
from objectpack.filters import (
    ColumnFilterEngine,
)

from edu_rdm_integration.core.helpers import (
    BaseTaskStarter,
    make_download_link,
)
from edu_rdm_integration.core.registry.ui import (
    CommandProgressListWindow,
    CommandQueueSelectWindow,
)


class BaseCommandProgressPack(ObjectPack):
    """Базовый пак прогресса выполнения команд сбора/экспорта данных."""

    list_window = CommandProgressListWindow
    can_delete = False

    select_related = ['task', 'stage__status']

    filter_engine_clz = ColumnFilterEngine

    def __init__(self):
        super().__init__()

        self.queue_select_win_action = QueueLevelSelectWinAction()

        self.actions.append(self.queue_select_win_action)

    def get_list_window_params(self, params, request, context):
        """Получает параметры окна списка."""
        params = super().get_list_window_params(params, request, context)

        params['queue_select_win_url'] = self.queue_select_win_action.get_absolute_url()

        return params

    def get_edit_window_params(self, params, request, context):
        """Возвращает словарь параметров, которые будут переданы окну редактирования."""
        params = super().get_edit_window_params(params, request, context)

        if not params['create_new']:
            params['read_only'] = True
            obj = params['object']
            params['log_url'] = make_download_link(obj.logs_link)

        return params

    def configure_grid(self, grid, *args, **kwargs):
        """Конфигурирует грид."""
        super().configure_grid(grid, *args, **kwargs)

        grid.sm = ExtGridCheckBoxSelModel()
        grid.top_bar.button_new.text = 'Сгенерировать команды'
        grid.top_bar.button_edit.text = 'Просмотр'
        grid.top_bar.button_edit.icon_cls = 'icon-application-view-detail'
        grid.context_menu_row.menuitem_edit.text = 'Просмотр'
        grid.context_menu_row.menuitem_edit.icon_cls = 'icon-application-view-detail'

    def extend_menu(self, menu):
        """Расширяет главное меню."""
        if settings.RDM_MENU_ITEM:
            return menu.SubMenu(
                'Администрирование',
                menu.SubMenu(
                    'Региональная витрина данных',
                    menu.Item(
                        self.title,
                        self.list_window_action,
                    ),
                    icon='menu-dicts-16',
                ),
            )


class BaseStartTaskAction(BaseAction):
    """Базовый экшн создания асинхронных задач для выгрузки РВД."""

    url: str = None

    task_starter: BaseTaskStarter = None

    def run(self, request, context):
        """Непосредственное исполнение запроса."""
        queue_level = getattr(context, 'queue_level', None)
        result = self.task_starter().run(command_ids=context.commands, queue_level=queue_level)  # noqa pylint: disable=not-callable

        return OperationResult(
            success=True,
            message=result,
        )


class QueueLevelSelectWinAction(BaseWindowAction):
    """Экшен окна выбора очереди для запуска ручной команды сбора/выгрузки."""

    def create_window(self):
        """Создание окна."""
        self.win = CommandQueueSelectWindow()
