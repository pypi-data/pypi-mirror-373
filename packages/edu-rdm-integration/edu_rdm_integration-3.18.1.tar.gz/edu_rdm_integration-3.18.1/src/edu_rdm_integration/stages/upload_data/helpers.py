from concurrent.futures import (
    ThreadPoolExecutor,
)
from json import (
    JSONDecodeError,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

from django.conf import (
    settings,
)
from django.db import (
    transaction,
)
from django.db.models import (
    QuerySet,
)
from uploader_client.adapters import (
    adapter,
)

from educommon import (
    logger,
)

from edu_rdm_integration.core.redis_cache import (
    AbstractCache,
)
from edu_rdm_integration.stages.export_data.consts import (
    TOTAL_ATTACHMENTS_SIZE_KEY,
)
from edu_rdm_integration.stages.export_data.functions.base.requests import (
    RegionalDataMartStatusRequest,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataSubStageStatus,
)
from edu_rdm_integration.stages.upload_data.consts import (
    FAILED_STATUSES,
)
from edu_rdm_integration.stages.upload_data.enums import (
    FileUploadStatusEnum,
)
from edu_rdm_integration.stages.upload_data.models import (
    RDMExportingDataSubStageUploaderClientLog,
    RDMRequestStatus,
    RDMUploadStatusRequestLog,
)


if TYPE_CHECKING:
    from uploader_client.logging.base import (
        Entry,
    )


class UploadStatusHelper:
    """Хелпер проверки статуса загрузки данных в витрину."""

    def __init__(self, in_progress_uploads: QuerySet, cache: AbstractCache) -> None:
        self._in_progress_uploads = in_progress_uploads
        self.cache = cache

    def run(self, thread_count: int = 1) -> None:
        """Запускает проверки статусов."""
        if thread_count > 1:
            with ThreadPoolExecutor(max_workers=thread_count) as pool:
                pool.map(self._process_upload, self._in_progress_uploads)
        else:
            for upload in self._in_progress_uploads:
                self._process_upload(upload)

    @classmethod
    def send_upload_status_request(cls, request_id: str) -> tuple[Optional[dict[str, Any]], 'Entry']:
        """Формирует и отправляет запрос для получения статуса загрузки данных в витрину."""
        request = RegionalDataMartStatusRequest(
            request_id=request_id,
            method='GET',
            parameters={},
            headers={
                'Content-Type': 'application/json',
            },
        )

        result = adapter.send(request)

        response = None

        if result.error:
            logger.warning(
                f'Ошибка при получении статуса загрузки данных в витрину. Идентификатор загрузки: {request_id}. '
                f'Ошибка: {result.error}, запрос: {result.log.request}, ответ: {result.log.response}',
            )
        else:
            logger.info(
                f'Получен ответ со статусом {result.response.status_code} и содержимым {result.response.text}. '
                f'Идентификатор загрузки: {request_id}',
            )
            try:
                response = result.response.json()
            except JSONDecodeError:
                logger.error(
                    f'Не удалось получить данные из ответа запроса статуса загрузки данных в витрину. '
                    f'Идентификатор загрузки: {request_id}, ответ: {result.response.text}',
                )

        return response, result.log

    @classmethod
    def update_upload_status(
        cls,
        upload: RDMExportingDataSubStageUploaderClientLog,
        response: Optional[dict[str, Any]],
        log_entry: 'Entry',
    ) -> None:
        """Обновляет статус загрузки данных в витрину."""
        request_status = None

        if isinstance(response, dict):
            request_status = RDMRequestStatus.get_values_to_enum_data().get(response.get('code'))

            if not request_status:
                logger.error(
                    'Не удалось определить статус загрузки данных в витрину. Идентификатор загрузки: '
                    f'{upload.request_id}, данные ответа: {response}',
                )

        with transaction.atomic():
            RDMUploadStatusRequestLog.objects.create(
                upload=upload,
                entry=log_entry,
                request_status_id=getattr(request_status, 'key', None),
            )

            if request_status in FAILED_STATUSES:
                upload.file_upload_status = FileUploadStatusEnum.ERROR
                upload.sub_stage.status_id = RDMExportingDataSubStageStatus.PROCESS_ERROR.key
                upload.sub_stage.save()

            elif request_status == RDMRequestStatus.SUCCESSFULLY_PROCESSED:
                upload.file_upload_status = FileUploadStatusEnum.FINISHED

            if upload.file_upload_status != FileUploadStatusEnum.IN_PROGRESS:
                upload.save()

    def _process_upload(self, upload: RDMExportingDataSubStageUploaderClientLog) -> None:
        """Обрабатывает запись загрузки данных в витрину."""
        response, log_entry = self.send_upload_status_request(upload.request_id)
        self.update_upload_status(upload, response, log_entry)
        # Обновим размер файлов в кеш (с блокировкой на время обновления)
        with self.cache.lock(f'{TOTAL_ATTACHMENTS_SIZE_KEY}:lock', timeout=300):
            queue_total_file_size = self.cache.get(TOTAL_ATTACHMENTS_SIZE_KEY) or 0
            if queue_total_file_size:
                queue_total_file_size -= upload.attachment.attachment_size
                if queue_total_file_size > 0:
                    self.cache.set(
                        TOTAL_ATTACHMENTS_SIZE_KEY,
                        queue_total_file_size,
                        timeout=settings.RDM_REDIS_CACHE_TIMEOUT_SECONDS,
                    )
