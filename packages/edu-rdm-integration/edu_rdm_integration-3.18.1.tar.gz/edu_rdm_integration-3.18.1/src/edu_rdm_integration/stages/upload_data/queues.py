import json
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Any,
    Union,
)

from django.conf import (
    settings,
)
from redis import (
    Redis,
)

from edu_rdm_integration.core.helpers import (
    as_text,
    get_redis_version,
)
from edu_rdm_integration.stages.export_data.consts import (
    REDIS_QUEUE_KEY_DELIMITER,
)
from edu_rdm_integration.stages.upload_data.dataclasses import (
    UploadFile,
)


class Queue(ABC):
    """Интерфейс очереди."""

    queue_key: str = ''

    @property
    @abstractmethod
    def count(self) -> int:
        """Возвращает кол-во всех элементов в очереди."""

    def is_empty(self) -> bool:
        """Возвращает признак пустая ли очередь."""
        return self.count == 0

    @abstractmethod
    def enqueue(self, *args, **kwargs) -> None:
        """Поместить в очередь."""

    @abstractmethod
    def dequeue(self) -> Any:
        """Вернуть из очереди."""

    @abstractmethod
    def clear(self) -> None:
        """Очистить очередь."""

    @abstractmethod
    def delete_from_queue(self, *args, **kwargs) -> None:
        """Удалить из очереди конкретное значение."""


class RdmRedisSubStageAttachmentQueue(Queue):
    """Очередь файлов и подэтапов.

    Данные хранятся следующим образом:
    - Подэтапы с сущностями (строка вида "407-MARKS" (sub_stage_id-entity)) хранятся в упорядоченном множестве Redis
    (Sorted Set in Redis)
    - Информация по файлам стандартно по ключу - ключом выступает sub_stage_id
    """

    queue_key = 'rdm:export_sub_stage_ids_queue'
    prefix = 'rdm:'

    def __init__(self, *args, **kwargs):
        """Инициализация объекта очереди Queue."""
        super().__init__(*args, **kwargs)

        self.connection = Redis(
            host=settings.RDM_REDIS_HOST,
            port=settings.RDM_REDIS_PORT,
            db=settings.RDM_REDIS_DB,
            password=settings.RDM_REDIS_PASSWORD,
        )

    def _make_key(self, key: Union[int, str]) -> str:
        """Формирование ключа."""
        return f'{self.prefix}{key}'

    @property
    def count(self) -> int:
        """Возвращает количество подэтапов в очереди."""
        return self.connection.zcard(self.queue_key)

    def enqueue(self, stage_id, entity_name: str, attachmets: list[UploadFile]) -> None:
        """Помещение в очередь.

        Подэтап попадает в упорядоченную очередь.
        """
        stage_info = f'{stage_id}{REDIS_QUEUE_KEY_DELIMITER}{entity_name}'
        pipe = self.connection.pipeline()
        # Упрядочиваем подэтапы
        pipe.zadd(self.queue_key, {stage_info: stage_id})
        pipe.set(self._make_key(stage_id), json.dumps(attachmets))
        pipe.execute()

    def dequeue_sub_stage_attachments(self, sub_stage_id: int) -> list[UploadFile]:
        """Возвращает файлы подэтапа из кеша."""
        result = []
        attachments = self.connection.get(self._make_key(sub_stage_id))
        attachments = json.loads(attachments) if attachments else ()
        for attachment in attachments:
            result.append(UploadFile(*attachment))

        return result

    def dequeue(self) -> dict[tuple[Any, Any], list[UploadFile]]:
        """Возвращает подэтапы из очереди - берется вся очередь без ограничений."""
        upload_files = {}
        exported_sub_stages = self.connection.zrange(self.queue_key, 0, -1)
        for sub_stage in exported_sub_stages:
            sub_stage_info = as_text(sub_stage)
            sub_stage_id, sub_stage_entity = sub_stage_info.split(REDIS_QUEUE_KEY_DELIMITER)
            upload_files[(sub_stage_id, sub_stage_entity)] = self.dequeue_sub_stage_attachments(sub_stage_id)

        return upload_files

    def delete_sub_stages_attachments(self, sub_stage_id: int) -> None:
        """Удаляет информацию о файлах из кеша."""
        self.connection.delete(self._make_key(sub_stage_id))

    def delete_sub_stages_from_queue(self, sub_stage_id: int, entity_name: str) -> None:
        """Удаляет подэтап из очереди."""
        self.connection.zrem(self.queue_key, f'{sub_stage_id}{REDIS_QUEUE_KEY_DELIMITER}{entity_name}')

    def delete_from_queue(self, sub_stage_id: int, entity_name: str) -> None:
        """Удаление элемента из очереди."""
        self.delete_sub_stages_attachments(sub_stage_id)
        self.delete_sub_stages_from_queue(sub_stage_id, entity_name)

    def clear(self) -> int:
        """Удаление из очереди всех подэтапов."""
        script = """
            local prefix = "{0}"
            local q = KEYS[1]
            local count = 0
            while true do
                local stage = redis.call("zpopmin", q)
                local stage_id = stage[2]

                if stage_id == nil then
                    break
                end
                redis.call("del", prefix..stage_id)
                count = count + 1
            end
            return count
        """.format(self.prefix).encode('utf-8')

        script = self.connection.register_script(script)

        return script(keys=[self.queue_key])

    @property
    def connection_info(self) -> str:
        """Информация об используемом соединении."""
        version = '.'.join(map(str, get_redis_version(self.connection)))
        kwargs = self.connection.connection_pool.connection_kwargs
        host = kwargs['host']
        port = kwargs['port']
        db = kwargs['db']

        return f'Redis {version} on {host}:{port}/{db}'
