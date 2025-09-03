from dataclasses import (
    dataclass,
)
from typing import (
    Any,
)

from django.conf import (
    settings,
)
from pydantic import (
    Field,
)
from uploader_client.interfaces import (
    OpenAPIRequest,
)


@dataclass
class RegionalDataMartEntityRequest(OpenAPIRequest):
    """Запрос на отправку данных сущности."""

    datamart_name: str
    table_name: str
    method: str
    operation: str
    headers: dict
    parameters: dict = Field(default_factory=dict)
    files: list = Field(default_factory=list)
    data: Any = None

    def get_method(self):
        """Получение метода запроса."""
        return self.method

    def get_url(self):
        """Получение сформированного URL."""
        return f'/v2/datamarts/{self.datamart_name}/tables/{self.table_name}/{self.operation}'

    def get_headers(self) -> dict:
        """Возвращает заголовки запроса."""
        return self.headers

    def get_files(self):
        """Возвращает файлы для отправки."""
        files = [(file_name, file_.open('rb')) for file_name, file_ in self.files]

        return files

    def get_data(self):
        """Возвращает содержимое запроса."""
        return self.data

    def get_timeout(self):
        """Возвращает время ожидания ответа."""
        return settings.RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT


@dataclass
class RegionalDataMartStatusRequest(OpenAPIRequest):
    """Запрос для получения статуса загрузки данных в РВД."""

    request_id: str
    method: str
    headers: dict
    parameters: dict = Field(default_factory=dict)

    def get_method(self):
        """Получение метода запроса."""
        return self.method

    def get_url(self):
        """Получение сформированного URL."""
        return f'/v2/requests/{self.request_id}/status'

    def get_headers(self) -> dict:
        """Возвращает заголовки запроса."""
        return self.headers

    def get_timeout(self):
        """Возвращает время ожидания ответа."""
        return settings.RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT
