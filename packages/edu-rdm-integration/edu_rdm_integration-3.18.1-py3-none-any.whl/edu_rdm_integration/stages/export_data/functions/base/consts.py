from educommon.integration_entities.enums import (
    EntityLogOperation,
)


POST = 'POST'
# удаление еще не реализовано, ожидается информация от МинЦифры
DELETE = 'DELETE'

OPERATIONS_METHODS_MAP = {
    EntityLogOperation.CREATE: POST,
    EntityLogOperation.UPDATE: POST,
    EntityLogOperation.DELETE: POST,
}

OPERATIONS_URLS_MAP = {
    EntityLogOperation.CREATE: 'upload',
    EntityLogOperation.UPDATE: 'upload',
    EntityLogOperation.DELETE: 'delete',
}


TEST_DIR = 'test_data'
