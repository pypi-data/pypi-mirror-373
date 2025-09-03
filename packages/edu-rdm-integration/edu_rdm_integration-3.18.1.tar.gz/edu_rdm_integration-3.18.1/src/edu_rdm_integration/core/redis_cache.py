from abc import (
    ABCMeta,
    abstractmethod,
)


class AbstractCache(metaclass=ABCMeta):
    """Абстрактный интерфейс для кеша отправки."""

    @abstractmethod
    def get(self, key, default=None, **kwargs):
        """Возвращает значение из кеша по ключу."""

    @abstractmethod
    def set(self, key, value, timeout=None, **kwargs):
        """Сохраняет значение в кеш по ключу."""

    @abstractmethod
    def lock(self, name, timeout=None, **kwargs):
        """Захватывает блокировку."""
