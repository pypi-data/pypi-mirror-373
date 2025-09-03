from educommon.utils.enums import (
    HashGostFunctionVersion,
)


REGIONAL_DATA_MART_INTEGRATION_COLLECTING_DATA = 'regional_data_mart_integration_collecting_data'
REGIONAL_DATA_MART_INTEGRATION_EXPORTING_DATA = 'regional_data_mart_integration_exporting_data'

# Формат даты. Используется для выгрузки
DATE_FORMAT = '%Y-%m-%d'

# Формат даты/времени. Для выгрузки не используется (в выгрузке ISO формат)
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

# Формат даты/времени. Для выгрузки
EXPORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

LOGS_DELIMITER = '    '

HASH_ALGORITHM = HashGostFunctionVersion.GOST12_512

BATCH_SIZE = 5000

CHUNK_MAX_VALUE = 100000
"""Максимальное значение для размера чанка при сборе данных РВД.
Ограничение 100000 предотвращает чрезмерное потребление памяти и блокировку БД
при обработке больших объемов данных в одном батче."""

SPLIT_BY_QUANTITY_MAX_VALUE = 366
"""Максимальное значение для размера подпериода при временном разделении данных."""

ACADEMIC_YEAR = {
    'start_day': 1,
    'start_month': 9,
    'end_day': 31,
    'end_month': 8,
}

TASK_QUEUE_NAME = 'RDM'
FAST_TRANSFER_TASK_QUEUE_NAME = 'RDM_FAST'
LONG_TRANSFER_TASK_QUEUE_NAME = 'RDM_LONG'
