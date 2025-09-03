from django.db.models import (
    CASCADE,
    BooleanField,
    OneToOneField,
    PositiveIntegerField,
)
from m3 import (
    json_encode,
)
from m3.db import (
    BaseObjectModel,
)

from edu_rdm_integration.pipelines.transfer.enums import (
    EntityLevelQueueTypeEnum,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)


class TransferredEntity(BaseObjectModel):
    """Сущность, по которой должен быть произведен сбор и экспорт данных."""

    entity = OneToOneField(
        to=RDMEntityEnum,
        verbose_name='Сущность',
        on_delete=CASCADE,
    )
    export_enabled = BooleanField(
        verbose_name='Включение экспорта для сущности',
        default=True,
    )
    queue_level = PositiveIntegerField(
        choices=EntityLevelQueueTypeEnum.get_choices(),
        default=EntityLevelQueueTypeEnum.BASE,
        verbose_name='Уровень очереди',
    )

    class Meta:
        db_table = 'rdm_transferred_entity'
        verbose_name = 'Сущность, по которой должен быть произведен сбор и экспорт данных'
        verbose_name_plural = 'Сущности, по которым должен быть произведен сбор и экспорт данных'

    @json_encode
    def no_export(self):
        """Формирует отображение признака отключения экспорта."""
        return 'Нет' if self.export_enabled else 'Да'
