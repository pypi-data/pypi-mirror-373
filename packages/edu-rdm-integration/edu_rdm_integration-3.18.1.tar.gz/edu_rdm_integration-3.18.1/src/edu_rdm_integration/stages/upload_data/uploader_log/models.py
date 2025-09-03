from functools import (
    cached_property,
)
from io import (
    StringIO,
)
from typing import (
    Optional,
)

from django.db.models import (
    Manager,
)
from uploader_client.models import (
    Entry,
)

from edu_rdm_integration.stages.upload_data.uploader_log.enums import (
    RequestResultStatus,
)
from edu_rdm_integration.stages.upload_data.uploader_log.managers import (
    UploaderClientLogManager,
)


class UploaderClientLog(Entry):
    """Прокси модель Загрузчика данных в витрину."""

    objects = UploaderClientLogManager()
    base_objects = Manager()

    @cached_property
    def http_method_and_url(self) -> tuple[str, str]:
        """Возвращает http-метод и url из поля запроса Entry.request."""
        request = StringIO(self.request)
        request_first_line = request.readline()
        request.close()

        method, url = request_first_line.split(' ')[:2]
        if not (method and url.startswith('http')):
            method = url = ''

        return method.strip('[]'), url

    @cached_property
    def http_response_status(self) -> Optional[str]:
        """Статус-код запроса к витрине."""
        try:
            http_status = self.response.split(' ')[0].strip('[]')

            if not http_status:
                return None

            if 200 <= int(http_status) < 300:
                http_status = 'Успех'
            elif int(http_status) >= 400:
                http_status = 'Ошибка'
        except (IndexError, AttributeError):
            http_status = None

        return http_status

    @property
    def http_method(self) -> str:
        """Значение http-метода."""
        return self.http_method_and_url[0]

    @property
    def request_url(self) -> str:
        """URL запроса."""
        return self.http_method_and_url[1]

    @property
    def request_error(self) -> Optional[str]:
        """Ошибка запроса."""
        return self.error

    @property
    def result_status_display(self) -> str:
        """Результат запроса."""
        result_status = getattr(self, 'result_status', RequestResultStatus.ERROR)

        return RequestResultStatus.values.get(result_status) or RequestResultStatus.values[RequestResultStatus.ERROR]

    class Meta:
        proxy = True
