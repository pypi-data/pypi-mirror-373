from abc import (
    ABCMeta,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
)


if TYPE_CHECKING:
    from m3_db_utils.models import (
        ModelEnumValue,
    )


class BaseModelOutdatedDataCleaner(metaclass=ABCMeta):
    """Базовый класс уборщика устаревших данных моделей РВД."""

    def __init__(self, model_enum_value: 'ModelEnumValue', *args, **kwargs):
        self._model_enum_value = model_enum_value

        super().__init__(*args, **kwargs)

    @abstractmethod
    def run(self):
        """Запуск очистки устаревших данных."""
