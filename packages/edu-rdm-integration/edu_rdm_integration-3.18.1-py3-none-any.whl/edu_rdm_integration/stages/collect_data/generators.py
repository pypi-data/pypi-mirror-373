import uuid
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    TYPE_CHECKING,
    Iterable,
    List,
    Optional,
    Tuple,
)

from django.apps import (
    apps,
)
from django.db import (
    connection,
)

from educommon.utils.date import (
    DatesSplitter,
)
from educommon.utils.seqtools import (
    make_chunks,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    BATCH_SIZE,
    DATE_FORMAT,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)
from edu_rdm_integration.stages.collect_data.consts import (
    ALL_UNITS_IN_COMMAND,
)


if TYPE_CHECKING:
    from educommon.audit_log.models import (
        AuditLog,
    )


class BaseEduLogGenerator:
    """Базовый класс генератора логов для указанной модели РВД за определенный период времени.

    Для каждой модели РВД есть модели в продукте, создание экземпляров которых, сигнализирует о необходимости сбора
    и выгрузки данных в РВД. Модели можно найти в
    edu_rdm_integration/mapping.py MODEL_FIELDS_LOG_FILTER, принадлежность к конкретной
    модели РВД необходимо определять в функциях.
    """

    def _get_generate_logs_method(self, model: ModelEnumValue):
        return getattr(self, f'_generate_{model.key.lower()}_logs')

    def generate(
        self,
        model: ModelEnumValue,
        logs_period_started_at: datetime = datetime.combine(date.today(), time.min),
        logs_period_ended_at: datetime = datetime.combine(date.today(), time.max),
        institute_ids: Optional[tuple[int, ...]] = (),
    ) -> list['AuditLog']:
        """Возвращает список сгенерированных экземпляров модели AuditLog.

        Формирование логов производится для указанной модели РВД за указанный период времени.

        Args:
            model: значение модели РВД из модели-перечисления;
            logs_period_started_at: начало периода формирования логов;
            logs_period_ended_at: конец периода формирования логов;
            institute_ids: идентификаторы учебных заведений.
        """
        generate_logs_method = self._get_generate_logs_method(model)

        logs = generate_logs_method(
            logs_period_started_at=logs_period_started_at,
            logs_period_ended_at=logs_period_ended_at,
            institute_ids=institute_ids,
        )

        return logs


class BaseFirstCollectModelsDataCommandsGenerator:
    """Класс, который генерирует список данных для формирования команд для сбора данных РВД."""

    def __init__(
        self,
        models: Iterable[str],
        split_by: Optional[str],
        split_mode: Optional[str],
        split_by_quantity: Optional[int],
        logs_period_started_at=datetime.combine(date.today(), time.min),
        logs_period_ended_at=datetime.combine(date.today(), time.min),
        batch_size=BATCH_SIZE,
    ):
        """Инициализация."""
        # Если модели не указаны, берется значение по умолчанию - все модели:
        models = models if models else RDMModelEnum.get_enum_data().keys()
        self.regional_data_mart_models: list[ModelEnumValue] = [
            RDMModelEnum.get_model_enum_value(model) for model in models
        ]

        self.logs_period_started_at = logs_period_started_at
        self.logs_period_ended_at = logs_period_ended_at

        self.splitter = (
            DatesSplitter(split_by=split_by, split_mode=split_mode, split_by_quantity=split_by_quantity)
            if split_by
            else None
        )

        self.batch_size = batch_size

        self.generation_id = uuid.uuid4()

        # Правую дату нужно увеличивать на одну секунду, т.к. подрезались миллисекунды
        self.get_logs_periods_sql = """
            select min(created),
                   max(created)  + interval '1 second',
                   row_batched
            from (
                select row_num,
                       ((row_num - 1) / {batch_size}) + 1 AS row_batched,
                       created
                from (
                    select row_number() over (order by created) as row_num,
                           created
                    from (
                        select *
                        from (
                        {ordered_rows}
                        ) as union_rows
                        order by created
                    ) as ordered
                ) as numbered
            ) as batched
            group by row_batched
            order by row_batched;
            """

        self.ordered_rows_query = """
            select distinct date_trunc('second', created) as created
            from "{table_name}"
            where created between '{period_started_at}' and '{period_ended_at}'
            """

    def generate(self) -> list:
        """Генерирует список данных для формирования команд для сбора данных РВД."""
        params_for_commands = []

        for rdm_model in self.regional_data_mart_models:
            # Если не заполнен creating_trigger_models и plugins_info, то список не формируется
            if not rdm_model.creating_trigger_models and not getattr(rdm_model, 'plugins_info', None):
                continue

            if self.splitter:
                # Формируется список с разбиением по split_by:
                intervals = self.splitter.split(
                    period_started_at=self.logs_period_started_at,
                    period_ended_at=self.logs_period_ended_at,
                )

                params_for_model = [
                    {
                        'period_started_at': start_datetime,
                        'period_ended_at': end_datetime,
                        'model': rdm_model.key,
                        'generation_id': self.generation_id,
                    }
                    for start_datetime, end_datetime in intervals
                ]

            # Если подпериод не указан, то формируется список с разбиением по batch_size
            else:
                ordered_rows_queries = [
                    self.ordered_rows_query.format(
                        table_name=model._meta.db_table,
                        period_started_at=self.logs_period_started_at,
                        period_ended_at=self.logs_period_ended_at,
                    )
                    for model in rdm_model.creating_trigger_models
                ]

                if hasattr(rdm_model, 'plugins_info'):
                    for app_name, app_models in rdm_model.plugins_info.items():
                        if apps.is_installed(app_name):
                            for app_model in app_models:
                                model = apps.get_model(app_model)
                                if model:
                                    ordered_rows_queries.append(
                                        self.ordered_rows_query.format(
                                            table_name=model._meta.db_table,
                                            period_started_at=self.logs_period_started_at.strftime(DATE_FORMAT),
                                            period_ended_at=self.logs_period_ended_at.strftime(DATE_FORMAT),
                                        )
                                    )

                ordered_rows_queries_sql = 'union'.join(ordered_rows_queries)

                temp_get_logs_periods_sql = self.get_logs_periods_sql.format(
                    batch_size=self.batch_size,
                    ordered_rows=ordered_rows_queries_sql,
                )

                with connection.cursor() as cursor:
                    cursor.execute(temp_get_logs_periods_sql)
                    rows = cursor.fetchall()

                params_for_model = [
                    {
                        'period_started_at': period_started_at,
                        'period_ended_at': period_ended_at,
                        'model': rdm_model.key,
                        'generation_id': self.generation_id,
                    }
                    for period_started_at, period_ended_at, _ in rows
                ]

            if params_for_model:
                # Корректируем границы начала и конца сбора данных под значения введенные пользователем
                params_for_model[0]['period_started_at'] = self.logs_period_started_at
                params_for_model[-1]['period_ended_at'] = self.logs_period_ended_at

            params_for_commands.extend(params_for_model)

        return params_for_commands


class FirstCollectModelsDataCommandsGenerator(BaseFirstCollectModelsDataCommandsGenerator):
    """Генерирует команды collect_models_by_generating_logs."""

    def generate_with_split(
        self,
        by_institutes: bool,
        institute_ids: Optional[Iterable[int]],
        institute_count: Optional[int],
        actual_institute_ids: Iterable[int],
    ):
        """Генерирует команды с разделением по организациям.

        Args:
            by_institutes: Разделение по организациям.
            institute_ids: ID организаций по которым генерируются команды.
            institute_count: Разделение по кол-ву организаций.
            actual_institute_ids: Текущие организации в системе.

        Returns:
            Cписок данных для формирования команд.
        """
        result_commands: List[dict] = []
        institute_ids_chunks: Tuple[Optional[Iterable]] = (None,)

        raw_commands = self.generate()

        if by_institutes and not institute_ids:
            # Если указано разбиение по организациям, без перечисления организаций:
            if institute_count == ALL_UNITS_IN_COMMAND:
                # Если указано -1, то в команде будут указаны все
                # существующие организации в параметре institute_ids.
                institute_ids_chunks = ((),)
            else:
                # Если значение, отличное от -1, то в каждой команде будет
                # указано institute_count кол-во организаций в параметре institute_ids.
                institute_ids_chunks = make_chunks(
                    iterable=actual_institute_ids,
                    size=institute_count,
                    is_list=True,
                )
        elif institute_ids:
            # Если указано разбиение по организациям и/или перечислены организации:
            if institute_count == ALL_UNITS_IN_COMMAND:
                institute_ids_chunks = (institute_ids,)
            else:
                institute_ids_chunks = make_chunks(
                    iterable=institute_ids,
                    size=institute_count,
                    is_list=True,
                )

        # Переформируются команды с учетом организаций и их кол-ва для каждой команды:
        for institute_ids_chunk in institute_ids_chunks:
            for command in raw_commands:
                result_commands.append({**command, 'institute_ids': institute_ids_chunk})

        return result_commands
