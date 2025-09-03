from edu_rdm_integration.stages.export_data.functions.base.requests import (
    RegionalDataMartStatusRequest,
)
from edu_rdm_integration.stages.upload_data.management.base import (
    BaseDatamartClientCommand,
)


# ruff: noqa: D101
class Command(BaseDatamartClientCommand):
    help = 'Команда для получения статуса загрузки файла в РВД с использованием uploader-client.'  # noqa A003

    def add_arguments(self, parser):
        """Добавление параметров."""
        super().add_arguments(parser)

        parser.add_argument(
            '--request_id',
            type=str,
            required=True,
            help='requestID полученный в результате выполнения команды на загрузку или удаление данных',
        )

    def _get_request(self, **options):
        """Возвращает запрос для отправки в РВД."""
        request = RegionalDataMartStatusRequest(
            request_id=options['request_id'],
            method='GET',
            parameters={},
            headers={
                'Content-Type': 'application/json',
            },
        )

        return request
