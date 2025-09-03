import uuid
from datetime import (
    datetime,
)

from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    DateTimeField,
    FileField,
    ForeignKey,
    PositiveIntegerField,
    PositiveSmallIntegerField,
    SmallIntegerField,
    UUIDField,
)
from django.utils import (
    timezone,
)
from m3.db import (
    BaseObjectModel,
)

from edu_function_tools.models import (
    EduEntity,
)
from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from m3_db_utils.models import (
    ModelEnumValue,
    TitledModelEnum,
)

from edu_rdm_integration.core.enums import (
    CommandType,
)
from edu_rdm_integration.core.utils import (
    get_data_command_progress_attachment_path,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)
from edu_rdm_integration.stages.export_data.helpers import (
    get_exporting_data_stage_attachment_path,
)


class RDMExportingDataStageStatus(TitledModelEnum):
    """Статус этапа выгрузки данных."""

    CREATED = ModelEnumValue(
        title='Создан',
    )

    IN_PROGRESS = ModelEnumValue(
        title='В процессе',
    )

    FAILED = ModelEnumValue(
        title='Завершено с ошибками',
    )

    FINISHED = ModelEnumValue(
        title='Завершено',
    )

    class Meta:
        db_table = 'rdm_exporting_data_stage_status'
        verbose_name = 'Модель-перечисление статусов этапа выгрузки данных'
        verbose_name_plural = 'Модели-перечисления статусов этапов выгрузки данных'


class RDMExportingDataStage(ReprStrPreModelMixin, BaseObjectModel):
    """Этап выгрузки данных."""

    manager = ForeignKey(
        to=EduEntity,
        verbose_name='Менеджер ранера Функции',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    period_started_at = DateTimeField(
        'Левая граница периода выборки данных для выгрузки',
        db_index=True,
    )

    period_ended_at = DateTimeField(
        'Правая граница периода выборки данных для выгрузки',
        db_index=True,
    )

    started_at = DateTimeField(
        'Время начала выгрузки данных',
        auto_now_add=True,
    )

    ended_at = DateTimeField(
        'Время завершения выгрузки данных',
        null=True,
        blank=True,
    )

    status = ForeignKey(
        to=RDMExportingDataStageStatus,
        verbose_name='Статус',
        on_delete=PROTECT,
        default=RDMExportingDataStageStatus.CREATED.key,
    )

    class Meta:
        db_table = 'rdm_exporting_data_stage'
        verbose_name = 'Этап формирования данных для выгрузки'
        verbose_name_plural = 'Этапы формирования данных для выгрузки'

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['manager_id', 'started_at', 'ended_at', 'status_id']

    def save(self, *args, **kwargs):
        """Сохранение этапа экспорта данных."""
        if 'update_fields' in kwargs:
            kwargs['update_fields'] = set(kwargs['update_fields'])
            # Добавляем все поля, которые меняются в save()
            kwargs['update_fields'].update({'ended_at'})

        if (
            self.status_id in (RDMExportingDataStageStatus.FAILED.key, RDMExportingDataStageStatus.FINISHED.key)
            and not self.ended_at
        ):
            self.ended_at = datetime.now()

        super().save(*args, **kwargs)


class RDMExportingDataSubStageStatus(TitledModelEnum):
    """Модель-перечисление статусов этапа выгрузки данных."""

    CREATED = ModelEnumValue(
        title='Создан',
    )

    IN_PROGRESS = ModelEnumValue(
        title='Запущен',
    )

    FAILED = ModelEnumValue(
        title='Завершено с ошибками',
    )

    FINISHED = ModelEnumValue(
        title='Завершен',
    )
    READY_FOR_EXPORT = ModelEnumValue(
        title='Готов к выгрузке',
    )
    PROCESS_ERROR = ModelEnumValue(title='Ошибка обработки витриной')

    class Meta:
        db_table = 'rdm_exporting_data_sub_stage_status'
        verbose_name = 'Модель-перечисление статусов подэтапа выгрузки данных'
        verbose_name_plural = 'Модели-перечисления статусов подэтапов выгрузки данных'

    @classmethod
    def get_not_finished_statuses(cls):
        """Получить список статусов, которые не завершены."""
        return cls.CREATED, cls.IN_PROGRESS, cls.FAILED, cls.READY_FOR_EXPORT, cls.PROCESS_ERROR


class RDMExportingDataSubStage(ReprStrPreModelMixin, BaseObjectModel):
    """Подэтап выгрузки данных."""

    function = ForeignKey(
        to=EduEntity,
        verbose_name='Функция',
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    stage = ForeignKey(
        to=RDMExportingDataStage,
        verbose_name='Этап выгрузки данных',
        on_delete=CASCADE,
    )

    started_at = DateTimeField(
        verbose_name='Время начала сбора данных',
        auto_now_add=True,
        db_index=True,
    )

    ended_at = DateTimeField(
        verbose_name='Время завершения сбора данных',
        null=True,
        blank=True,
        db_index=True,
    )

    status = ForeignKey(
        to=RDMExportingDataSubStageStatus,
        verbose_name='Статус',
        on_delete=PROTECT,
        default=RDMExportingDataSubStageStatus.CREATED.key,
    )

    class Meta:
        db_table = 'rdm_exporting_data_sub_stage'
        verbose_name = 'Стадия выгрузки данных'
        verbose_name_plural = 'Стадии выгрузки данных'

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['function_id', 'collecting_data_sub_stage_id', 'stage_id', 'started_at', 'ended_at', 'status_id']

    def save(self, *args, **kwargs):
        """Сохранение экземпляра модели."""
        if 'update_fields' in kwargs:
            kwargs['update_fields'] = set(kwargs['update_fields'])
            # Добавляем все поля, которые меняются в save()
            kwargs['update_fields'].update({'ended_at'})

        if (
            self.status_id
            in {
                RDMExportingDataSubStageStatus.FAILED.key,
                RDMExportingDataSubStageStatus.FINISHED.key,
                RDMExportingDataSubStageStatus.READY_FOR_EXPORT.key,
            }
            and not self.ended_at
        ):
            self.ended_at = datetime.now()

        super().save(*args, **kwargs)


class RDMExportingDataSubStageAttachment(ReprStrPreModelMixin, BaseObjectModel):
    """Сгенерированный файл для дальнейшей выгрузки в "Региональная витрина данных"."""

    exporting_data_sub_stage = ForeignKey(
        to=RDMExportingDataSubStage,
        verbose_name='Подэтап выгрузки данных',
        on_delete=CASCADE,
    )

    # TODO PYTD-22 В зависимости от принятого решения по инструменту ограничения доступа к media-файлам, нужно будет
    #  изменить тип поля или оставить как есть
    attachment = FileField(
        verbose_name='Сгенерированный файл',
        upload_to=get_exporting_data_stage_attachment_path,
        max_length=512,
        null=True,
        blank=True,
    )

    operation = SmallIntegerField(
        verbose_name='Действие',
        choices=EntityLogOperation.get_choices(),
    )

    created = DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
        blank=True,
    )
    modified = DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
        null=True,
        blank=True,
    )
    attachment_size = PositiveIntegerField(null=True, verbose_name='Размер файла (байт)')

    class Meta:
        db_table = 'rdm_exporting_data_sub_stage_attachment'
        verbose_name = 'Сгенерированный файл для дальнейшей выгрузки в "Региональная витрина данных"'
        verbose_name_plural = 'Сгенерированные файлы для дальнейшей выгрузки в "Региональная витрина данных"'

    @property
    def attrs_for_repr_str(self):
        """Список атрибутов для отображения экземпляра модели."""
        return ['exporting_data_sub_stage_id', 'attachment', 'operation', 'created', 'modified']


class RDMExportingDataSubStageEntity(BaseObjectModel):
    """Модель связи сущности и подэтапа выгрузки."""

    entity = ForeignKey(
        to=RDMEntityEnum,
        verbose_name='Сущность РВД',
        on_delete=PROTECT,
    )

    exporting_data_sub_stage = ForeignKey(
        to=RDMExportingDataSubStage,
        verbose_name='Подэтап выгрузки данных',
        on_delete=CASCADE,
    )

    class Meta:
        db_table = 'rdm_exporting_data_sub_stage_entity'
        verbose_name = 'Связь сущности и подэтапа выгрузки'
        verbose_name_plural = 'Связи сущности и подэтапа выгрузки'


class RDMExportingDataCommandProgress(ReprStrPreModelMixin, BaseObjectModel):
    """Команда экспорта данных."""

    task = ForeignKey(
        to='async_task.RunningTask',
        verbose_name='Асинхронная задача',
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )
    logs_link = FileField(
        upload_to=get_data_command_progress_attachment_path,
        max_length=255,
        verbose_name='Файл лога',
    )
    type = PositiveSmallIntegerField(  # noqa: A003
        verbose_name='Тип команды',
        choices=CommandType.get_choices(),
    )
    stage = ForeignKey(
        to=RDMExportingDataStage,
        verbose_name='Этап выгрузки данных',
        null=True,
        blank=True,
        on_delete=SET_NULL,
    )
    entity = ForeignKey(
        to=RDMEntityEnum,
        verbose_name='Сущность РВД',
        on_delete=PROTECT,
    )
    created = DateTimeField(
        verbose_name='Дата создания',
        default=timezone.now,
    )
    period_started_at = DateTimeField(
        'Левая граница периода выборки данных для выгрузки',
    )
    period_ended_at = DateTimeField(
        'Правая граница периода выборки данных для выгрузки',
    )
    generation_id = UUIDField(
        'Идентификатор генерации',
        default=uuid.uuid4,
    )

    class Meta:
        db_table = 'edu_rdm_exporting_data_command_progress'
        verbose_name = 'Команда экспорта данных'
        verbose_name_plural = 'Команды экспорта данных'
