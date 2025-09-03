import uuid
from datetime import (
    date,
    datetime,
    time,
)
from typing import (
    Iterable,
)

from django.db import (
    connection,
)

from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.core.consts import (
    BATCH_SIZE,
    DATE_FORMAT,
)
from edu_rdm_integration.rdm_entities.models import (
    RDMEntityEnum,
)


class BaseFirstExportEntitiesDataCommandsGenerator:
    """Класс, который генерирует список данных для формирования команд для экспорта данных РВД."""

    def __init__(
        self,
        entities: Iterable[str],
        period_started_at=datetime.combine(date.today(), time.min),
        period_ended_at=datetime.combine(date.today(), time.min),
        batch_size=BATCH_SIZE,
        **kwargs,
    ):
        """Инициализация."""
        # Если сущности не указаны, берется значение по умолчанию - все сущности:
        entities = entities if entities else RDMEntityEnum.get_enum_data().keys()
        self.entities: list[ModelEnumValue] = [RDMEntityEnum.get_model_enum_value(entity) for entity in entities]

        self.period_started_at = period_started_at
        self.period_ended_at = period_ended_at

        self.batch_size = batch_size

        self.generation_id = uuid.uuid4()

        # Правую дату нужно увеличивать на одну секунду, т.к. подрезались миллисекунды
        self.get_logs_periods_sql = """
            select min(modified),
                   max(modified) + interval '1 second',
                   row_batched
            from (
                select row_num,
                       ((row_num - 1) / {batch_size}) + 1 AS row_batched,
                       modified
                from (
                    select row_number() over (order by modified) as row_num,
                           modified
                    from (
                        select *
                        from (
                        {ordered_rows}
                        ) as union_rows
                        order by modified
                    ) as ordered
                ) as numbered
            ) as batched
            group by row_batched
            order by row_batched;
            """

        self.ordered_rows_query = """
            select distinct date_trunc('second', modified) as modified
            from {table_name}
            where modified between '{period_started_at}' and '{period_ended_at}'
            """

    def generate(self) -> list:
        """Генерирует список данных для формирования команд для экспорта данных РВД."""
        params_for_commands = []

        for entity in self.entities:
            ordered_rows_queries_sql = self.ordered_rows_query.format(
                table_name=entity.main_model_enum.model._meta.db_table,
                period_started_at=self.period_started_at.strftime(DATE_FORMAT),
                period_ended_at=self.period_ended_at.strftime(DATE_FORMAT),
            )

            temp_get_logs_periods_sql = self.get_logs_periods_sql.format(
                batch_size=self.batch_size,
                ordered_rows=ordered_rows_queries_sql,
            )

            with connection.cursor() as cursor:
                cursor.execute(temp_get_logs_periods_sql)
                rows = cursor.fetchall()

            for period_started_at, period_ended_at, _ in rows:
                params_for_commands.append(
                    {
                        'period_started_at': period_started_at,
                        'period_ended_at': period_ended_at,
                        'entity': entity.key,
                        'generation_id': self.generation_id,
                    },
                )

        return params_for_commands
