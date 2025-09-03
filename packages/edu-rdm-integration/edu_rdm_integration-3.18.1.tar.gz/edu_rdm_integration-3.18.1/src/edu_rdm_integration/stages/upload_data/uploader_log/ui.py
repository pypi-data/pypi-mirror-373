from m3_ext.ui.fields import (
    ExtTextArea,
)
from objectpack.ui import (
    BaseEditWindow,
)

from educommon.utils.ui import (
    switch_window_in_read_only_mode,
)


class UploaderLogInfoWindow(BaseEditWindow):
    """Окно просмотра лога Загрузчика данных в витрину."""

    def _init_components(self):
        """Инициализация компонентов окна."""
        super(UploaderLogInfoWindow, self)._init_components()
        self.field__request = ExtTextArea(
            label='Запрос',
            name='request',
            anchor='100%',
            height=160,
        )
        self.field__response = ExtTextArea(
            label='Ответ',
            name='response',
            anchor='100%',
            height=160,
        )
        self.field__error = ExtTextArea(
            label='Ошибка',
            name='request_error',
            anchor='100%',
            height=80,
        )
        self.field__attachment = ExtTextArea(
            label='Вложения',
            name='attachment_file',
            anchor='100%',
            height=40,
        )

    def _do_layout(self):
        """Размещение компонентов окна на форме."""
        super(UploaderLogInfoWindow, self)._do_layout()

        self.form.items.extend(
            (
                self.field__request,
                self.field__response,
                self.field__error,
                self.field__attachment,
            )
        )

    def set_params(self, params):
        """Настройка окна."""
        super(UploaderLogInfoWindow, self).set_params(params)

        self.height = 'auto'
        self.width = 700

        switch_window_in_read_only_mode(self)
        self.make_read_only()
