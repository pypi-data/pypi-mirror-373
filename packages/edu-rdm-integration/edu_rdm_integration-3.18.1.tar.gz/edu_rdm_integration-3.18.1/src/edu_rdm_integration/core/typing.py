from typing import (
    Sequence,
    TypeVar,
    Union,
)

from django.db.models import (
    Expression,
    Model,
)


# Тип, обозначающий любую модель. При указании в качестве type annotation
# можно указать, что аргументом может быть любая модель или тип модели (через
# type[MODEL_TYPE_VAR]), а сама функция возвращает инстанс этой
# конкретной модели
MODEL_TYPE_VAR = TypeVar('MODEL_TYPE_VAR', bound=Model)

# Аннотация типов для id записи в БД
RECORD_IDS = Union[
    tuple[int, ...],
    tuple[str, ...],
    list[int],
    list[str],
    Sequence[int],
    Sequence[str],
    Expression,
]
