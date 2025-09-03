from django.db.models import (
    CASCADE,
    PROTECT,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    SmallIntegerField,
)
from m3.db import (
    BaseObjectModel,
)
from uploader_client.models import (
    Entry,
)

from educommon.django.db.mixins import (
    ReprStrPreModelMixin,
)
from m3_db_utils.models import (
    ModelEnumValue,
    TitledIntegerModelEnum,
)

from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataSubStage,
    RDMExportingDataSubStageAttachment,
)
from edu_rdm_integration.stages.upload_data.enums import (
    FileUploadStatusEnum,
)


class RDMRequestStatus(TitledIntegerModelEnum):
    """Модель-перечисление статусов загрузки данных в Витрину."""

    UPLOAD_TO_BUFFER = ModelEnumValue(
        value=-1,
        title='Загрузка данных в буффер',
    )

    BUFFERED = ModelEnumValue(
        value=0,
        title='Запрос буфферизирован',
    )

    WAIT_FOR_OPEN_DELTA = ModelEnumValue(
        value=1,
        title='Ожидает открытия дельты',
    )

    IN_PROCESSING = ModelEnumValue(
        value=2,
        title='В обработке',
    )

    SUCCESSFULLY_PROCESSED = ModelEnumValue(
        value=3,
        title='Успешно обработан',
    )

    FAILED_PROCESSING = ModelEnumValue(
        value=4,
        title='Ошибка обработки запроса',
    )

    REQUEST_ID_NOT_FOUND = ModelEnumValue(
        value=5,
        title='Идентификатор запроса не обнаружен',
    )

    FORMAT_LOGICAL_CONTROL = ModelEnumValue(
        value=6,
        title='Форматно-логический контроль',
    )

    FLC_ERROR = ModelEnumValue(
        value=7,
        title='Ошибки ФЛК',
    )

    class Meta:
        db_table = 'rdm_request_status'
        verbose_name = 'Статус загрузки данных в Витрину'
        verbose_name_plural = 'Статусы загрузки данных в Витрину'


class RDMExportingDataSubStageUploaderClientLog(ReprStrPreModelMixin, BaseObjectModel):
    """Связь лога Загрузчика данных с подэтапом выгрузки данных."""

    entry = ForeignKey(
        to=Entry,
        verbose_name='Лог запроса и ответа',
        on_delete=CASCADE,
        related_name='uploader_client_log',
    )

    sub_stage = ForeignKey(
        to=RDMExportingDataSubStage,
        verbose_name='Подэтап выгрузки данных',
        on_delete=CASCADE,
    )

    attachment = ForeignKey(
        to=RDMExportingDataSubStageAttachment,
        verbose_name='Прикрепленный файл',
        on_delete=CASCADE,
    )

    request_id = CharField(
        verbose_name='Id запроса загрузки в витрину',
        max_length=100,
        blank=True,
        db_index=True,
    )

    is_emulation = BooleanField(
        verbose_name='Включен режим эмуляции',
        default=False,
    )

    file_upload_status = SmallIntegerField(
        verbose_name='Общий статус загрузки файла в витрину',
        choices=FileUploadStatusEnum.get_choices(),
        null=True,
        blank=True,
    )

    created = DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True,
    )
    modified = DateTimeField(
        verbose_name='Дата изменения',
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        db_table = 'rdm_exporting_data_sub_stage_uploader_client_log'
        verbose_name = 'Лог запроса подэтапа выгрузки данных'
        verbose_name_plural = 'Лог запроса подэтапа выгрузки данных'


class RDMUploadStatusRequestLog(ReprStrPreModelMixin, BaseObjectModel):
    """Модель связывающая статусы, загрузку файла в витрину и http-запрос к витрине."""

    upload = ForeignKey(
        verbose_name='Cвязь запроса статуса с загрузкой файла в витрину',
        to=RDMExportingDataSubStageUploaderClientLog,
        on_delete=CASCADE,
    )
    entry = ForeignKey(
        verbose_name='Cвязь запроса статуса с запросом в витрину',
        to=Entry,
        on_delete=CASCADE,
        related_name='upload_status_request_log',
    )
    request_status = ForeignKey(
        verbose_name='Статус запроса в витрине',
        to=RDMRequestStatus,
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'rdm_upload_status_request_log'
        verbose_name = 'Лог запроса подэтапа выгрузки данных'
        verbose_name_plural = 'Логи запроса подэтапа выгрузки данных'
