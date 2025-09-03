from typing import (
    Iterable,
)

from m3_ext.ui import (
    all_components as ext,
)
from m3_ext.ui.icons import (
    Icons,
)
from objectpack.ui import (
    BaseEditWindow,
    BaseWindow,
    ComboBoxWithStore,
)

from educommon.objectpack.ui import (
    BaseListWindow,
)
from educommon.utils.ui import (
    append_template_globals,
)

from edu_rdm_integration.pipelines.transfer.enums import (
    EntityLevelQueueTypeEnum,
)


class CommandProgressListWindow(BaseListWindow):
    """Окно списка команд на сбор/экспорт данных."""

    def set_params(self, params):
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.maximized = True
        append_template_globals(self, 'ui-js/start-task.js')
        append_template_globals(self, 'ui-js/async-task-revoke.js')

        self.start_task_url = params['start_task_url']
        self.revoke_url = params['revoke_url']
        self.queue_select_win_url = params['queue_select_win_url']

    def _init_components(self):
        """Инициализирует компоненты окна."""
        super()._init_components()

        self.start_task_button = ext.ExtButton(
            text='Запустить команду',
            icon_cls=Icons.APPLICATION_GO,
            handler='startTask',
        )
        self.revoke_task_button = ext.ExtButton(
            text='Отменить',
            icon_cls=Icons.CANCEL,
            handler='revokeTask',
        )

    def _do_layout(self):
        """Располагает компоненты окна."""
        super()._do_layout()

        self.grid.top_bar.items.insert(1, self.start_task_button)
        self.grid.top_bar.items.append(self.revoke_task_button)


class BaseCreateCommandWindow(BaseEditWindow):
    """Базовое окно создания команды на сбор/экспорт данных."""

    def _init_components(self):
        """Инициализация компонентов."""
        super()._init_components()

        # Поля, которые нужно добавить на форму:
        self.items_: Iterable = ()

    def _do_layout(self):
        """Расположение компонентов."""
        super()._do_layout()

        self.form.items.extend(self.items_)

    def set_params(self, params):
        """Параметры окна."""
        super().set_params(params)

        self.form.label_width = 150
        self.width = 400
        self.height = 'auto'


class CommandQueueSelectWindow(BaseWindow):
    """Окно выбора очереди для запуска периодических задач команд."""

    def _init_components(self):
        """Инициализация компонентов."""
        super()._init_components()

        self.queue_level_combobox = ComboBoxWithStore(
            label='Очередь выполнения команд',
            name='queue_level',
            data=EntityLevelQueueTypeEnum.get_choices(),
            value=EntityLevelQueueTypeEnum.BASE,
            allow_blank=False,
            editable=False,
            anchor='100%',
        )
        self.close_btn = self.btn_close = ext.ExtButton(
            name='close_btn',
            text='Закрыть',
            handler='function(){Ext.getCmp("%s").close();}' % self.client_id,
        )
        self.start_task_button = ext.ExtButton(
            name='start_task',
            text='Запустить команду',
            handler='function(){ win.fireEvent("closed_ok");}',
        )

    def _do_layout(self):
        """Расположение компонентов."""
        super()._do_layout()

        self.items.append(self.queue_level_combobox)
        self.buttons.extend(
            (
                self.start_task_button,
                self.btn_close,
            )
        )

    def set_params(self, params):
        """Параметры окна."""
        super().set_params(params)

        self.width = 400
        self.height = 'auto'
        self.title = 'Очередь для выполнения команды'
