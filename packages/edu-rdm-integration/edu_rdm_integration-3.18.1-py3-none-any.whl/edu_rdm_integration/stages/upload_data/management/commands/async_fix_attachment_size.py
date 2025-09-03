"""Команда для проставления расчетов файла . По умолчанию собирается за месяц. Обновление работает асинхронно.

Выполнение:
django-admin async_fix_attachment_size --chunk_size=50 --count_store_size --connection_pool_size=5
 --async_workers_count=10 --date_begin='01-01-2023'

Параметры:
 --date_begin: дата начала сбора данных по сгенерированным файлам в формате ДД-ММ-ГГГГ (по умолчанию месяц назад).
 --date_end: дата окончания сбора данных по сгенерированным файлам в формате ДД-ММ-ГГГГ (по умолчанию текущая дата).
 --chunk_size: количество файлов в одной итерации, по умолчанию 500
 --count_store_size: при указании этого флага, будет произведен расчет размера файла (
 запрос через оs и вычисление размера) - не рекомендуется при большом количестве данных и на дампах с прода
--connection_pool_size: количество одновременных коннектов к базе по умолчанию 10
--async_workers_count количество одновременных асинхронных воркеров-исполнителей по умолчанию 20
"""

import asyncio
from datetime import (
    date,
    datetime,
    timedelta,
)

import asyncpg
from django.conf import (
    settings,
)
from django.core.management import (
    BaseCommand,
    CommandError,
)

from educommon import (
    logger,
)
from educommon.utils.seqtools import (
    make_chunks,
)

from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataSubStageAttachment,
)
from edu_rdm_integration.stages.upload_data.enums import (
    FileUploadStatusEnum,
)


DEFAULT_QUERYSET_CHUNK_SIZE = 500
DEFAULT_FILE_SIZE = 10_485_760
DEFAULT_ASYNC_WORKERS_COUNT = 20
DEFAULT_POOL_SIZE = 10
DB_SETTINGS = settings.DATABASES['default']


class Command(BaseCommand):
    """Команда для проставления размера по умолчанию (в байтах) для отправленных файлов."""

    help = (  # noqa: A003
        'Команда для проставления размера по умолчанию (в байтах) для отправленных файлов.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.result = {
            'initial_count_rows_to_fix': 0,
            'errors': [],
            'fixed_rows_count': 0,
        }

    def add_arguments(self, parser):
        """Добавление аргументов запуска команды."""
        parser.add_argument(
            '--chunk_size',
            type=int,
            default=DEFAULT_QUERYSET_CHUNK_SIZE,
            help='Кол-во единовременно изменяемых элементов в запросе',
        )
        (
            parser.add_argument(
                '--count_store_size', action='store_true', default=False, help='Рассчитать размер файлов'
            ),
        )
        parser.add_argument(
            '--connection_pool_size', type=int, default=DEFAULT_POOL_SIZE, help='Кол-во одновременных коннектов к базе'
        )
        parser.add_argument(
            '--async_workers_count',
            type=int,
            default=DEFAULT_ASYNC_WORKERS_COUNT,
            help='Кол-во одновременных асинхронных воркеров-исполнителей',
        )
        parser.add_argument(
            '--date_begin',
            type=lambda d: datetime.strptime(d, '%d-%m-%Y').date(),
            help='Дата начала поиска сгенерированных файлов в формате %%d-%%m-%%Y.',
        )
        parser.add_argument(
            '--date_end',
            type=lambda d: datetime.strptime(d, '%d-%m-%Y').date(),
            help='Дата окончания поиска сгенерированных файлов в формате %%d-%%m-%%Y.',
        )

    def get_attachments_fix_query(
        self, chunk_size: int, date_begin: date, date_end: date, count_store_size: bool
    ) -> list[tuple[int, int]]:
        """Формирование id файлов, которым надо обновить размер."""
        logger.info('Определение файлов, которым надо обновить размер.')
        attachment_query = RDMExportingDataSubStageAttachment.objects.filter(
            exportingdatasubstageuploaderclientlog__file_upload_status=FileUploadStatusEnum.IN_PROGRESS,
            exportingdatasubstageuploaderclientlog__is_emulation=False,
            attachment_size__isnull=True,
            modified__gte=date_begin,
            modified__lte=date_end,
        )
        update_attachments = []

        for chunk in make_chunks(attachment_query.iterator(), chunk_size):
            if count_store_size:
                update_attachments.append(
                    [
                        (
                            attachment.id,
                            attachment.attachment.size
                            if attachment.attachment.field.storage.exists(attachment.attachment.name)
                            else DEFAULT_FILE_SIZE,
                        )
                        for attachment in chunk
                    ]
                )
            else:
                update_attachments.append([(attachment.id, DEFAULT_FILE_SIZE) for attachment in chunk])

        return update_attachments

    async def execute_update_sql(self, pool: asyncpg.Pool, data: list[tuple[int, int]]) -> None:
        """Метод для исполнения сгенерированного UPDATE sql запроса."""
        self.result['initial_count_rows_to_fix'] += len(data)
        logger.info('Обновление размера файлов')
        async with pool.acquire() as connection:
            try:
                await connection.executemany(
                    """
                    UPDATE rdm_exporting_data_sub_stage_attachment
                    set attachment_size = $2
                    where id = $1;
                    """,
                    data,
                )
                self.result['fixed_rows_count'] += len(data)
            except Exception as ex:
                self.result['errors'].append(str(ex))

    async def fix_attachment_size(self, fix_queries: list, pool_size: int = None, workers_count: int = None) -> None:
        """Асинхронное обновление размера файлов."""
        pool = await asyncpg.create_pool(
            max_size=pool_size,
            min_size=pool_size,
            host=DB_SETTINGS['HOST'],
            port=DB_SETTINGS['PORT'],
            user=DB_SETTINGS['USER'],
            password=DB_SETTINGS['PASSWORD'],
            database=DB_SETTINGS['NAME'],
        )
        if len(fix_queries) > workers_count:
            for chunk in make_chunks(fix_queries, workers_count):
                tasks = [self.execute_update_sql(pool, query) for query in chunk]
                await asyncio.gather(*tasks)
        else:
            tasks = [self.execute_update_sql(pool, query) for query in fix_queries]
            await asyncio.gather(*tasks)

    def update_attachment_size(
        self,
        connection_pool_size: int,
        chunk_size: int,
        date_begin: date,
        date_end: date,
        async_workers_count: int,
        count_store_size: bool,
    ):
        """Обновление размеров файла."""
        fix_queries = self.get_attachments_fix_query(chunk_size, date_begin, date_end, count_store_size)
        if fix_queries:
            event_loop = asyncio.get_event_loop()
            try:
                event_loop.run_until_complete(
                    self.fix_attachment_size(fix_queries, connection_pool_size, async_workers_count)
                )
            finally:
                event_loop.close()

    def handle(self, *args, **options):
        """Выполнение команды."""
        time_start = datetime.now()

        chunk_size = options['chunk_size']
        connection_pool_size = options['connection_pool_size']
        async_workers_count = options['async_workers_count']
        count_store_size = options['count_store_size']

        date_begin = options.get('date_begin')
        date_end = options.get('date_end') or date.today()

        if not date_begin:
            date_begin = date_end - timedelta(days=30)

        elif date_begin > date_end:
            raise CommandError('Дата начала сборки больше, чем дата окончания')

        logger.info('Обновление размеров файла\n')

        self.update_attachment_size(
            connection_pool_size, chunk_size, date_begin, date_end, async_workers_count, count_store_size
        )

        delta = datetime.now() - time_start

        logger.info(f'Время выполнения: {delta}\n')

        logger.info(
            f'Начальное кол-во записей для исправления: {self.result["initial_count_rows_to_fix"]}\n'
            f'Исправлено: {self.result["fixed_rows_count"]}\n'
        )

        errors = self.result['errors']
        for error in errors:
            logger.error(error)
