from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from functools import (
    partial,
)
from typing import (
    Optional,
)

from django.conf import (
    settings,
)
from django.db.models import (
    Q,
)
from m3_ext.ui.icons import (
    Icons,
)
from objectpack.actions import (
    ObjectPack,
)
from objectpack.filters import (
    CustomFilter,
)

from educommon.objectpack.actions import (
    ExtObjectRowsAction,
)
from educommon.objectpack.filters import (
    ColumnFilterEngine,
    DateFilterByAnnotatedField,
)
from educommon.utils.object_grid import (
    add_one_row_button,
    boolean_column_renderer,
)
from educommon.utils.ui import (
    ChoicesFilter,
    append_template_globals,
)

from edu_rdm_integration.stages.upload_data.uploader_log.enums import (
    RequestResultStatus,
)
from edu_rdm_integration.stages.upload_data.uploader_log.models import (
    UploaderClientLog,
)
from edu_rdm_integration.stages.upload_data.uploader_log.ui import (
    UploaderLogInfoWindow,
)


class UploaderLogPack(ObjectPack):
    """Пак журнала Загрузчика данных в витрину."""

    title = 'Журнал логов РВД'
    model = UploaderClientLog

    edit_window = UploaderLogInfoWindow

    _is_primary_for_model = False
    can_delete = False
    list_sort_order = ['-request_datetime']
    _DEFAULT_PAGING_LIMIT = 35

    filter_engine_clz = ColumnFilterEngine
    _fd = partial(DateFilterByAnnotatedField, model)

    need_check_permission = True

    columns = [
        {
            'header': '№ п/п',
            'data_index': 'row_number',
            'sortable': False,
            'width': 3,
        },
        {
            'header': 'Метод',
            'data_index': 'http_method',
            'sortable': False,
            'width': 3,
        },
        {
            'header': 'URL',
            'data_index': 'request_url',
            'searchable': False,
            'sortable': False,
            'width': 21,
        },
        {
            'header': 'Дата и время запроса',
            'data_index': 'request_datetime',
            'sortable': True,
            'filter': _fd(
                'request_datetime',
                tooltip='C',
                default_value=date.today() - timedelta(days=1),
                editable=False,
                lookup=lambda v: Q(request_datetime__gte=datetime.combine(v, time.min)),
            )
            & _fd(
                'request_datetime',
                tooltip='По',
                default_value=date.today,
                editable=False,
                lookup=lambda v: Q(request_datetime__lte=datetime.combine(v, time.max)),
            ),
            'width': 11,
        },
        {
            'header': 'Результат',
            'data_index': 'result_status_display',
            'sortable': False,
            'filter': ChoicesFilter(
                choices=RequestResultStatus.get_choices(),
                parser=int,
                lookup='result_status',
            ),
            'width': 5,
        },
        {
            'header': 'Путь до файлов',
            'data_index': 'attachment_file',
            'sortable': False,
            'searchable': True,
            'width': 37,
        },
        {
            'header': 'ID запроса',
            'data_index': 'request_id',
            'sortable': False,
            'searchable': True,
            'width': 10,
        },
        {
            'header': 'Код статуса загрузки',
            'data_index': 'status_code',
            'sortable': True,
            'searchable': True,
            'filter': CustomFilter(
                xtype='field',
                parser=str,
                lookup=lambda v: Q(response__icontains=f'"code": {v}'),
            ),
            'width': 10,
        },
        {
            'header': 'Описание статуса загрузки',
            'data_index': 'status_description',
            'sortable': False,
            'searchable': True,
            'width': 10,
        },
        {
            'header': 'Режим эмуляции',
            'data_index': 'is_emulation',
            'sortable': False,
            'filter': ChoicesFilter(
                choices=((True, 'Да'), (False, 'Нет')),
                parser='boolean',
                lookup='is_emulation',
            ),
            'column_renderer': boolean_column_renderer(),
            'width': 5,
        },
    ]

    def __init__(self):
        """Инициализация."""
        super(UploaderLogPack, self).__init__()
        self.edit_window_action.perm_code = 'view'
        self.replace_action('rows_action', ExtObjectRowsAction())

    def get_rows_query(self, request, context):
        """Возвращает кварисет для получения списка данных."""
        context._row_number = int(getattr(context, 'start', 0))

        return super().get_rows_query(request, context)

    def get_row(self, row_id: Optional[int]) -> 'UploaderClientLog':
        """Возвращает объект по идентификатору."""
        if row_id:
            record = self.model.objects.get(id=row_id)
        else:
            record = super().get_row(row_id)

        return record

    def prepare_row(self, obj, request, context):
        """Установка дополнительных атрибутов объекта."""
        context._row_number += 1
        obj.row_number = context._row_number

        return obj

    def create_list_window(self, is_select_mode, request, context):
        """Создание окна списка."""
        win = super().create_list_window(is_select_mode, request, context)

        append_template_globals(win, 'ui-js/object-grid-buttons.js')

        return win

    def get_list_window_params(self, params, request, context):
        """Установка параметров окна списка."""
        params = super().get_list_window_params(params, request, context)

        params.update(
            maximized=True,
        )

        return params

    def configure_grid(self, grid, *args, **kwargs):
        """Конфигурирование грида окна списка."""
        super().configure_grid(grid, *args, **kwargs)

        if self.allow_paging:
            grid.allow_paging = self.allow_paging
            grid.paging_bar.page_size = self._DEFAULT_PAGING_LIMIT

        grid.url_edit = None
        add_one_row_button(
            'Просмотр',
            grid,
            self.edit_window_action,
            Icons.APPLICATION_VIEW_DETAIL,
            dbl_clicked=True,
            index=0,
        )

    def get_edit_window_params(self, params, request, context):
        """Параметры окна редактирования."""
        params = super().get_edit_window_params(params, request, context)

        params.update(
            title=f'{self.title}: Просмотр',
        )

        return params

    def extend_menu(self, menu):
        """Размещение в меню подменю "Администрирование -> Региональная витрина данных -> Журнал логов РВД".

        Args:
            menu: Объект меню.

        Returns:
            Подменю "Администрирование -> Региональная витрина данных -> Журнал логов РВД".
        """
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
