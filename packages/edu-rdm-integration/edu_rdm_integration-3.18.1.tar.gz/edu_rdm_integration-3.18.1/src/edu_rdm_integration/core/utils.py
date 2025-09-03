import os
from datetime import (
    datetime,
    time,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
    Optional,
    Union,
)

from _operator import (
    attrgetter,
)
from django.conf import (
    settings,
)
from django.db.models import (
    DateTimeField,
    Expression,
    F,
    Func,
)
from django.db.models.functions import (
    Now,
)

from m3_db_utils.mixins import (
    BaseEnumRegisterMixin,
)

from edu_rdm_integration.core.consts import (
    ACADEMIC_YEAR,
)


if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )

    from edu_rdm_integration.core.helpers import (
        Graph,
    )
    from edu_rdm_integration.stages.collect_data.models import (
        RDMCollectingDataCommandProgress,
    )
    from edu_rdm_integration.stages.export_data.models import (
        RDMExportingDataCommandProgress,
    )


def register_classes(classes: Iterable[type[BaseEnumRegisterMixin]]) -> None:
    """Вызывает метод регистрации в модель-перечисление у переданных классов.

    Args:
        classes: Классы, поддерживающие интерфейс регистрации.
    """
    classes = sorted(classes, key=attrgetter('order_number'))

    for enum_class in classes:
        enum_class.register()


def split_by_academic_years(start_date: datetime, end_date: datetime) -> list[tuple]:
    """Разбивает исходный интервал из команды по учебным годам."""
    academic_year_end_date = datetime(
        start_date.year,
        ACADEMIC_YEAR['end_month'],
        ACADEMIC_YEAR['end_day'],
    )
    if academic_year_end_date <= start_date:
        academic_year_end_date = datetime(
            academic_year_end_date.year + 1,
            ACADEMIC_YEAR['end_month'],
            ACADEMIC_YEAR['end_day'],
            time.max.hour,
            time.max.minute,
            time.max.second,
        )

    splitted_interval = []
    splitted_interval.append(start_date)

    while start_date < academic_year_end_date < end_date:
        splitted_interval.append(academic_year_end_date)

        academic_year_end_date = datetime(
            academic_year_end_date.year + 1,
            ACADEMIC_YEAR['end_month'],
            ACADEMIC_YEAR['end_day'],
            time.max.hour,
            time.max.minute,
            time.max.second,
        )
        academic_year_start_date = datetime(
            academic_year_end_date.year - 1,
            ACADEMIC_YEAR['start_month'],
            ACADEMIC_YEAR['start_day'],
            time.min.hour,
            time.min.minute,
            time.min.second,
        )

        splitted_interval.append(academic_year_start_date)

    splitted_interval.append(end_date)

    iter_interval = iter(splitted_interval)
    intervals = [*zip(iter_interval, iter_interval)]

    return intervals


def split_interval_by_delta(start_date: datetime, end_date: datetime, days_delta: int) -> list[tuple]:
    """Разбивает учебный год на интервалы по дельте."""
    subinterval_end = start_date + timedelta(days=days_delta)

    splitted_interval = []
    splitted_interval.append(start_date)

    # В данном цикле проверять нужно именно даты чтобы не получилась ситуация что две одинаковые даты
    # попадут в интервалы и различаться будут лишь временем (минимальная дельта 1 день т.е. 24 часа)
    while start_date.date() < subinterval_end.date() < end_date.date():
        splitted_interval.append(subinterval_end)
        subinterval_start = subinterval_end + timedelta(days=1)
        splitted_interval.append(subinterval_start)
        subinterval_end = subinterval_end + timedelta(days=days_delta + 1)

    splitted_interval.append(end_date)

    iter_interval = iter(splitted_interval)
    intervals = [*zip(iter_interval, iter_interval)]

    return intervals


def camel_to_underscore(name: str, upper=False) -> str:
    """Переводит строку из верблюжьего в змеиный регистр.

    По умолчанию строка приводится к нижнему регистру. Несколько заглавных букв не будут разъединены, кроме последней.

    Args:
        name: форматируемая строка;
        upper: флаг перевода в верхний регистр;

    Returns:
        Строка, приведенная к змеиному регистру.

    >>> camel_to_underscore('ОдинДваТри')
    'один_два_три'
    >>> camel_to_underscore('Один_два_три')
    'один_два_три'
    >>> camel_to_underscore('Один_Два_Три')
    'один_два_три'
    >>> camel_to_underscore('__ОдинДваТри__')
    '__один_два_три__'
    >>> camel_to_underscore('__ОдинДВАТри__')
    '__один_два_три__'
    """
    output = []
    for i, c in enumerate(name):
        if i > 0:
            pc = name[i - 1]
            if c.isupper() and not pc.isupper() and pc != '_':
                output.append('_')
            elif i > 3 and not c.isupper():
                previous = name[i - 3 : i]
                if previous.isalpha() and previous.isupper():
                    output.insert(len(output) - 1, '_')

        output.append(c.upper() if upper else c.lower())

    return ''.join(output)


def build_related_model_graph(
    graph: 'Graph',
    current_model: 'Model',
    find_model: 'Model',
    ignored_model_fields: Optional[dict[str, set[str]]] = None,
) -> 'Graph':
    """Построение графа связей от модели до модели.

    Построение графа связей между моделями. Связи строятся только для полей c прямым отношением.
    Обход моделей осуществляется до нахождения нужной или до исчерпания полей со связями (FK, M2M, O2O).

    Args:
        graph: объект Graph
        current_model: объект Model для которой строятся связи
        find_model: объект Model до которой строятся связи
        ignored_model_fields: словарь с наименованием модели (формат app.Model_name)
            и перечисления полей, для которых не нужно строить связь
    """
    if current_model == find_model:
        return graph

    ignored_model_fields = ignored_model_fields or {}
    ignored_current_model_fields = set(ignored_model_fields.get(current_model._meta.label, {}))

    graph.add_vertex(current_model._meta.model_name)

    related_fields = [field for field in current_model._meta.get_fields() if field.is_relation]
    for field in related_fields:
        is_ignore = field.auto_created and not field.concrete and not field.one_to_one
        if is_ignore or field.name in ignored_current_model_fields:
            continue

        related_model = field.related_model

        if related_model._meta.model_name not in graph:
            graph.add_vertex(related_model._meta.model_name)
            graph.add_edge(current_model._meta.model_name, related_model._meta.model_name, field.name)
            graph = build_related_model_graph(graph, related_model, find_model, ignored_model_fields)
        else:
            graph.add_edge(current_model._meta.model_name, related_model._meta.model_name, field.name)

    return graph


def get_data_command_progress_attachment_path(
    instance: Union['RDMCollectingDataCommandProgress', 'RDMExportingDataCommandProgress'], filename: str
) -> str:
    """Возвращает путь до файла-вложения при формировании команды сборки или выгрузки данных.

    Args:
        instance: объект ExportDataCommandProgress или объект CollectDataCommandProgres
        filename: имя загружаемого файла

    Returns:
        Строковое представление пути
    """
    date_now = datetime.now()

    return os.path.join(
        settings.UPLOADS,
        date_now.strftime('%Y/%m/%d'),
        instance.__class__.__name__.lower(),
        str(instance.type),
        filename,
    )


class MakeInterval(Func):
    """Функция обработки даты/времени."""

    template = 'make_interval(%(expressions)s)'

    def __init__(
        self,
        *,
        years: Union[int, F] = 0,
        months: Union[int, F] = 0,
        weeks: Union[int, F] = 0,
        days: Union[int, F] = 0,
        hours: Union[int, F] = 0,
        minutes: Union[int, F] = 0,
        seconds: Union[float, F] = 0.0,
        output_field=None,
    ) -> None:
        self.years = years
        self.months = months
        self.weeks = weeks
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

        super().__init__(
            self.years,
            self.months,
            self.weeks,
            self.days,
            self.hours,
            self.minutes,
            self.seconds,
            output_field=output_field or DateTimeField(),
        )


def make_passed_datetime_from_today(
    *,
    years: int = 0,
    months: int = 0,
    days: int = 0,
) -> Union[datetime, Expression, F]:
    """Возвращает выражение на лет/месяцев/дней меньше относительно сегодня."""
    now_expr = Now()

    return now_expr - MakeInterval(years=years, months=months, days=days)
