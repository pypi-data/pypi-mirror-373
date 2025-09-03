from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    TYPE_CHECKING,
)

from django.core.management import (
    BaseCommand,
    CommandParser,
)

from edu_rdm_integration.core.consts import (
    DATETIME_FORMAT,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)
from edu_rdm_integration.stages.export_data.operations import (
    BaseExportEntitiesData,
)


if TYPE_CHECKING:
    from django.core.management import (
        CommandParser,
    )


class BaseExportEntityDataCommand(BaseCommand):
    """Базовая команда для выполнения выгрузки данных сущностей РВД за указанный период."""

    def add_arguments(self, parser: 'CommandParser'):
        """Добавление параметров."""
        entities = ', '.join([f'{key} - {value.title}' for key, value in RDMEntityEnum.get_enum_data().items()])
        entities_help_text = (
            f'Значением параметра является перечисление сущностей РВД, для которых должена быть произведена выгрузка '
            f'данных. Перечисление сущностей:\n{entities}. Если сущности не указываются, то выгрузка данных '
            f'производится для всех сущностей. Сущности перечисляются через запятую без пробелов.'
        )
        parser.add_argument(
            '--entities',
            action='store',
            dest='entities',
            type=lambda e: e.split(','),
            help=entities_help_text,
        )

        parser.add_argument(
            '--period_started_at',
            action='store',
            dest='period_started_at',
            type=lambda started_at: datetime.strptime(started_at, DATETIME_FORMAT),
            default=datetime.combine(date.today(), time.min),
            help=(
                'Дата и время начала периода сбора записей моделей РВД. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 00:00:00.'
            ),
        )

        parser.add_argument(
            '--period_ended_at',
            action='store',
            dest='period_ended_at',
            type=(
                lambda ended_at: datetime.strptime(ended_at, DATETIME_FORMAT).replace(microsecond=time.max.microsecond)
            ),
            default=datetime.combine(date.today(), time.max),
            help=(
                'Дата и время конца периода сбора записей моделей РВД. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 23:59:59.'
            ),
        )
        parser.add_argument(
            '--task_id',
            action='store',
            dest='task_id',
            type=str,
            default=None,
            help='task_id для поиска асинхронной задачи',
        )
        parser.add_argument(
            '--no-update-modified',
            dest='update_modified',
            action='store_false',
            default=True,
            help='Не обновлять поле modified моделей',
        )

    def _prepare_export_entities_data_class(self, *args, **kwargs) -> BaseExportEntitiesData:
        """Возвращает объект класса экспорта данных сущностей РВД."""
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        """Выполнение действий команды."""
        export_entities_data = self._prepare_export_entities_data_class(*args, **kwargs)
        export_entities_data.export()
