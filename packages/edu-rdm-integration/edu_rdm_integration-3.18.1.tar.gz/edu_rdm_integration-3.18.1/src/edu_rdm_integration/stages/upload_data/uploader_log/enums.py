from m3.db import (
    BaseEnumerate,
)


class RequestResultStatus(BaseEnumerate):
    """Результат выполнения запроса."""

    SUCCESS = 1
    ERROR = 2

    values = {
        SUCCESS: 'Успех',
        ERROR: 'Ошибка',
    }
