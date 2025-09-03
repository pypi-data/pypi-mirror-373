import inspect
import sys
from importlib import (
    import_module,
)

from educommon.integration_entities.entities import (
    BaseEntity,
)

from edu_rdm_integration.core.utils import (
    register_classes,
)
from edu_rdm_integration.rdm_entities.mixins import (
    EntityEnumRegisterMixin,
)


def is_register_entity(class_) -> bool:
    """Проверяет, является ли класс регистрируемой сущностью."""
    return inspect.isclass(class_) and issubclass(class_, BaseEntity) and issubclass(class_, EntityEnumRegisterMixin)


def register_entities(import_path: str) -> None:
    """Находит регистрируемые сущности в модуле по переданному пути и регистрирует в RegionalDataMartEntityEnum.

    Args:
        import_path: Путь до пакета, хранящего классы сущностей;
    """
    import_module(import_path)
    entities_module = sys.modules[import_path]

    register_classes([c[1] for c in inspect.getmembers(entities_module, is_register_entity)])
