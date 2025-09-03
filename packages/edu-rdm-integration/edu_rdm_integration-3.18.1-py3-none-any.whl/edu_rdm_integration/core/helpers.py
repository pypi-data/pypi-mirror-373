import heapq
import os
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Optional,
    Union,
)

from django.conf import (
    settings,
)
from django.utils.html import (
    format_html,
)
from django.utils.safestring import (
    mark_safe,
)
from redis import (
    Redis,
    ResponseError,
)

from educommon.async_task.exceptions import (
    TaskUniqueException,
)
from educommon.async_task.tasks import (
    AsyncTask,
)

from edu_rdm_integration.core.consts import (
    TASK_QUEUE_NAME,
)
from edu_rdm_integration.pipelines.transfer.enums import (
    EntityLevelQueueTypeEnum,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataCommandProgress,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataCommandProgress,
)


if TYPE_CHECKING:
    from django.db.models.query import (
        QuerySet,
    )


class BaseTaskProgressUpdater(ABC):
    """Базовый класс, который обновляет данные в таблицах, хранящих команды сбора/экспорта."""

    @property
    @abstractmethod
    def update_model(self):
        """Основная модель для обновления.

        Необходимо задать в дочернем классе.
        """

    @property
    @abstractmethod
    def async_model(self):
        """Модель асинхронных задач.

        Необходимо задать в дочернем классе.
        """

    def set_async_task(self, commands_to_update: Dict[RDMCollectingDataCommandProgress, str]) -> None:
        """Устанавливает ссылку на асинхронную задачу."""
        for command, task_uuid in commands_to_update.items():
            command.task_id = task_uuid

        self.update_model.objects.bulk_update(
            commands_to_update,
            ['task_id'],
        )

    def set_stage(self, command_id: int, stage_id: int) -> None:
        """Устанавливает ссылку на stage."""
        self.update_model.objects.filter(
            id=command_id,
        ).update(
            stage_id=stage_id,
        )


class BaseTaskStarter(ABC):
    """Запускает асинхронные задачи."""

    updater: BaseTaskProgressUpdater = None
    async_task: AsyncTask = None
    model_only_fields: Iterable[str] = ()

    def run(self, command_ids: Iterable[int], queue_level: Optional[int] = None) -> str:
        """Создает задачи и ставит их в очередь."""
        commands_to_update = {}
        skipped_commands_count = 0
        commands = self._get_commands(command_ids)
        queue_name = None

        if queue_level:
            queue_name = EntityLevelQueueTypeEnum.get_queue_name(level=queue_level)

        if not queue_name:
            queue_name = TASK_QUEUE_NAME

        for command in commands:
            if command.task_id:
                # Повторный запуск команды не допускается
                skipped_commands_count += 1
                continue

            try:
                async_result = self.async_task().apply_async(  # noqa pylint: disable=not-callable
                    args=None,
                    queue=queue_name,
                    routing_key=queue_name,
                    kwargs={
                        'command_id': command.id,
                    },
                    lock_data={
                        'lock_params': {
                            'command_id': f'{self.updater.update_model.__name__}_{command.id}',
                        },
                    },
                )
            except TaskUniqueException:
                skipped_commands_count += 1
                continue
            else:
                commands_to_update[command] = async_result.task_id

        if commands_to_update:
            self.updater().set_async_task(commands_to_update)  # noqa pylint: disable=not-callable

        message = f'Поставлено задач в очередь: {len(commands_to_update)} из {len(commands)}.'
        if skipped_commands_count:
            message += (
                f' Кол-во задач, которые были запущены ранее: {skipped_commands_count}. '
                'Однажды запущенные задачи не могут быть запущены снова!'
            )

        return message

    def _get_commands(self, command_ids: Iterable[int]) -> 'QuerySet':
        """Возвращает Queryset команд для создания задач."""
        return self.updater.update_model.objects.filter(
            id__in=command_ids,
        ).only(
            *self.model_only_fields,
        )


class Graph:
    """Граф связей между моделями.

    Предназначен для поиска кратчайшей связи между моделями и дальнейшего построения lookup`а
    до необходимого поля модели с последующим использованием его в фильтре.
    Вершинами графа выступают наименования моделей. Ребро содержит наименования модели связанной
    с другой моделью и наименования поля, через которое осуществляется связь.
    Вместо наименования поля может быть наименование обратной связи между моделями,
    в случае если данная связь является связью OneToOne.
    """

    def __init__(self):
        self.vertices: dict[str, dict[str, Optional[str]]] = {}
        """Словарь для хранения данных графа."""

    def add_vertex(self, vertex: str):
        """Добавление вершины."""
        if vertex not in self.vertices:
            self.vertices[vertex] = {}

    def add_edge(self, vertex1: str, vertex2: str, edge_name: str):
        """Добавление связи."""
        if vertex1 in self.vertices and vertex2 in self.vertices:
            self.vertices[vertex1][vertex2] = edge_name
            if vertex1 not in self.vertices[vertex2]:
                self.vertices[vertex2][vertex1] = None

    def remove_vertex(self, vertex: str):
        """Удаление вершины."""
        if vertex in self.vertices:
            del self.vertices[vertex]

            # Удаляем связанные с удаленной вершиной ребра
            for neighbour in self.vertices:
                if vertex in self.vertices[neighbour]:
                    self.vertices[neighbour].pop(vertex)

    def remove_edge(self, vertex1: str, vertex2: str):
        """Удаление связи."""
        if vertex1 in self.vertices and vertex2 in self.vertices:
            self.vertices[vertex1].pop(vertex2, None)
            self.vertices[vertex2].pop(vertex1, None)

    def get_vertices(self) -> list[str]:
        """Получение списка всех вершин."""
        return list(self.vertices)

    def get_edges(self) -> list[tuple[str, str, Optional[str]]]:
        """Получение всех связей."""
        edges = []

        for vertex, neighbors in self.vertices.items():
            for neighboring_vertex, edge_name in neighbors.items():
                edge = (vertex, neighboring_vertex, edge_name)
                edges.append(edge)

        return edges

    def __contains__(self, vertex: str) -> bool:
        return vertex in self.vertices

    def __iter__(self):
        return iter(self.vertices)

    def __getitem__(self, vertex: str):
        return self.vertices.get(vertex, {})

    def get_edges_between_vertices(
        self, from_vertex: str, to_vertex: str, required_edge_name: bool = True
    ) -> list[str]:
        """Получение списка наименований ребер между вершинами."""
        if from_vertex not in self.vertices and to_vertex not in self.vertices:
            return []

        path = []
        edge_weight = 1

        # Инициализация расстояния между вершинами
        distances = {vertex: float('inf') for vertex in self}
        distances[from_vertex] = 0

        priority_queue = [(0, from_vertex)]

        while priority_queue:
            current_distance, current_vertex = heapq.heappop(priority_queue)

            # Если достигнута конечная вершина, заканчиваем цикл
            if current_vertex == to_vertex:
                break

            # Проверяем все смежные вершины и обновляем расстояния, если находим более короткий путь
            for neighbor, edge_name in self[current_vertex].items():
                distance = current_distance + edge_weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    heapq.heappush(priority_queue, (distance, neighbor))

        # Восстанавливаем путь от конечной вершины к начальной
        current_vertex = to_vertex
        while current_vertex != from_vertex:
            previous_vertex = edge_name = None

            for neighbor in self[current_vertex]:
                if distances[current_vertex] == distances[neighbor] + 1:
                    for neighbor_vertex, edge_name in self[neighbor].items():
                        if neighbor_vertex == current_vertex:
                            break

                    previous_vertex = neighbor
                    break

            if required_edge_name and not edge_name:
                path = []
                break

            path.append(edge_name)
            current_vertex = previous_vertex

        # Инвертируем путь и возвращаем его
        path.reverse()

        return path


def save_command_log_link(
    command: Union[RDMCollectingDataCommandProgress, RDMExportingDataCommandProgress], log_dir: str
) -> None:
    """Сохраняет ссылку на лог команды."""
    log_file = os.path.join(settings.MEDIA_ROOT, log_dir, f'{command.id}.log')
    if os.path.exists(log_file):
        command.logs_link = os.path.join(log_dir, f'{command.id}.log')
        command.save()


def make_download_link(fieldfile, text='Cкачать', show_filename=False):
    """Возвращает html ссылку для скачивания файла.

    Если show_filename == True, использует имя файла как текст ссылки
    """
    link = mark_safe('')
    if fieldfile:
        link_text = os.path.basename(fieldfile.name) if show_filename else text
        link = make_link(fieldfile.url, link_text)

    return link


def make_link(url, text):
    """Возвращает экаранированную html ссылку файла."""
    return format_html('<a href="{}" target="_blank" download>{}</a>', url, text)


def get_redis_version(connection: 'Redis') -> tuple[int, int, int]:
    """Возвращает кортеж с версией сервера Redis."""
    try:
        version = getattr(connection, '__redis_server_version', None)
        if not version:
            version = tuple([int(n) for n in connection.info('server')['redis_version'].split('.')[:3]])
            setattr(connection, '__redis_server_version', version)
    except ResponseError:
        version = (0, 0, 0)

    return version


def as_text(v: Union[bytes, str]) -> str:
    """Конвертирует последовательность байт в строку."""
    if isinstance(v, bytes):
        return v.decode('utf-8')
    elif isinstance(v, str):
        return v
    else:
        raise ValueError('Неизвестный тип %r' % type(v))
