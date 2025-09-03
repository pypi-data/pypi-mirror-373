# Реализуйте свои unit-тесты здесь
import datetime
import shutil
from typing import (
    TYPE_CHECKING,
)

from django.conf import (
    settings,
)
from django.test import (
    TestCase,
    override_settings,
)
from django.utils import (
    timezone,
)

from edu_function_tools.models import (
    EduEntity,
    EduEntityType,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
    REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA,
)
from edu_rdm_integration.stages.collect_data.models import (
    CollectingExportedDataStage,
    CollectingExportedDataSubStage,
)
from edu_rdm_integration.stages.export_data.functions.base.consts import (
    TEST_DIR,
)
from edu_rdm_integration.stages.export_data.models import (
    ExportingDataStage,
    ExportingDataSubStage,
)


if TYPE_CHECKING:
    from edu_function_tools.managers import (
        EduRunnerManager,
    )

    from edu_rdm_integration.stages.export_data.functions.base.functions import (
        BaseExportDataFunction,
    )


class BaseExportTestCase(TestCase):
    """Базовый тест экспорта сущности РВД."""

    databases = (settings.DEFAULT_DB_ALIAS, settings.SERVICE_DB_ALIAS)

    def setUp(self) -> None:
        """Подготавливает фикстуры."""
        self.now = timezone.now()

        self.export_period_started_at = datetime.datetime.combine(self.now, datetime.time.min)
        self.export_period_ended_at = datetime.datetime.combine(self.now, datetime.time.max)

    def create_sub_stage(self, *class_names: str) -> CollectingExportedDataSubStage:
        """Создает подэтап сбора данных."""
        function_tools_entities = dict(
            EduEntity.objects.filter(
                type__in=(EduEntityType.MANAGER.key, EduEntityType.FUNCTION.key),
                tags__contains=[REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA],
                class_name__in=class_names,
            ).values_list('type', 'uuid'),
        )
        stage = CollectingExportedDataStage.objects.create(
            manager_id=function_tools_entities[EduEntityType.MANAGER.key],
        )

        return CollectingExportedDataSubStage.objects.create(
            function_id=function_tools_entities[EduEntityType.FUNCTION.key],
            stage=stage,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Удаляет временные директории."""
        try:
            shutil.rmtree(TEST_DIR)
        except OSError:
            pass

        super().tearDownClass()


class BaseExportManagerTestCase(BaseExportTestCase):
    """Базовый тест менеджера экспорта сущности РВД."""

    @property
    def manager(self) -> type['EduRunnerManager']:
        """Менеджер раннера Функции экспорта'."""
        raise NotImplementedError

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def run_exporting_manager(self) -> None:
        """Запускает менеджер экспорта."""
        runner_manager = self.manager(
            period_started_at=self.export_period_started_at,
            period_ended_at=self.export_period_ended_at,
        )
        runner_manager.run()

    def get_exporting_stage_sub_stage(self, *class_names) -> tuple[ExportingDataStage, ExportingDataSubStage]:
        """Возвращает этап и подэтап экспорта."""
        function_tools_entities = dict(
            EduEntity.objects.filter(
                type__in=(EduEntityType.MANAGER.key, EduEntityType.FUNCTION.key),
                tags__contains=[REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA],
                class_name__in=class_names,
            ).values_list('type', 'uuid'),
        )
        exported_data_stage = ExportingDataStage.objects.filter(
            manager_id=function_tools_entities[EduEntityType.MANAGER.key],
            period_started_at=self.export_period_started_at,
            period_ended_at=self.export_period_ended_at,
        ).first()
        exported_data_substage = ExportingDataSubStage.objects.filter(
            function_id=function_tools_entities[EduEntityType.FUNCTION.key], stage=exported_data_stage
        ).first()

        return exported_data_stage, exported_data_substage


class BaseExportFunctionTestCase(BaseExportTestCase):
    """Базовый тест менеджера экспорта сущности РВД."""

    @property
    def export_function(self) -> type['BaseExportDataFunction']:
        """Функция экспорта."""
        raise NotImplementedError

    def create_exporting_stage(self, *class_names: str) -> ExportingDataStage:
        """Создает этап экспорта данных."""
        function_tools_entities = dict(
            EduEntity.objects.filter(
                type__in=(EduEntityType.MANAGER.key, EduEntityType.FUNCTION.key),
                tags__contains=[REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA],
                class_name__in=class_names,
            ).values_list('type', 'uuid'),
        )
        return ExportingDataStage.objects.create(
            manager_id=function_tools_entities[EduEntityType.MANAGER.key],
            period_started_at=self.export_period_started_at,
            period_ended_at=self.export_period_ended_at,
        )

    @override_settings(MEDIA_ROOT=(TEST_DIR + '/media'))
    def run_exporting_function(self, exporting_stage: ExportingDataStage, model_ids: list[int]) -> dict:
        """Запускает функцию экспорта."""
        exporting_function = self.export_function(stage=exporting_stage, model_ids=model_ids)
        exporting_function.run()

        return exporting_function.get_function_data()
