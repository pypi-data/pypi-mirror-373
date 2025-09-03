from datetime import (
    date,
    datetime,
)
from typing import (
    Any,
)

from django.conf import (
    settings,
)

from edu_function_tools.helpers import (
    EduFunctionHelper,
    EduRunnerHelper,
)
from educommon.utils.conversion import (
    str_without_control_chars,
)
from educommon.utils.crypto import (
    HashData,
)

from edu_rdm_integration.core.consts import (
    DATE_FORMAT,
    EXPORT_DATETIME_FORMAT,
    HASH_ALGORITHM,
)
from edu_rdm_integration.stages.export_data.functions.base.caches import (
    BaseExportDataFunctionCacheStorage,
    BaseExportDataRunnerCacheStorage,
)


class BaseExportDataRunnerHelper(EduRunnerHelper):
    """Базовый класс помощников ранеров функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    def _prepare_cache_class(self) -> type[BaseExportDataRunnerCacheStorage]:
        """Возвращает класс кеша помощника ранера."""
        return BaseExportDataRunnerCacheStorage


class BaseExportDataFunctionHelper(EduFunctionHelper):
    """Базовый класс помощников функций выгрузки данных для интеграции с "Региональная витрина данных"."""

    cryptographer = HashData(hash_algorithm=HASH_ALGORITHM)

    @classmethod
    def _prepare_str_field(cls, field_value: str, *, required: bool) -> str:
        # Очистка строковых полей от управляющих символов
        return str_without_control_chars(field_value)

    @classmethod
    def _prepare_datetime_field(cls, field_value: datetime, *, required: bool) -> str:
        # Дату/время передаём в формате: YYYY-MM-DD hh:mm:ss
        return field_value.strftime(EXPORT_DATETIME_FORMAT)

    @classmethod
    def _prepare_date_field(cls, field_value: date, *, required: bool) -> str:
        return field_value.strftime(DATE_FORMAT)

    @classmethod
    def _prepare_common_field(cls, field_value: Any, *, required: bool) -> str:
        return str(field_value if field_value is not None else '')

    @classmethod
    def _surround_with_quotes(cls, field_value: str, *, required: bool) -> str:
        has_value = not (field_value is None or field_value == '')
        if not required and not has_value:
            return ''

        return f'"{field_value}"'

    @classmethod
    def prepare_record(
        cls,
        entity_instance,
        ordered_fields: tuple[str, ...],
        primary_key_fields: set[str],
        foreign_key_fields: set[str],
        required_fields: set[str],
        hashable_fields: set[str],
        ignore_prefix_fields: set[str],
    ) -> list[str]:
        """Формирование списка строковых значений полей."""
        field_values = []
        key_fields = primary_key_fields.union(foreign_key_fields)
        add_prefix_fields = key_fields.difference(ignore_prefix_fields)

        for field in ordered_fields:
            required = field in required_fields
            field_value = getattr(entity_instance, field)

            if isinstance(field_value, str):
                field_value = cls._prepare_str_field(field_value, required=required)
            elif isinstance(field_value, datetime):
                field_value = cls._prepare_datetime_field(field_value, required=required)
            elif isinstance(field_value, date):
                field_value = cls._prepare_date_field(field_value, required=required)
            else:
                field_value = cls._prepare_common_field(field_value, required=required)

            if field_value and field in add_prefix_fields:
                field_value = f'{settings.RDM_EXPORT_ENTITY_ID_PREFIX}-{field_value}'

            if field_value and field in hashable_fields:
                field_value = cls.cryptographer.get_hash(field_value)

            # Экранирование двойных кавычек
            field_value = field_value.replace('"', '""')

            field_value = cls._surround_with_quotes(field_value, required=required)

            field_values.append(field_value)

        return field_values

    def _prepare_cache_class(self) -> type[BaseExportDataFunctionCacheStorage]:
        """Возвращает класс кеша помощника функции."""
        return BaseExportDataFunctionCacheStorage
