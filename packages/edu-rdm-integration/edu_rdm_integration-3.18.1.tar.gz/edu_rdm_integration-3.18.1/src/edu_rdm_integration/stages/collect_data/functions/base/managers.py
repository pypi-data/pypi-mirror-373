from abc import (
    ABCMeta,
)
from datetime import (
    datetime,
)
from typing import (
    TYPE_CHECKING,
)

from django.apps import (
    apps,
)

from edu_function_tools.managers import (
    EduRunnerManager,
)
from edu_function_tools.runners import (
    EduRunner,
)
from educommon import (
    logger,
)
from educommon.audit_log.helpers import (
    get_models_table_ids,
)
from educommon.audit_log.models import (
    AuditLog,
)

from edu_rdm_integration.core.consts import (
    DATETIME_FORMAT,
    LOGS_DELIMITER,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStage,
    RDMCollectingDataStageStatus,
)


if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )


class BaseCollectingDataRunnerManager(EduRunnerManager, metaclass=ABCMeta):
    """Базовый менеджер ранеров функций сбора данных для интеграции с "Региональная витрина данных"."""

    forced_run = True

    def __init__(
        self,
        logs_period_started_at: datetime,
        logs_period_ended_at: datetime,
        logs: list[AuditLog] = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Логи для сущности
        self._logs = logs

        self._logs_period_started_at = logs_period_started_at
        self._logs_period_ended_at = logs_period_ended_at
        self._stage = RDMCollectingDataStage.objects.create(
            manager_id=self.uuid,
            logs_period_started_at=logs_period_started_at,
            logs_period_ended_at=logs_period_ended_at,
        )

        self._command_id = kwargs.get('command_id')

        logger.info(f'{LOGS_DELIMITER}logs period started at {self._logs_period_started_at.strftime(DATETIME_FORMAT)}')
        logger.info(f'{LOGS_DELIMITER}log period ended at {self._logs_period_ended_at.strftime(DATETIME_FORMAT)}')
        logger.info(f'{LOGS_DELIMITER}created {repr(self._stage)}')

    def _collect_runner_regional_data_mart_integration_entities(
        self,
        runner_class: type[EduRunner],
        runner_regional_data_mart_integration_entities: list[str],
    ):
        """Собирает и возвращает список сущностей."""
        for runnable_class in runner_class._prepare_runnable_classes():
            if hasattr(runnable_class, '_prepare_runnable_classes'):
                self._collect_runner_regional_data_mart_integration_entities(
                    runner_class=runnable_class,
                    runner_regional_data_mart_integration_entities=runner_regional_data_mart_integration_entities,
                )

                continue

            if hasattr(runnable_class, 'entities'):
                entities = getattr(runnable_class, 'entities')

                runner_regional_data_mart_integration_entities.extend(entities)

    def _get_loggable_models(self) -> set['Model']:
        """Возвращает перечень моделей по которым собираются логи."""
        loggable_models = set()
        regional_data_mart_integration_entities = []

        self._collect_runner_regional_data_mart_integration_entities(
            self.runner_class,
            regional_data_mart_integration_entities,
        )
        for entity in regional_data_mart_integration_entities:
            loggable_models.update(entity.loggable_models)
            # TODO: EDUSCHL-20938 Произвести рефакторинг plugins_info.
            if hasattr(entity, 'plugins_info'):
                for app_name, app_contents in entity.plugins_info.items():
                    if not apps.is_installed(app_name):
                        continue

                    for app_content in app_contents:
                        app_label, model_name = app_content.split('.')
                        try:
                            model = apps.get_model(app_label=app_label, model_name=model_name)
                            loggable_models.add(model)
                        except (ValueError, LookupError):
                            continue

        return loggable_models

    def _collect_logs(self):
        """Сбор логов для дальнейшей обработки."""
        return (
            AuditLog.objects.filter(
                time__gte=self._logs_period_started_at,
                time__lt=self._logs_period_ended_at,
                table_id__in=get_models_table_ids(self._get_loggable_models()),
            )
            .order_by('time')
            .iterator()
        )

    def _create_runner(self, *args, **kwargs):
        """Метод создания ранера."""
        collected_logs = self._logs or self._collect_logs()

        logger.info(f'{LOGS_DELIMITER}{self.__class__.__name__} start preparing logs records..')

        self._stage.status_id = RDMCollectingDataStageStatus.IN_PROGRESS.key
        self._stage.save()

        super()._create_runner(
            *args,
            logs=collected_logs,
            stage=self._stage,
            is_force_fill_cache=False,
            **kwargs,
        )

        logger.info(f'{LOGS_DELIMITER}change status {repr(self._stage)}')

    def _start_runner(self, *args, **kwargs):
        """Ранер необходимо запустить с отложенным заполнением кешей.

        Необходимо для заполнения перед запуском объекта.
        """
        super()._start_runner(*args, is_force_fill_cache=False, **kwargs)

    def _after_start_runner(self, *args, **kwargs):
        """Точка расширения поведения менеджера ранера после запуска ранера."""
        if self._runner.result.errors:
            self._stage.status_id = RDMCollectingDataStageStatus.FAILED.key
        else:
            self._stage.status_id = RDMCollectingDataStageStatus.FINISHED.key

        self._stage.save()

        logger.info(f'{LOGS_DELIMITER}change status {repr(self._stage)}')
