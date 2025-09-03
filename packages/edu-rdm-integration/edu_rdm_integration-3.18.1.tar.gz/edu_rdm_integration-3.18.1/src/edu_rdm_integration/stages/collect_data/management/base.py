from datetime import (
    date,
    datetime,
    time,
)

from django.core.management import (
    BaseCommand,
    CommandParser,
)

from edu_rdm_integration.core.consts import (
    DATETIME_FORMAT,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)
from edu_rdm_integration.stages.collect_data.operations import (
    BaseCollectModelsData,
)


class BaseCollectModelDataCommand(BaseCommand):
    """Базовая команда для выполнения сбора данных моделей РВД."""

    def add_arguments(self, parser: 'CommandParser'):
        """Добавление параметров."""
        models = ', '.join([f'{key} - {value.title}' for key, value in RDMModelEnum.get_enum_data().items()])
        models_help_text = (
            f'Значением параметра является перечисление моделей РВД, для которых должен быть произведен сбор данных. '
            f'Перечисление моделей:\n{models}. Если модели не указываются, то сбор данных производится для всех '
            f'моделей. Модели перечисляются через запятую без пробелов.'
        )
        parser.add_argument(
            '--models',
            action='store',
            dest='models',
            type=lambda e: e.split(','),
            help=models_help_text,
        )

        parser.add_argument(
            '--logs_period_started_at',
            action='store',
            dest='logs_period_started_at',
            type=lambda started_at: datetime.strptime(started_at, DATETIME_FORMAT),
            default=datetime.combine(date.today(), time.min),
            help=(
                'Дата и время начала периода обрабатываемых логов. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 00:00:00.'
            ),
        )

        parser.add_argument(
            '--logs_period_ended_at',
            action='store',
            dest='logs_period_ended_at',
            type=lambda ended_at: datetime.strptime(ended_at, DATETIME_FORMAT),
            default=datetime.combine(date.today(), time.max),
            help=(
                'Дата и время конца периода обрабатываемых логов. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 23:59:59.'
            ),
        )

    def _prepare_collect_models_data_class(self, *args, **kwargs) -> BaseCollectModelsData:
        """Возвращает объект класса сбора данных моделей РВД."""
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        """Выполнение действий команды."""
        collect_models_data = self._prepare_collect_models_data_class(*args, **kwargs)
        collect_models_data.collect()


class BaseCollectModelsDataByGeneratingLogsCommand(BaseCollectModelDataCommand):
    """Команда сбора данных моделей РВД на основе существующих в БД данных моделей ЭШ.

    Можно регулировать, для каких моделей должен быть произведен сбор данных, и период, за который должны
    быть собраны логи. Логи формируются в процессе выполнения команды при помощи генератора логов LogGenerator для
    указанной модели.
    """

    # flake8: noqa: A003
    help = 'Команда сбора данных моделей РВД на основе существующих в БД данных моделей продукта'

    def add_arguments(self, parser: 'CommandParser'):
        """Добавление параметров."""
        super().add_arguments(parser=parser)

        parser.add_argument(
            '--institute_ids',
            action='store',
            dest='institute_ids',
            type=lambda v: tuple(map(int, v.split(','))),
            default=(),
            help='Идентификаторы учебных заведений, для которых производится выгрузка.',
        )
