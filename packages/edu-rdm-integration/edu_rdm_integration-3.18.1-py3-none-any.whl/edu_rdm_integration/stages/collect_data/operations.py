import os
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
    Optional,
)

from django.conf import (
    settings,
)
from django.utils import (
    timezone,
)

from edu_function_tools.managers import (
    EduRunnerManager,
)
from educommon import (
    logger,
)
from educommon.utils.date import (
    get_today_min_datetime,
)
from m3_db_utils.consts import (
    DEFAULT_ORDER_NUMBER,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
)
from edu_rdm_integration.core.operations import (
    BaseOperationData,
)
from edu_rdm_integration.core.signals import (
    manager_created,
)
from edu_rdm_integration.core.storages import (
    RegionalDataMartEntityStorage,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)
from edu_rdm_integration.stages.collect_data.helpers import (
    get_collecting_managers_max_period_ended_dates,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStage,
    RDMCollectingDataStageStatus,
)


if TYPE_CHECKING:
    from educommon.audit_log.models import (
        AuditLog,
    )

    from edu_rdm_integration.stages.collect_data.generators import (
        BaseEduLogGenerator,
    )


class BaseCollectModelsData(BaseOperationData):
    """Базовый класс сбора данных моделей РВД."""

    def __init__(
        self,
        models: Iterable[str],
        logs_period_started_at=datetime.combine(date.today(), time.min),
        logs_period_ended_at=datetime.combine(date.today(), time.min),
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Если модели не указаны, берется значение по умолчанию - все модели:
        model_enum_data = RDMModelEnum.get_enum_data()
        models = models if models else model_enum_data.keys()
        self.models: list[ModelEnumValue] = [v for k, v in model_enum_data.items() if k in models]

        self.logs_period_started_at = logs_period_started_at
        self.logs_period_ended_at = logs_period_ended_at

        # Классы менеджеров Функций, которые должны быть запущены для сбора данных моделей РВД
        self._collecting_data_managers: dict[str, type[EduRunnerManager]] = {}

        # Результаты работы Функций сбора данных моделей РВД
        self._collecting_data_results = []

    @property
    def _log_file_path(self) -> str:
        """Путь до лог файла."""
        return os.path.join(settings.MEDIA_ROOT, settings.RDM_COLLECT_LOG_DIR, f'{self.command_id}.log')

    def _has_stage_created_or_in_progress(self, manager_id: str, model: str) -> bool:
        """Проверяет есть ли готовый к работе stage или в работе для данной модели.

        В общем случае разрешается параллельный сбор данных одной модели.
        """
        return False

    def _find_collecting_models_data_managers(self):
        """Поиск менеджеров Функций, которые должны быть запущены для сбора данных моделей РВД."""
        logger.info('collecting models data managers..')

        entity_storage = RegionalDataMartEntityStorage()
        entity_storage.prepare()

        collecting_models_data_managers_map = entity_storage.prepare_entities_manager_map(
            tags={REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA},
        )

        models = filter(lambda model: model.order_number != DEFAULT_ORDER_NUMBER, self.models)

        for model_enum in models:
            manager_class = collecting_models_data_managers_map.get(model_enum.key)

            if manager_class and not self._has_stage_created_or_in_progress(manager_class.uuid, model_enum.key):
                self._collecting_data_managers[model_enum.key] = manager_class

        logger.info('collecting models data managers finished')

    def _collect_models_data(self, *args, logs: Optional[dict[str, list['AuditLog']]] = None, **kwargs):
        """Запуск Функций по формированию данных моделей РВД из логов."""
        logger.info('collect models data..')

        kwargs['logs_period_started_at'] = self.logs_period_started_at
        kwargs['logs_period_ended_at'] = self.logs_period_ended_at

        for model_key, manager_class in self._collecting_data_managers.items():
            model_logs = logs.get(model_key) if logs else None
            manager = manager_class(*args, logs=model_logs, command_id=self.command_id, **kwargs)

            if self.command_id:
                # Подается сигнал, что менеджер создан:
                manager_created.send(sender=manager, command_id=self.command_id)

            manager.run()

            self._collecting_data_results.append(manager.result)

        logger.info('collecting models data finished.')

    def _collect(self):
        """Собирает данные моделей РВД."""
        logger.info(f'start collecting data of models - {", ".join([model.key for model in self.models])}..')

        self._find_collecting_models_data_managers()
        self._collect_models_data()

        logger.info('collecting data of models is finished.')

    def collect(self):
        """Запускает сбор данных."""
        try:
            self._collect()
        except Exception as err:
            logger.exception(err)
            raise err
        finally:
            self._remove_file_handler()


class BaseCollectModelsDataByGeneratingLogs(BaseCollectModelsData):
    """Сбор данных моделей РВД на основе существующих в БД данных моделей ЭШ.

    Можно регулировать, для каких моделей должен быть произведен сбор данных, и период, за который должны
    быть собраны логи. Логи формируются в процессе выполнения команды при помощи генератора логов
    EduSchoolLogGenerator для указанной модели.
    """

    def __init__(
        self,
        models: Iterable[str],
        logs_period_started_at=datetime.combine(date.today(), time.min),
        logs_period_ended_at=datetime.combine(date.today(), time.min),
        institute_ids=(),
        **kwargs,
    ):
        super().__init__(models, logs_period_started_at, logs_period_ended_at, **kwargs)

        # Учебные заведения, для которых производится выгрузка
        self.institute_ids = institute_ids
        # Генератор логов
        self.log_generator = self._prepare_log_generator()

    def _prepare_log_generator(self) -> 'BaseEduLogGenerator':
        """Возвращает генератор логов."""
        raise NotImplementedError

    def _generate_logs(self) -> list[tuple[dict[str, list['AuditLog']], datetime, datetime]]:
        """Генерация логов.

        Осуществляет генерацию логов по уже существующим записям в базе данных. В качестве параметров указываются
        начало и конец периода сбора логов. Генерация логов производится только для указанных моделей.
        """
        temp_logs: dict[str, list['AuditLog']] = {}

        for model in self.models:
            logs = self.log_generator.generate(
                model=model,
                logs_period_started_at=self.logs_period_started_at,
                logs_period_ended_at=self.logs_period_ended_at,
                institute_ids=self.institute_ids,
            )

            temp_logs[model.key] = logs

        return [(temp_logs, self.logs_period_started_at, self.logs_period_ended_at)]

    def _collect(self):
        """Собирает данные моделей РВД."""
        logger.info(f'start collecting data of models - {", ".join([model.key for model in self.models])}..')
        self._find_collecting_models_data_managers()

        temp_kwargs = {}

        for logs, logs_period_started_at, logs_period_ended_at in self._generate_logs():
            temp_kwargs['logs_period_started_at'] = logs_period_started_at
            temp_kwargs['logs_period_ended_at'] = logs_period_ended_at

            self._collect_models_data(logs=logs, **temp_kwargs)

        logger.info('collecting data of models is finished.')


class BaseCollectLatestModelsData(BaseCollectModelsData):
    """Сбор данных моделей РВД на основе логов за период с последней сборки до указанной даты."""

    def __init__(self, *args, use_times_limit: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        # Если этот параметр не указан - то высчитываем временные рамки по менеджеру, не учитывая переданные
        # logs_period_started_at и  logs_period_ended_at
        self.use_times_limit = use_times_limit

    def _has_stage_created_or_in_progress(self, manager_id: str, model: str) -> bool:
        """Проверяет есть ли готовый к работе stage или в работе для данной модели."""
        stage_created_or_in_progress = RDMCollectingDataStage.objects.filter(
            manager_id=manager_id,
            status_id__in=(RDMCollectingDataStageStatus.CREATED.key, RDMCollectingDataStageStatus.IN_PROGRESS.key),
        ).exists()

        if stage_created_or_in_progress:
            logger.info(f'model {model} is skipped because it is already created or in progress!')

        return stage_created_or_in_progress

    def _collect_models_data(self, *args, logs: Optional[dict[str, list['AuditLog']]] = None, **kwargs) -> None:
        """Запуск Функций по формированию данных из логов для дальнейшей выгрузки."""
        logger.info('collect models data..')

        managers_last_period_ended_at = get_collecting_managers_max_period_ended_dates(
            self._collecting_data_managers.values()
        )

        for model_key, manager_class in self._collecting_data_managers.items():
            model_logs = logs.get(model_key) if logs else None
            manager_last_period_ended_at = managers_last_period_ended_at.get(manager_class.uuid)

            kwargs['logs_period_started_at'] = (
                self.logs_period_started_at
                if self.use_times_limit
                else (manager_last_period_ended_at or get_today_min_datetime())
            )
            kwargs['logs_period_ended_at'] = self.logs_period_ended_at if self.use_times_limit else timezone.now()

            manager = manager_class(*args, logs=model_logs, **kwargs)

            if self.command_id:
                # Подается сигнал, что менеджер создан:
                manager_created.send(sender=manager, command_id=self.command_id)

            manager.run()

            self._collecting_data_results.append(manager.result)

        logger.info('collecting models data finished.')


class CollectModelsData(BaseCollectModelsData):
    """Сбор данных моделей РВД за указанных период по существующим логам."""
