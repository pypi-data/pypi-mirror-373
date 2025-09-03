from typing import (
    Optional,
)

from m3.db import (
    BaseEnumerate,
)

from edu_rdm_integration.core.consts import (
    FAST_TRANSFER_TASK_QUEUE_NAME,
    LONG_TRANSFER_TASK_QUEUE_NAME,
    TASK_QUEUE_NAME,
)


class EntityLevelQueueTypeEnum(BaseEnumerate):
    """Тип уровня очереди сущности."""

    FAST = 1
    BASE = 2
    LONG = 3

    values = {FAST: 'Быстрая', BASE: 'Основная', LONG: 'Долгая'}

    celery_queue_maps = {
        FAST: FAST_TRANSFER_TASK_QUEUE_NAME,
        BASE: TASK_QUEUE_NAME,
        LONG: LONG_TRANSFER_TASK_QUEUE_NAME,
    }

    @classmethod
    def get_queue_name(cls, level: int) -> Optional[str]:
        """Возвращает очередь."""
        return cls.celery_queue_maps.get(level)
