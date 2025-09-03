import datetime
import decimal
import uuid
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)
from unittest import (
    mock,
)

from django.conf import (
    settings,
)
from django.db.models.fields.files import (
    FieldFile,
)
from django.test import (
    TestCase,
)
from django.utils import (
    timezone,
)

from edu_function_tools.models import (
    EduEntity,
    EduEntityType,
)
from educommon.audit_log.models import (
    AuditLog,
    Table,
)
from educommon.integration_entities.enums import (
    EntityLogOperation,
)
from educommon.utils.phone_number.phone_number import (
    PhoneNumber,
)

from edu_rdm_integration.core.consts import (
    REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA,
)
from edu_rdm_integration.stages.collect_data.models import (
    RDMCollectingDataStage,
    RDMCollectingDataSubStage,
)


if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )

    from edu_function_tools.managers import (
        EduRunnerManager,
    )


class BaseCollectingFunctionTestCase(TestCase):
    """Базовый класс тестирования Функции сбора."""

    databases = (settings.DEFAULT_DB_ALIAS, settings.SERVICE_DB_ALIAS)

    @property
    def manager(self) -> type['EduRunnerManager']:
        """Менеджер раннера Функции сбора."""
        raise NotImplementedError

    @classmethod
    def tearDownClass(cls) -> None:
        """Вызывается один раз после запуска всех тестов класса."""
        cls.delete_auditlogs()

        super().tearDownClass()

    @staticmethod
    def delete_auditlogs() -> None:
        """Удаляет логи."""
        AuditLog.objects.all().delete()

    def setUp(self) -> None:
        """Подготавливает фикстуры."""
        self.now = timezone.now()

    def run_collecting_function(self) -> None:
        """Запускает Функцию сбора."""
        runner_manager = self.manager(
            logs_period_started_at=datetime.datetime.combine(self.now, datetime.time.min),
            logs_period_ended_at=datetime.datetime.combine(self.now, datetime.time.max),
        )
        runner_manager.run()

    @mock.patch('educommon.audit_log.models.AuditLog.ready_to_save')
    @mock.patch('educommon.audit_log.models.AuditLog.is_read_only')
    def create_auditlog(
        self,
        is_read_only_mock: mock.MagicMock,
        ready_to_save_mock: mock.MagicMock,
        *,
        instance: 'Model',
        changes: Optional[dict[str, Any]] = None,
        operation: EntityLogOperation = EntityLogOperation.UPDATE,
    ) -> None:
        """Создает AuditLog."""
        is_read_only_mock.return_value = False
        ready_to_save_mock.return_value = True

        table = Table.objects.only('pk').get(name=instance._meta.db_table)

        timestamp = datetime.datetime.combine(self.now, timezone.now().time())

        if changes is None:
            changes = {'__stub': None}  # changes не может быть пустым
        else:
            changes['modified'] = timestamp.isoformat().replace('T', ' ')

        AuditLog.objects.create(
            user_id=1,
            user_type_id=1,
            ip='127.0.0.1',
            data=self._clean_data(instance),
            changes=changes,
            table=table,
            object_id=instance.pk,
            time=timestamp,
            operation=operation,
        )

    def create_sub_stage(self, *class_names: str) -> RDMCollectingDataSubStage:
        """Создает подэтап сбора данных."""
        function_tools_entities = dict(
            EduEntity.objects.filter(
                type__in=(EduEntityType.MANAGER.key, EduEntityType.FUNCTION.key),
                tags__contains=[REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA],
                class_name__in=class_names,
            ).values_list('type', 'uuid'),
        )
        stage = RDMCollectingDataStage.objects.create(
            manager_id=function_tools_entities[EduEntityType.MANAGER.key],
        )

        return RDMCollectingDataSubStage.objects.create(
            function_id=function_tools_entities[EduEntityType.FUNCTION.key],
            stage=stage,
        )

    def _clean_data(self, instance: 'Model') -> dict[str, Optional[str]]:
        """Подготавливает данные экземпляра модели для формирования AuditLog'a."""
        fields = {}

        for key, value in vars(instance).items():
            if key.startswith('_'):
                continue

            if isinstance(value, datetime.datetime):
                fields[key] = value.strftime('%Y-%m-%d %H:%M:%S.%f%z')
            elif isinstance(value, datetime.date):
                fields[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, datetime.time):
                fields[key] = value.strftime('%H:%M:%S')
            elif isinstance(value, bool):
                fields[key] = 't' if value else 'f'
            elif isinstance(value, (int, float, uuid.UUID, decimal.Decimal)):
                fields[key] = str(value)
            elif isinstance(value, FieldFile):
                fields[key] = value.name
            elif isinstance(value, list):
                fields[key] = f'{{{",".join(map(str, value))}}}'
            elif isinstance(value, PhoneNumber):
                fields[key] = value.cleaned
            else:
                fields[key] = value

        return fields
