"""Команда для проверки состояния отправленных в витрину данных.

Необязательные параметры:
--period_started_at - дата и время начала периода загрузки данных в витрину
--period_ended_at - дата и время конца периода загрузки данных в витрину
--thread_count - количество потоков для обработки

Пример использования:
python manage.py check_upload_status --period_started_at="01.11.2023 10:00:00" --thread_count=4
"""

from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from django.core.cache import (
    cache,
)
from django.core.management.base import (
    BaseCommand,
)

from edu_rdm_integration.core.consts import (
    DATETIME_FORMAT,
)
from edu_rdm_integration.stages.upload_data.enums import (
    FileUploadStatusEnum,
)
from edu_rdm_integration.stages.upload_data.helpers import (
    UploadStatusHelper,
)
from edu_rdm_integration.stages.upload_data.models import (
    RDMExportingDataSubStageUploaderClientLog,
)


if TYPE_CHECKING:
    from django.core.management.base import (
        CommandParser,
    )


class Command(BaseCommand):
    """Команда для проверки состояния отправленных в витрину данных."""

    help = 'Команда для проверки состояния отправленных в витрину данных'  # noqa: A003

    def add_arguments(self, parser: 'CommandParser') -> None:
        """Добавляет аргументы парсера."""
        parser.add_argument(
            '--period_started_at',
            action='store',
            dest='period_started_at',
            type=lambda started_at: datetime.strptime(started_at, DATETIME_FORMAT),
            default=datetime.combine(date.today(), time.min),
            help=(
                'Дата и время начала периода загрузки данных в витрину. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 00:00:00.'
            ),
        )

        parser.add_argument(
            '--period_ended_at',
            action='store',
            dest='period_ended_at',
            type=lambda ended_at: datetime.strptime(ended_at, DATETIME_FORMAT),
            default=datetime.combine(date.today(), time.max),
            help=(
                'Дата и время конца периода загрузки данных в витрину. Значение предоставляется в формате '
                '"дд.мм.гггг чч:мм:сс". По умолчанию, сегодняшний день, время 23:59:59.'
            ),
        )

        parser.add_argument(
            '--thread_count',
            default=1,
            type=int,
            help='Количество потоков для обработки. По умолчанию, 1.',
        )

    def handle(self, *args: tuple[Any], **kwargs: dict[str, Any]) -> None:
        """Обработчик команды."""
        thread_count = kwargs['thread_count']
        if thread_count < 1:
            raise ValueError(f'Количество потоков {thread_count} должно быть больше 0.')

        in_progress_attachment_uploads = RDMExportingDataSubStageUploaderClientLog.objects.filter(
            created__gte=kwargs['period_started_at'],
            created__lte=kwargs['period_ended_at'],
            is_emulation=False,
            file_upload_status=FileUploadStatusEnum.IN_PROGRESS,
        )

        UploadStatusHelper(in_progress_attachment_uploads, cache).run(thread_count=thread_count)
