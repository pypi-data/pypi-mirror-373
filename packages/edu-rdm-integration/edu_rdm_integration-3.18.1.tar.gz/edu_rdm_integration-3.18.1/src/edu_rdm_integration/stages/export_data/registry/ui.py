from typing import (
    Any,
    Dict,
)

from m3_ext.ui.controls.buttons import (
    ExtButton,
)
from m3_ext.ui.fields import (
    ExtComboBox,
    ExtDisplayField,
    ExtNumberField,
    ExtStringField,
)
from m3_ext.ui.fields.simple import (
    ExtDateTimeField,
)
from m3_ext.ui.icons import (
    Icons,
)
from m3_ext.ui.misc import (
    ExtDataStore,
)

from educommon.objectpack.ui import (
    BaseEditWindow,
)
from educommon.utils.ui import (
    append_template_globals,
)

from edu_rdm_integration.core.consts import (
    BATCH_SIZE,
)
from edu_rdm_integration.core.registry.ui import (
    BaseCreateCommandWindow,
    CommandProgressListWindow,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)


class CreateExportCommandWindow(BaseCreateCommandWindow):
    """Окно создания команды экспорта данных сущности РВД."""

    def _init_components(self):
        """Инициализация компонентов."""
        super()._init_components()

        entity = ExtComboBox(
            name='entity_id',
            label='Сущность',
            display_field='entity',
            anchor='100%',
            editable=False,
            trigger_action_all=True,
            allow_blank=False,
        )
        entity.set_store(ExtDataStore((idx, key) for idx, key in enumerate(RDMEntityEnum.get_model_enum_keys())))
        period_started_at = ExtDateTimeField(
            name='period_started_at',
            label='Начало периода',
            anchor='100%',
            allow_blank=False,
            client_id='period_started_at',
        )
        period_ended_at = ExtDateTimeField(
            name='period_ended_at',
            label='Конец периода',
            anchor='100%',
            allow_blank=False,
            client_id='period_ended_at',
        )
        batch_size = ExtNumberField(
            name='batch_size',
            label='Размер чанка',
            allow_blank=False,
            allow_decimals=False,
            allow_negative=False,
            anchor='100%',
            min_value=1,
            value=BATCH_SIZE,
        )

        self.items_ = (
            entity,
            period_started_at,
            period_ended_at,
            batch_size,
        )

    def set_params(self, params: Dict[str, Any]) -> None:
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.template_globals = 'ui-js/create-export-command-win.js'


class DetailExportCommandWindow(BaseEditWindow):
    """Окно просмотра команды экспорта данных сущности РВД."""

    def set_params(self, params: Dict[str, Any]) -> None:
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.height = 'auto'
        self.logs_link_field.value = params.get('log_url', '')

    def _init_components(self) -> None:
        """Инициализирует компоненты окна."""
        super()._init_components()

        self.entity_field = ExtStringField(
            name='entity_id',
            label='Сущность',
            anchor='100%',
        )
        self.created_field = ExtDateTimeField(
            name='created',
            label='Дата создания',
            anchor='100%',
        )
        self.generation_id_field = ExtStringField(
            name='generation_id',
            label='Идентификатор генерации',
            anchor='100%',
        )
        self.task_id_field = ExtStringField(
            name='task_id',
            label='Идентификатор задачи',
            anchor='100%',
        )
        self.status_field = ExtStringField(
            name='stage.status.key',
            label='Статус экспорта',
            anchor='100%',
        )
        self.started_at_field = ExtDateTimeField(
            name='stage.started_at',
            label='Время начала экспорта',
            anchor='100%',
        )
        self.logs_link_field = ExtDisplayField(
            name='log_url',
            label='Ссылка на логи',
            anchor='100%',
        )
        self.period_started_at_field = ExtDateTimeField(
            name='period_started_at',
            label='Начало периода',
            anchor='100%',
        )
        self.period_ended_at_field = ExtDateTimeField(
            name='period_ended_at',
            label='Конец периода',
            anchor='100%',
        )

    def _do_layout(self) -> None:
        """Располагает компоненты окна."""
        super()._do_layout()

        self.form.items.extend(
            (
                self.entity_field,
                self.created_field,
                self.generation_id_field,
                self.task_id_field,
                self.status_field,
                self.started_at_field,
                self.logs_link_field,
                self.period_started_at_field,
                self.period_ended_at_field,
            )
        )


class ExportCommandProgressListWindow(CommandProgressListWindow):
    """Окно отображения реестра Экспорт данных сущностей РВД."""

    def _init_components(self):
        """Инициализирует компоненты окна."""
        super()._init_components()

        self.sub_stage_for_export_button = ExtButton(
            text='Переотправить',
            icon_cls=Icons.ARROW_REFRESH,
            handler='stageForExport',
        )

    def _do_layout(self):
        """Располагает компоненты окна."""
        super()._do_layout()

        self.grid.top_bar.items.append(self.sub_stage_for_export_button)

    def set_params(self, params):
        """Устанавливает параметры окна."""
        super().set_params(params)

        append_template_globals(self, 'ui-js/stage_for_export.js')
        self.sub_stage_for_export_url = params['sub_stage_for_export_url']
