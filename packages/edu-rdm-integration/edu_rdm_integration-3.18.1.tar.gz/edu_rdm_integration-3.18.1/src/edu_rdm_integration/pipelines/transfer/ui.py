from m3_ext.ui.all_components import (
    ExtButton,
    ExtDisplayField,
)
from objectpack.ui import (
    BaseEditWindow,
    BaseListWindow,
    anchor100,
    model_fields_to_controls,
)

from educommon.utils.ui import (
    append_template_globals,
)

from edu_rdm_integration.pipelines.transfer.models import (
    TransferredEntity,
)


class TransferredEntityListWindow(BaseListWindow):
    """Окно реестра сущностей для сбора и экспорта данных."""

    def _init_components(self):
        """Инициализация компонентов окна."""
        super()._init_components()

        self.export_off_button = ExtButton(text='Отключить экспорт', handler='offExport')
        self.export_on_button = ExtButton(text='Включить экспорт', handler='onExport')

    def _do_layout(self):
        """Размещение компонентов окна на форме."""
        super()._do_layout()

        self.grid.top_bar.items.extend((self.export_off_button, self.export_on_button))

    def set_params(self, params, *args, **kwargs):
        """Настройка окна."""
        super().set_params(params, *args, **kwargs)

        append_template_globals(self, 'ui-js/transferred-entity-list.js')
        self.export_change_action_url = params['pack'].export_change_action.get_absolute_url()
        self.pack = params['pack']


class TransferredEntityEditWindow(BaseEditWindow):
    """Окно редактирования сущностей."""

    def _init_components(self):
        """Инициализация компонентов."""
        super()._init_components()

        self._controls = model_fields_to_controls(
            TransferredEntity,
            self,
            field_list=[
                'queue_level',
            ],
        )
        self.entity_name_field = ExtDisplayField(
            read_only=True,
            label='Сущность',
            name='entity_name',
        )
        self._controls.insert(0, self.entity_name_field)

    def _do_layout(self):
        """Расположение компонентов."""
        super()._do_layout()

        self.form.items.extend(list(map(anchor100, self._controls)))

    def set_params(self, params, *args, **kwargs):
        """Простановка парметров."""
        super().set_params(params, *args, **kwargs)

        obj = params.get('object')
        if obj:
            self.entity_name_field.value = obj.entity_id
