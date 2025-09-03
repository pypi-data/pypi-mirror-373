from abc import (
    ABCMeta,
)
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    Iterator,
)

from edu_function_tools.managers import (
    EduRunnerManager,
)
from educommon import (
    logger,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    LOGS_DELIMITER,
)
from edu_rdm_integration.core.storages import (
    RegionalDataMartEntityStorage,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStageStatus,
)
from edu_rdm_integration.stages.export_data.functions.base.runners import (
    BaseExportDataRunner,
)
from edu_rdm_integration.stages.export_data.models import (
    RDMExportingDataStage,
    RDMExportingDataStageStatus,
)


class BaseExportDataRunnerManager(EduRunnerManager, metaclass=ABCMeta):
    """Менеджер ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    forced_run = True

    def __init__(
        self,
        *args,
        is_only_main_model: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Выгрузка данных производится только для основной модели сущности
        self._is_only_main_model = is_only_main_model

        self._period_started_at, self._period_ended_at = self._prepare_period(*args, **kwargs)

        self._stage = RDMExportingDataStage.objects.create(
            manager_id=self.uuid,
            period_started_at=self._period_started_at,
            period_ended_at=self._period_ended_at,
        )

        logger.info(f'{LOGS_DELIMITER}{repr(self._stage)} created.')

    @classmethod
    def _prepare_runner_class(cls) -> type[BaseExportDataRunner]:
        """Возвращает класс ранера."""
        return BaseExportDataRunner

    def _find_exporting_data_stage(self):
        """Поиск последнего подэтапа выгрузки данных сущности РВД."""
        entity_storage = RegionalDataMartEntityStorage()
        entity_storage.prepare()

        exporting_data_stage = RDMExportingDataStage.objects.filter(
            manager_id=self.uuid,
            status_id__in=(
                RDMCollectingDataStageStatus.FAILED.key,
                RDMCollectingDataStageStatus.FINISHED.key,
            ),
        ).latest('period_ended_at')

        if exporting_data_stage:
            logger.info(f'{LOGS_DELIMITER}{repr(exporting_data_stage)} sub stages found.')
        else:
            logger.info(f'{LOGS_DELIMITER} sub stages not found.')

        return exporting_data_stage

    def _prepare_period(self, *args, **kwargs) -> tuple[datetime, datetime]:
        """Формирование периода сбора данных моделей РВД."""
        period_started_at = kwargs.get('period_started_at')
        period_ended_at = kwargs.get('period_ended_at')

        if not period_started_at:
            last_exporting_data_stage = self._find_exporting_data_stage()

            if last_exporting_data_stage:
                period_started_at = last_exporting_data_stage.period_ended_at
            else:
                period_started_at = datetime.combine(date.today(), time.min)

        if not period_ended_at:
            period_ended_at = datetime.combine(date.today(), time.max)

        return period_started_at, period_ended_at

    def _prepare_model_ids_map(self) -> dict[ModelEnumValue, Iterator[int]]:
        """Осуществляется поиск записей моделей добавленных или обновленных за указанный период времени.

        Т.к. моделей влияющих на сущность может быть множество, то в методе формируется словарь, содержащий в качестве
        ключа название модели, значение - итератор идентификаторов записей.
        """
        return {}

    def _create_runner(self, *args, **kwargs):
        """Производится расширение для осуществления поиска идентификаторов записей моделей РВД для дальнейшей выгрузки.

        model_ids_map пробрасывается в ранер для дальнейшей обработки записей для формирования чанков.
        is_force_fill_cache указывается для отказа от заполнения кешей запускаемых объектов при их создании.
        """
        model_ids_map = self._prepare_model_ids_map()

        self._stage.status_id = RDMExportingDataStageStatus.IN_PROGRESS.key
        self._stage.save()

        super()._create_runner(
            *args,
            model_ids_map=model_ids_map,
            stage=self._stage,
            is_force_fill_cache=False,
            **kwargs,
        )

        logger.info(f'{LOGS_DELIMITER}change status {repr(self._stage)}')

    def _start_runner(self, *args, **kwargs):
        """Ранер необходимо запустить с отложенным заполнением кешей.

        Это позволит произвести заполнение перед запуском объекта.
        """
        super()._start_runner(*args, is_force_fill_cache=False, **kwargs)

    def _after_start_runner(self, *args, **kwargs):
        """Точка расширения поведения менеджера ранера после запуска ранера."""
        if self._runner.result.has_not_errors:
            self._stage.status_id = RDMExportingDataStageStatus.FINISHED.key
        else:
            self._stage.status_id = RDMExportingDataStageStatus.FAILED.key

        self._stage.save()

        logger.info(f'{LOGS_DELIMITER}change status {repr(self._stage)}')
