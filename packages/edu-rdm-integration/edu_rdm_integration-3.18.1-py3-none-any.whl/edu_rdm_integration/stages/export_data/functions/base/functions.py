from abc import (
    ABCMeta,
)
from typing import (
    Union,
)

from django.core.files.base import (
    ContentFile,
)
from django.core.files.storage import (
    default_storage,
)
from transliterate import (
    slugify,
)

from edu_function_tools.functions import (
    EduLazySavingPredefinedQueueGlobalHelperFunction,
)
from educommon import (
    logger,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from educommon.integration_entities.mixins import (
    EntitiesMixin,
)

from edu_rdm_integration.core.consts import (
    LOGS_DELIMITER,
)
from edu_rdm_integration.stages.export_data.consts import (
    DELIMITER,
)
from edu_rdm_integration.stages.export_data.functions.base.helpers import (
    BaseExportDataFunctionHelper,
)
from edu_rdm_integration.stages.export_data.functions.base.results import (
    BaseExportDataFunctionResult,
)
from edu_rdm_integration.stages.export_data.functions.base.validators import (
    BaseExportDataFunctionValidator,
)
from edu_rdm_integration.stages.export_data.helpers import (
    get_exporting_data_stage_attachment_path,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataStage,
    RDMExportingDataSubStage,
    RDMExportingDataSubStageAttachment,
    RDMExportingDataSubStageEntity,
    RDMExportingDataSubStageStatus,
)


class BaseExportDataFunction(
    EntitiesMixin,
    EduLazySavingPredefinedQueueGlobalHelperFunction,
    metaclass=ABCMeta,
):
    """Базовый класс функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def __init__(self, *args, stage: RDMExportingDataStage, model_ids: list[Union[int, str]], **kwargs):
        super().__init__(*args, entities=self.entities, model_ids=model_ids, **kwargs)

        self._sub_stage = RDMExportingDataSubStage.objects.create(
            stage=stage,
            function_id=self.uuid,
        )
        RDMExportingDataSubStageEntity.objects.create(
            exporting_data_sub_stage=self._sub_stage, entity_id=self.first_entity.key
        )
        self._chunk_index = kwargs.get('chunk_index')

        logger.info(f'{LOGS_DELIMITER * 3}{repr(self._sub_stage)} created.')

        self._file_name = f'rdm_{self.first_entity.key.lower()}.csv'

        self._data = {
            EntityLogOperation.CREATE: [],
            EntityLogOperation.UPDATE: [],
            EntityLogOperation.DELETE: [],
        }

        self.has_data = False
        # Id записей моделей РВД, которые в итоге попали в файл
        self.exported_to_file_model_ids = set()

    @property
    def _models_unique_id(self) -> str:
        """Возвращает название уникального идентификатора записи модели рвд."""
        return 'id'

    def _prepare_helper_class(self) -> type[BaseExportDataFunctionHelper]:
        """Возвращает класс помощника функции."""
        return BaseExportDataFunctionHelper

    def _prepare_validator_class(self) -> type[BaseExportDataFunctionValidator]:
        """Возвращает класс валидатора функции."""
        return BaseExportDataFunctionValidator

    def _prepare_result_class(self) -> type[BaseExportDataFunctionResult]:
        """Возвращает класс результата функции."""
        return BaseExportDataFunctionResult

    def _before_prepare(self, *args, **kwargs):
        """Выполнение действий функций системы."""
        self._sub_stage.status_id = RDMExportingDataSubStageStatus.IN_PROGRESS.key
        self._sub_stage.save()

        logger.info(f'{LOGS_DELIMITER * 3}change status {repr(self._sub_stage)}')

    def _prepare_record(self, entity_instance) -> list[str]:
        """Формирование списка строковых значений полей."""
        ordered_fields = self.first_entity.entity.get_ordered_fields()
        primary_key_fields = set(self.first_entity.entity.get_primary_key_fields())
        foreign_key_fields = set(self.first_entity.entity.get_foreign_key_fields())
        required_fields = set(self.first_entity.entity.get_required_fields())
        hashable_fields = set(self.first_entity.entity.get_hashable_fields())
        ignore_prefix_fields = set(self.first_entity.entity.get_ignore_prefix_key_fields())

        field_values = self.helper.prepare_record(
            entity_instance=entity_instance,
            ordered_fields=ordered_fields,
            primary_key_fields=primary_key_fields,
            foreign_key_fields=foreign_key_fields,
            required_fields=required_fields,
            hashable_fields=hashable_fields,
            ignore_prefix_fields=ignore_prefix_fields,
        )

        return field_values

    def _prepare_data(self):
        """Преобразование собранных данных в удобный для выгрузки вид."""
        logger.info(f'{LOGS_DELIMITER * 3}{self.__class__.__name__} prepare data..')

        for entity_instance in self.helper.cache.entity_instances:
            self._data[entity_instance.operation].append(
                self._prepare_record(
                    entity_instance=entity_instance,
                )
            )
            entity_instance_id = getattr(entity_instance, self._models_unique_id, None)
            if entity_instance_id:
                self.exported_to_file_model_ids.add(entity_instance_id)

        for operation in EntityLogOperation.values.keys():
            entities = self._data.get(operation)

            if entities:
                logger.info(
                    f'{LOGS_DELIMITER * 3}prepared {len(entities)} records with status '
                    f'{slugify(EntityLogOperation.values.get(operation))}..'
                )

    def _prepare_files(self):
        """Формирование файлов для дальнейшей выгрузки."""
        logger.info(f'{LOGS_DELIMITER * 3}{self.__class__.__name__} prepare files..')
        has_record = False

        for operation in EntityLogOperation.values.keys():
            records = self._data[operation]
            if records:
                title_record = f'{DELIMITER}'.join(
                    [field.lower() for field in self.first_entity.entity.get_ordered_fields()]
                )

                joined_records = '\n'.join([title_record, *[f'{DELIMITER}'.join(record) for record in records]])

                sub_stage_attachment = RDMExportingDataSubStageAttachment(
                    exporting_data_sub_stage=self._sub_stage,
                    operation=operation,
                )

                file_path = get_exporting_data_stage_attachment_path(
                    instance=sub_stage_attachment,
                    filename=self._file_name,
                )

                sub_stage_attachment.attachment = default_storage.save(file_path, ContentFile(joined_records))
                sub_stage_attachment.attachment_size = sub_stage_attachment.attachment.size

                self.do_on_save(sub_stage_attachment)
                has_record |= True

        self.has_data = has_record

    def _prepare(self, *args, **kwargs):
        """Выполнение действий функции."""
        if self.result.has_not_errors:
            if self.helper.cache.entity_instances:
                self._prepare_data()
                self._prepare_files()
            else:
                logger.info(f'{LOGS_DELIMITER * 3} no data for preparing.')

    def before_run(self, *args, **kwargs):
        """Действия перед запуском."""
        super().before_run(*args, **kwargs)

        logger.info(
            '{delimiter}{force_run}run {runner_name}{log_chunks}..'.format(
                delimiter=LOGS_DELIMITER * 2,
                force_run='force ' if kwargs.get('is_force_run', False) else '',
                runner_name=self.__class__.__name__,
                log_chunks=f' with logs chunk {self._chunk_index}' if self._chunk_index else '',
            )
        )

    def run(self, *args, **kwargs):
        """Выполнение действий функции с дальнейшим сохранением объектов в базу при отсутствии ошибок."""
        super().run(*args, **kwargs)

        if self.result.has_not_errors:
            self._sub_stage.status_id = (
                RDMExportingDataSubStageStatus.FINISHED.key
                if not self.has_data
                else RDMExportingDataSubStageStatus.READY_FOR_EXPORT.key
            )
            # Проставление подэтапа выгрузки
            if self.exported_to_file_model_ids:
                self.entities[0].main_model_enum.model.objects.filter(pk__in=self.exported_to_file_model_ids).update(
                    exporting_sub_stage=self._sub_stage,
                )

        else:
            self._sub_stage.status_id = RDMExportingDataSubStageStatus.FAILED.key

        self._sub_stage.save()

        logger.info(f'{LOGS_DELIMITER * 3}change status {repr(self._sub_stage)}')

    def get_function_data(self):
        """Возвращает словарь с данными сущностей подготовленных к выгрузке."""
        return self._data
