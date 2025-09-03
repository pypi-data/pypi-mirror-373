from typing import (
    Any,
    Dict,
)

from m3_ext.ui.fields.simple import (
    ExtCheckBox,
    ExtComboBox,
    ExtDateTimeField,
    ExtDisplayField,
    ExtNumberField,
    ExtStringField,
)
from m3_ext.ui.misc import (
    ExtDataStore,
)

from educommon.objectpack.ui import (
    BaseEditWindow,
)
from educommon.utils.date import (
    DatesSplitter,
)

from edu_rdm_integration.core.consts import (
    BATCH_SIZE,
    CHUNK_MAX_VALUE,
    SPLIT_BY_QUANTITY_MAX_VALUE,
)
from edu_rdm_integration.core.registry.ui import (
    BaseCreateCommandWindow,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)
from edu_rdm_integration.stages.collect_data.consts import (
    ALL_UNITS_IN_COMMAND,
)


class CreateCollectCommandWindow(BaseCreateCommandWindow):
    """Окно создания команды сбора данных модели РВД."""

    def _init_components(self):
        """Инициализация компонентов."""
        super()._init_components()

        model = ExtComboBox(
            name='model_id',
            label='Модель',
            display_field='model',
            anchor='100%',
            editable=False,
            trigger_action_all=True,
            allow_blank=False,
        )
        model.set_store(ExtDataStore((idx, key) for idx, key in enumerate(RDMModelEnum.get_model_enum_keys())))
        logs_period_started_at = ExtDateTimeField(
            name='logs_period_started_at',
            label='Начало периода',
            anchor='100%',
            allow_blank=False,
            client_id='logs_period_started_at',
        )
        logs_period_ended_at = ExtDateTimeField(
            name='logs_period_ended_at',
            label='Конец периода',
            anchor='100%',
            allow_blank=False,
            client_id='logs_period_ended_at',
        )
        split_by = ExtComboBox(
            name='split_by',
            display_field='split_by',
            label='Единица подпериода',
            anchor='100%',
            editable=False,
            trigger_action_all=True,
            client_id='split_by',
        )
        split_by.set_store(ExtDataStore(enumerate(DatesSplitter.get_split_by_modes())))
        split_by_quantity = ExtNumberField(
            name='split_by_quantity',
            label='Размер подпериода',
            allow_blank=False,
            allow_decimals=False,
            allow_negative=False,
            max_value=SPLIT_BY_QUANTITY_MAX_VALUE,
            anchor='100%',
            value=1,
        )
        split_mode = ExtComboBox(
            name='split_mode',
            display_field='split_mode',
            label='Режим разбиения на подпериоды',
            anchor='100%',
            editable=False,
            allow_blank=True,
            trigger_action_all=True,
            value=DatesSplitter.WW_MODE,
        )
        split_mode.set_store(
            ExtDataStore(enumerate(DatesSplitter.get_modes())),
        )
        batch_size = ExtNumberField(
            name='batch_size',
            label='Размер чанка',
            allow_blank=False,
            allow_decimals=False,
            allow_negative=False,
            anchor='100%',
            value=BATCH_SIZE,
            max_value=CHUNK_MAX_VALUE,
            client_id='batch_size',
        )
        by_institutes = ExtCheckBox(
            anchor='100%',
            label='Разбить по организациям',
            name='by_institutes',
        )
        institute_ids = ExtStringField(
            label='ID организаций (через запятую, например: 1,2,3 или оставить пустым для всех)',
            name='institute_ids',
            allow_blank=True,
            anchor='100%',
            max_length=100,
            client_id='institute_ids',
        )
        institute_count = ExtNumberField(
            name='institute_count',
            label='Кол-во организаций в одной команде',
            allow_decimals=False,
            anchor='100%',
            min_value=ALL_UNITS_IN_COMMAND,
            value=ALL_UNITS_IN_COMMAND,
            client_id='institute_count',
            allow_blank=False,
        )
        hint_text = ExtDisplayField(
            value=(
                f'Данные можно разбить или по "{batch_size.label}" или по "{split_by.label}"! '
                f'Если выбрать оба варианта, то будет выбрано разбиение по "{split_by.label}".'
            ),
            read_only=True,
            label_style='width: 0px',
            style={'text-align': 'center'},
        )
        just_or_hint_text = ExtDisplayField(
            label='или',
        )
        self.items_ = (
            model,
            logs_period_started_at,
            logs_period_ended_at,
            by_institutes,
            institute_ids,
            institute_count,
            hint_text,
            batch_size,
            just_or_hint_text,
            split_by,
            split_by_quantity,
            split_mode,
        )

    def set_params(self, params: Dict[str, Any]) -> None:
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.template_globals = 'ui-js/collect-command-window.js'


class DetailCollectCommandWindow(BaseEditWindow):
    """Окно просмотра команды сбора данных модели РВД."""

    def set_params(self, params: Dict[str, Any]) -> None:
        """Устанавливает параметры окна."""
        super().set_params(params)

        self.height = 'auto'
        self.logs_link_field.value = params.get('log_url', '')

    def _init_components(self) -> None:
        """Инициализирует компоненты окна."""
        super()._init_components()

        self.model_field = ExtStringField(
            name='model_id',
            label='Модель',
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
        self.institute_ids_field = ExtStringField(
            name='institute_ids',
            label='Идентификаторы организаций',
            anchor='100%',
        )
        self.status_field = ExtStringField(
            name='stage.status.key',
            label='Статус сбора',
            anchor='100%',
        )
        self.started_at_field = ExtDateTimeField(
            name='stage.started_at',
            label='Время начала сбора',
            anchor='100%',
        )
        self.logs_link_field = ExtDisplayField(
            name='log_url',
            label='Ссылка на логи',
            anchor='100%',
        )
        self.logs_period_started_at_field = ExtDateTimeField(
            name='logs_period_started_at',
            label='Начало периода',
            anchor='100%',
        )
        self.logs_period_ended_at_field = ExtDateTimeField(
            name='logs_period_ended_at',
            label='Конец периода',
            anchor='100%',
        )

    def _do_layout(self) -> None:
        """Располагает компоненты окна."""
        super()._do_layout()

        self.form.items.extend(
            (
                self.model_field,
                self.created_field,
                self.generation_id_field,
                self.task_id_field,
                self.institute_ids_field,
                self.status_field,
                self.started_at_field,
                self.logs_link_field,
                self.logs_period_started_at_field,
                self.logs_period_ended_at_field,
            )
        )
