import logging
import os
from typing import (
    Union,
)

from django.conf import (
    settings,
)

from educommon import (
    logger,
)

from edu_rdm_integration.core.operations import (
    BaseOperationData,
)
from edu_rdm_integration.core.redis_cache import (
    AbstractCache,
)
from edu_rdm_integration.stages.export_data.consts import (
    TOTAL_ATTACHMENTS_SIZE_KEY,
)
from edu_rdm_integration.stages.upload_data.export_managers import (
    ExportQueueSender,
    WorkerSender,
)
from edu_rdm_integration.stages.upload_data.queues import (
    Queue,
)


class UploadData(BaseOperationData):
    """Класс отправки файлов в витрину."""

    def __init__(
        self,
        data_cache: AbstractCache,
        queue: Queue,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.data_cache = data_cache
        self.queue = queue

        self._configure_agent_client()
        self.result = {
            'total_file_size': 0,  # Общий размер отправленных файлов
            'queue_is_full': False,  # Признак переполнения очереди
            'uploaded_entities': '',  # Список сущностей, попавших в выгрузку
        }

    @property
    def _log_file_path(self) -> Union[str, bytes]:
        """Путь до лог файла."""
        return os.path.join(settings.MEDIA_ROOT, settings.RDM_UPLOAD_LOG_DIR, 'upload_entity.log')

    def _add_file_handler(self) -> None:
        """Добавляет обработчик логов."""
        self._file_handler = logging.FileHandler(self._log_file_path)

        logging.getLogger('info_logger').addHandler(self._file_handler)
        logging.getLogger('exception_logger').addHandler(self._file_handler)

    # TODO https://jira.bars.group/browse/EDUSCHL-22492. Вынужденная мера, т.к. при запуске команды не производится
    #  проверка готовности конфигов приложений. Нужно переработать механизм конфигурирования клиента загрузчика.
    def _configure_agent_client(self):
        """Конфигурирование клиента загрузчика данных в Витрину."""
        import uploader_client
        from django.core.cache import (
            DEFAULT_CACHE_ALIAS,
            caches,
        )
        from uploader_client.contrib.rdm.interfaces.configurations import (
            RegionalDataMartEmulationUploaderConfig,
            RegionalDataMartUploaderConfig,
        )

        if settings.RDM_UPLOADER_CLIENT_ENABLE_REQUEST_EMULATION:
            uploader_client.set_config(
                RegionalDataMartEmulationUploaderConfig(
                    interface='uploader_client.contrib.rdm.interfaces.rest.OpenAPIInterfaceEmulation',
                    url=settings.RDM_UPLOADER_CLIENT_URL,
                    datamart_name=settings.RDM_UPLOADER_CLIENT_DATAMART_NAME,
                    timeout=1,
                    request_retries=1,
                    file_status=settings.RDM_RESPONSE_FILE_STATUS,
                )
            )
        elif settings.RDM_UPLOADER_CLIENT_USE_PROXY_API:
            uploader_client.set_config(
                RegionalDataMartUploaderConfig(
                    interface='uploader_client.contrib.rdm.interfaces.rest.ProxyAPIInterface',
                    cache=caches[DEFAULT_CACHE_ALIAS],
                    url=settings.RDM_UPLOADER_CLIENT_URL,
                    datamart_name=settings.RDM_UPLOADER_CLIENT_DATAMART_NAME,
                    timeout=settings.RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT,
                    request_retries=settings.RDM_UPLOADER_CLIENT_REQUEST_RETRIES,
                    organization_ogrn=settings.RDM_UPLOADER_CLIENT_ORGANIZATION_OGRN,
                    installation_name=settings.RDM_UPLOADER_CLIENT_INSTALLATION_NAME,
                    installation_id=settings.RDM_UPLOADER_CLIENT_INSTALLATION_ID,
                    username=settings.RDM_UPLOADER_CLIENT_USERNAME,
                    password=settings.RDM_UPLOADER_CLIENT_PASSWORD,
                )
            )
        else:
            uploader_client.set_config(
                RegionalDataMartUploaderConfig(
                    url=settings.RDM_UPLOADER_CLIENT_URL,
                    datamart_name=settings.RDM_UPLOADER_CLIENT_DATAMART_NAME,
                    timeout=settings.RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT,
                    request_retries=settings.RDM_UPLOADER_CLIENT_REQUEST_RETRIES,
                )
            )

    def update_total_queue_size_in_cache(self, received_files_size: int):
        """Обновление размера файлов в кеш."""
        with self.data_cache.lock(f'{TOTAL_ATTACHMENTS_SIZE_KEY}:lock', timeout=300):
            queue_total_file_size = self.data_cache.get(TOTAL_ATTACHMENTS_SIZE_KEY) or 0
            if queue_total_file_size:
                queue_total_file_size -= received_files_size
                if queue_total_file_size > 0:
                    self.data_cache.set(
                        TOTAL_ATTACHMENTS_SIZE_KEY,
                        queue_total_file_size,
                        timeout=settings.RDM_REDIS_CACHE_TIMEOUT_SECONDS,
                    )

    def upload_data(self, *args, **kwargs):
        """Запускает отправку данных в витрину."""
        try:
            exporter = ExportQueueSender(self.data_cache, self.queue, settings.RDM_UPLOAD_DATA_TASK_EXPORT_STAGES)
            exporter.run()

            self.result['queue_is_full'] = exporter.queue_is_full
            self.result['total_file_size'] = exporter.queue_total_file_size

            # Если очередь не переполнена - то отправляем данные в витрину
            if not exporter.queue_is_full:
                sender = WorkerSender(self.queue)
                sender.run()

                if sender.entities:
                    self.result['uploaded_entities'] = ','.join(sender.entities)

                if sender.received_file_size:
                    self.update_total_queue_size_in_cache(sender.received_file_size)

        except Exception as err:
            logger.exception(err)
            raise err
        finally:
            self._remove_file_handler()

        return self.result
