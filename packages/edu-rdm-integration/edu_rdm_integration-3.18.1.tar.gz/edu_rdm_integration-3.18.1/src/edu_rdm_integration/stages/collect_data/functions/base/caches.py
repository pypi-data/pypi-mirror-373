from typing import (
    Any,
    NamedTuple,
    Optional,
    Union,
)

from django.db.models import (
    Q,
)

from educommon.integration_entities.enums import (
    EntityLogOperation,
)


class LogChange(NamedTuple):
    """Операция и значения измененных полей из лога."""

    operation: EntityLogOperation
    fields: dict[str, Any]

    @property
    def is_create(self) -> bool:
        """Лог создания."""
        return self.operation == EntityLogOperation.CREATE

    @property
    def is_update(self) -> bool:
        """Лог изменения."""
        return self.operation == EntityLogOperation.UPDATE

    @property
    def is_delete(self) -> bool:
        """Лог удаления."""
        return self.operation == EntityLogOperation.DELETE


class DependencyFilter(NamedTuple):
    """Описание правила фильтрации данных модели."""

    model_label: str
    """
    Наименование модели от которой зависимы обрабатываемые логи.

    Строка должна соответствовать формату app_name.Model_name.
    """

    filters: Union[tuple[Q, ...], dict[str, Any]]
    """
    Описание полей и значений для описания фильтрации.
    """


class IgnoreLogDependency(NamedTuple):
    """Зависимость для исключения логов из последующей обработки."""

    dependency_filters: tuple[DependencyFilter, ...]
    """
    Описание фильтра применяемого к зависимости.
    """

    ignore_model_fields: Optional[dict[str, set[str]]] = None
    """
    Словарь, определяющий, какие поля моделей должны быть проигнорированы при построении графа связей между моделями.

    Ключом является наименование модели, а в множестве описываются наименования полей.
    """
