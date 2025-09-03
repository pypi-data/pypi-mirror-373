from abc import (
    ABCMeta,
)

from edu_function_tools.functions import (
    EduLazySavingPredefinedQueueFunction,
)
from educommon import (
    logger,
)
from educommon.integration_entities.mixins import (
    EntitiesMixin,
)

from edu_rdm_integration.core.consts import (
    LOGS_DELIMITER,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStage,
    RDMCollectingDataSubStage,
    RDMCollectingDataSubStageStatus,
)


class BaseCollectingCalculatedDataFunction(
    EntitiesMixin,
    EduLazySavingPredefinedQueueFunction,
    metaclass=ABCMeta,
):
    """Базовый класс функций сбора данных для интеграции с "Региональная витрина данных"."""

    def __init__(self, *args, stage: RDMCollectingDataStage, **kwargs):
        super().__init__(*args, stage=stage, **kwargs)

        previous_sub_stage = (
            RDMCollectingDataSubStage.objects.filter(
                function_id=self.uuid,
            )
            .order_by('started_at')
            .only('pk')
            .first()
        )

        self._sub_stage = RDMCollectingDataSubStage.objects.create(
            stage=stage,
            function_id=self.uuid,
            previous_id=getattr(previous_sub_stage, 'pk', None),
        )

        self._chunk_index = kwargs.get('chunk_index')

        logger.info(f'{LOGS_DELIMITER * 3}created {repr(self._sub_stage)}')

    def _before_prepare(self, *args, **kwargs):
        """Выполнение действий функций системы."""
        self._sub_stage.status_id = RDMCollectingDataSubStageStatus.IN_PROGRESS.key
        self._sub_stage.save()

        logger.info(f'{LOGS_DELIMITER * 3}change status {repr(self._sub_stage)}')

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

        if self.result.errors:
            self._sub_stage.status_id = RDMCollectingDataSubStageStatus.FAILED.key
        else:
            self._sub_stage.status_id = RDMCollectingDataSubStageStatus.READY_TO_EXPORT.key

        self._sub_stage.save()

        logger.info(f'{LOGS_DELIMITER * 3}change status {repr(self._sub_stage)}')

        logger.info(f'{LOGS_DELIMITER * 3}{self.__class__.__name__} finished.')
