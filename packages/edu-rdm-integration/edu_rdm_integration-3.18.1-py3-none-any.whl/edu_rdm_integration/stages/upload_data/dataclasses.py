from typing import (
    NamedTuple,
)


class UploadFile(NamedTuple):
    """Структура файла подэтапа для очереди отправки."""

    attachment_id: int
    attachment_name: str
    attachment_size: int
    operation: str
