from educommon.integration_entities.enums import (
    EntityLogOperation,
)


# Перечень отслеживаемых моделей и перечней полей по операциям лога. Расширяется в продуктах
MODEL_FIELDS_LOG_FILTER: dict[EntityLogOperation, dict[str, tuple]] = {
    EntityLogOperation.CREATE: {},
    EntityLogOperation.UPDATE: {},
    EntityLogOperation.DELETE: {},
}

# Маппинг операций логов моделей и сущностей по умолчанию
DEFAULT_ENTITY_LOG_OPERATION_MAP = {op: op for op in EntityLogOperation.values}
