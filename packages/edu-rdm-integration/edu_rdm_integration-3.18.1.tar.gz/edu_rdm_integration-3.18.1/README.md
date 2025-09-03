# Проект "Интеграция с Региональной витриной данных (РВД)"

Для интеграции с Региональной витриной данных был выделен отдельный пакет для использования его компонентов в различных 
продуктах. 

На текущий момент интеграция реализуется в рамках проектов Электронный детский сад (ЭДС), Электронная школа (ЭШ) и 
Электронный колледж (ЭК).

## Описание концепции

Со стороны Минцифры предоставляется спецификация (ЕФТТ) с требованиями по формату и механизму выгрузки данных. 

Выбрана модель промежуточного хранения данных на стороне продукта, которые подлежат выгрузке. При помощи такого подхода,
можно обеспечить формирование не хранящихся в продукте данных и дальнейшее их обновление и удаление. Упрощается процесс 
поиска ошибок в данных, т.к. можно явно определить, в каких записях находятся ошибки и далее анализировать существующие 
данные в продуктах или функционал по формированию данных.

## Принцип работы

Весь процесс разделен на сбор, выгрузку данных в файлы, отправку файлов. Выделяются следующие понятия:

Модель продукта
: Django-модель находящаяся в самом продукте. При помощи нее производится накапливание пользовательских данных;

Модель РВД
: Django-модель находящаяся в пакете РВД продукта. Из моделей РВД формируется схема БД, позволяющая хранить данные для 
дальнейшей выгрузки в нормализованном виде;

Сущность РВД
: Описание формата выгрузки данных в РВД в виде dataclass-а. Хранит в себе описание первичных, внешних ключей, 
обязательность и порядок полей.

На этапе сбора данных производится формирование данных моделей РВД на основе данных моделей продуктов. Существуют так 
называемые расчетные модели, для которых данные рассчитываются в процессе сбора.

Стоит обратить внимание, что сущности РВД могут содержать в себе данные из нескольких моделей РВД.

Очереди для периодических задач сборки и выгрузки данных
: Важно учитывать, что с версии пакета 3.6 вводится две новые очереди и соответствущие этим очередям периодические задачи
сбора и выгрузки данных. Очередь для сущности указывается в реестре "Сущности для сбора и экспорта данных" - по умолчанию все
сущности относятся к основной очереди.
Итого - нужно настроить три очереди для работы.

 - "Быстрая" очередь - RDM_FAST - для сущностей, по которым данные должны отдаваться каждые 5/10/15 минут по требованиям 
витрины. Периодическая задача - TransferLatestEntitiesDataFastPeriodicTask.
 - Основная очередь (та которая была до версии 3.6) - RDM- ля всех сущностей по умолчанию.
Периодическая задача - TransferLatestEntitiesDataFastPeriodicTask.
 - "Долгая" очередь - RDM_LONG - для сущностей по которым идет долгий сбор, например для расчетных сущностей. 
Периодическая задача - TransferLatestEntitiesDataLongPeriodicTask.

## Требования к окружению

Для работы требуется Python >=3.9. Так же в зависимостях есть внутренние пакеты:

- educommon;
- function-tools;
- m3-db-utils;
- uploader-client.

Версии всех пакетов уточнены в файлах с зависимостями.

## Разворачивание

Перед внедрением пакета в проект, необходимо убедиться, что:

- В проекте используется логирование из educommon;
- В проект внедрен function-tools;
- В проект внедрен m3-db-utils;
- В проект внедрен uploader-client. 

## Подключение в settings.py

INSTALLED_APPS = (
    ...
    'edu_rdm_integration',
    'edu_rdm_integration.collect_and_export_data',
    'edu_rdm_integration.core.registry',
    'edu_rdm_integration.rdm_entities',
    'edu_rdm_integration.rdm_models',
    'edu_rdm_integration.pipelines.cleanup_outdated_data',
    'edu_rdm_integration.pipelines.transfer',
    'edu_rdm_integration.stages.collect_data',
    'edu_rdm_integration.stages.export_data',
    'edu_rdm_integration.stages.service',
    'edu_rdm_integration.stages.upload_data',
    'edu_rdm_integration.stages.upload_data.uploader_log',
    'edu_rdm_integration.stages.collect_data.registry',
    'edu_rdm_integration.stages.export_data.registry',
    ...
)

## Параметры конфигурационного файла

В разных проектах существуют различные способы добавления настроек, где-то через плагины, где-то напрямую в settings.py.
Будет рассмотрен подход указания настроек в settings.py и указания параметров в конфигурационном файле.

Для возможности конфигурирования необходимо проделать ряд действий:

- Определение значений по умолчанию настроек в settings.py:
    ```
    PROJECT_DEFAULT_CONFIG.update({
        # Настройки РВД
        ('rdm_general', 'EXPORT_ENTITY_ID_PREFIX'): '', # Дефолтное значение нужно изменить на специфическое системе
        ('rdm_general', 'COLLECT_CHUNK_SIZE'): 500,
        ('rdm_general', 'EXPORT_CHUNK_SIZE'): 500,
        ('rdm_general', 'UPLOAD_QUEUE_MAX_SIZE'): 500_000_000,
        ('rdm_general', 'RDM_MENU_ITEM'): False,
        ('rdm_transfer_task', 'MINUTE'): '0',
        ('rdm_transfer_task', 'HOUR'): '*/4',
        ('rdm_transfer_task', 'DAY_OF_WEEK'): '*',
        ('rdm_transfer_task', 'LOCK_EXPIRE_SECONDS'): 21600,
        ('rdm_transfer_task_fast', 'MINUTE'): '*/5',
        ('rdm_transfer_task_fast', 'HOUR'): '*',
        ('rdm_transfer_task_fast', 'DAY_OF_WEEK'): '*',
        ('rdm_transfer_task_fast', 'LOCK_EXPIRE_SECONDS'): 1800,
        ('rdm_transfer_task_long', 'MINUTE'): '0',
        ('rdm_transfer_task_long', 'HOUR'): '*/6',
        ('rdm_transfer_task_long', 'DAY_OF_WEEK'): '*',
        ('rdm_transfer_task_long', 'LOCK_EXPIRE_SECONDS'): 28800,
        ('rdm_upload_data_task', 'MINUTE'): '0',
        ('rdm_upload_data_task', 'HOUR'): '*/2',
        ('rdm_upload_data_task', 'DAY_OF_WEEK'): '*',
        ('rdm_upload_data_task', 'LOCK_EXPIRE_SECONDS'): 7200,
        ('rdm_upload_data_task', 'EXPORT_STAGES'): 500,
        ('rdm_upload_status_task', 'MINUTE'): '*/30',
        ('rdm_upload_status_task', 'HOUR'): '*',
        ('rdm_upload_status_task', 'DAY_OF_WEEK'): '*',
        ('rdm_upload_status_task', 'LOCK_EXPIRE_SECONDS'): 7200,
        ('rdm_check_suspend_task', 'MINUTE'): '*/10',
        ('rdm_check_suspend_task', 'HOUR'): '*',
        ('rdm_check_suspend_task', 'DAY_OF_WEEK'): '*',
        ('rdm_check_suspend_task', 'LOCK_EXPIRE_SECONDS'): 7200,
        ('rdm_check_suspend_task', 'STAGE_TIMEOUT'): 120,
        # Настройки очереди отправки
        ('rdm_redis', 'REDIS_HOST'): 'localhost',
        ('rdm_redis', 'REDIS_PORT'): 6379,
        ('rdm_redis', 'REDIS_DB'): 1,
        ('rdm_redis', 'REDIS_PASSWORD'): '',
        ('rdm_redis', 'REDIS_CACHE_TIMEOUT_SECONDS'): 7200,
        ('uploader_client', 'URL'): 'http://localhost:8090',
        ('uploader_client', 'DATAMART_NAME'): '',
        ('uploader_client', 'REQUEST_RETRIES'): 10,
        ('uploader_client', 'REQUEST_TIMEOUT'): 10,
        ('uploader_client', 'ENABLE_REQUEST_EMULATION'): False,
        ('uploader_client', 'RESPONSE_FILE_STATUS'): 'success',
        ('uploader_client', 'USE_PROXY_API'): False,
        ('uploader_client', 'USERNAME'): '',
        ('uploader_client', 'PASSWORD'): '',
        ('uploader_client', 'ORGANIZATION_OGRN'): '',
        ('uploader_client', 'INSTALLATION_NAME'): '',
        ('uploader_client', 'INSTALLATION_ID'): '',
    })  
    ```
- Получение значений настроек из конфигурационного файла в settings.py:

    ```
    # Ссылка на каталог с файлами для загрузки
    UPLOADS = 'uploads'
  
    # =============================================================================
    # Интеграция с Региональной витриной данных (РВД)
    # =============================================================================
    
    # Префикс идентификаторов записей сущностей специфический для продукта
    RDM_EXPORT_ENTITY_ID_PREFIX = conf.get('rdm_general', 'EXPORT_ENTITY_ID_PREFIX') 
  
    # Количество записей моделей ЭШ обрабатываемых за одну итерацию сбора данных
    RDM_COLLECT_CHUNK_SIZE = conf.get_int('rdm_general', 'COLLECT_CHUNK_SIZE')
    
    # Количество записей моделей обрабатываемых за одну итерацию экспорта данных
    RDM_EXPORT_CHUNK_SIZE = conf.get_int('rdm_general', 'EXPORT_CHUNK_SIZE')
  
    # Количество не экспортированных записей моделей обрабатываемых за одну итерацию обновления поля modified
    RDM_UPDATE_NON_EXPORTED_CHUNK_SIZE = conf.get_int('rdm_general', 'UPDATE_NON_EXPORTED_CHUNK_SIZE')
  
    # Объем очереди файлов в витрину (в байтах) - по умолчанию 512 Мбайт
    RDM_UPLOAD_QUEUE_MAX_SIZE = conf.get_int('rdm_general', 'UPLOAD_QUEUE_MAX_SIZE')
  
    # Пункт меню "Региональная витрина данных" - Спрятать (False) / Отображать (True)
    RDM_MENU_ITEM = conf.get_bool('rdm_general', 'RDM_MENU_ITEM')
    
    # Настройка запуска периодической задачи выгрузки данных:
    RDM_TRANSFER_TASK_MINUTE = conf.get('rdm_transfer_task', 'MINUTE')
    RDM_TRANSFER_TASK_HOUR = conf.get('rdm_transfer_task', 'HOUR')
    RDM_TRANSFER_TASK_DAY_OF_WEEK = conf.get('rdm_transfer_task', 'DAY_OF_WEEK')
    RDM_TRANSFER_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_transfer_task', 'LOCK_EXPIRE_SECONDS')
    
    # Настройка запуска периодической задачи выгрузки данных - быстрая очередь:
    RDM_FAST_TRANSFER_TASK_MINUTE = conf.get('rdm_transfer_task_fast', 'MINUTE')
    RDM_FAST_TRANSFER_TASK_HOUR = conf.get('rdm_transfer_task_fast', 'HOUR')
    RDM_FAST_TRANSFER_TASK_DAY_OF_WEEK = conf.get('rdm_transfer_task_fast', 'DAY_OF_WEEK')
    RDM_FAST_TRANSFER_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_transfer_task_fast', 'LOCK_EXPIRE_SECONDS')
    
    # Настройка запуска периодической задачи выгрузки данных - долгая очередь расчетных моделей:
    RDM_LONG_TRANSFER_TASK_MINUTE = conf.get('rdm_transfer_task_long', 'MINUTE')
    RDM_LONG_TRANSFER_TASK_HOUR = conf.get('rdm_transfer_task_long', 'HOUR')
    RDM_LONG_TRANSFER_TASK_DAY_OF_WEEK = conf.get('rdm_transfer_task_long', 'DAY_OF_WEEK')
    RDM_LONG_TRANSFER_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_transfer_task_long', 'LOCK_EXPIRE_SECONDS')
  
    # Настройка запуска периодической задачи поиска зависших этапов экспорта:
    RDM_CHECK_SUSPEND_TASK_MINUTE = conf.get('rdm_check_suspend_task', 'MINUTE')
    RDM_CHECK_SUSPEND_TASK_HOUR = conf.get('rdm_check_suspend_task', 'HOUR')
    RDM_CHECK_SUSPEND_TASK_DAY_OF_WEEK = conf.get('rdm_check_suspend_task', 'DAY_OF_WEEK')
    RDM_CHECK_SUSPEND_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_check_suspend_task', 'LOCK_EXPIRE_SECONDS')
    RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT = conf.get_int('rdm_check_suspend_task', 'STAGE_TIMEOUT')

    # Настройка запуска периодической задачи отправки файлов с данными РВД
    RDM_UPLOAD_DATA_TASK_MINUTE = conf.get('rdm_upload_data_task', 'MINUTE')
    RDM_UPLOAD_DATA_TASK_HOUR = conf.get('rdm_upload_data_task', 'HOUR')
    RDM_UPLOAD_DATA_TASK_DAY_OF_WEEK = conf.get('rdm_upload_data_task', 'DAY_OF_WEEK')
    RDM_UPLOAD_DATA_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_upload_data_task', 'LOCK_EXPIRE_SECONDS')
    # Количество подэтапов для обработки в периодической задаче отправки данных
    RDM_UPLOAD_DATA_TASK_EXPORT_STAGES = conf.get_int('rdm_upload_data_task', 'EXPORT_STAGES')
    
    # Настройка запуска периодической задачи статуса загрузки данных в витрину:
    RDM_UPLOAD_STATUS_TASK_MINUTE = conf.get('rdm_upload_status_task', 'MINUTE')
    RDM_UPLOAD_STATUS_TASK_HOUR = conf.get('rdm_upload_status_task', 'HOUR')
    RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK = conf.get('rdm_upload_status_task', 'DAY_OF_WEEK')
    RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_upload_status_task', 'LOCK_EXPIRE_SECONDS')
  
    # Настройка очереди Redis для формирования файлов РВД.
    RDM_REDIS_HOST = conf.get('rdm_redis', 'REDIS_HOST')
    RDM_REDIS_PORT = conf.get('rdm_redis', 'REDIS_PORT')
    RDM_REDIS_DB = conf.get('rdm_redis', 'REDIS_DB')
    RDM_REDIS_PASSWORD = conf.get('rdm_redis', 'REDIS_PASSWORD')    
    # Таймаут для сохранения параметров в общем кеш.
    RDM_REDIS_CACHE_TIMEOUT_SECONDS = conf.get_int('rdm_redis', 'REDIS_CACHE_TIMEOUT_SECONDS')
  
    # Загрузка данных в Региональную витрину данных (РВД)
    # Адрес витрины (schema://host:port)
    RDM_UPLOADER_CLIENT_URL = conf.get('uploader_client', 'URL')    
    # Мнемоника Витрины
    RDM_UPLOADER_CLIENT_DATAMART_NAME = conf.get('uploader_client', 'DATAMART_NAME')    
    # Количество повторных попыток запроса
    RDM_UPLOADER_CLIENT_REQUEST_RETRIES = conf.get_int('uploader_client', 'REQUEST_RETRIES')    
    # Таймаут запроса, сек
    RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT = conf.get_int('uploader_client', 'REQUEST_TIMEOUT')    
    # Включить эмуляцию отправки запросов
    RDM_UPLOADER_CLIENT_ENABLE_REQUEST_EMULATION = conf.get_bool('uploader_client', 'ENABLE_REQUEST_EMULATION')
    # Установить тип ответа витрины при проверке статуса отправленного файла
    RDM_RESPONSE_FILE_STATUS = conf.get('uploader_client', 'RESPONSE_FILE_STATUS')
    # Использование Proxy API
    RDM_UPLOADER_CLIENT_USE_PROXY_API = conf.get_bool('uploader_client', 'USE_PROXY_API')
    # Имя пользователя IAM
    RDM_UPLOADER_CLIENT_USERNAME = conf.get('uploader_client', 'USERNAME')
    # Пароль пользователя IAM
    RDM_UPLOADER_CLIENT_PASSWORD = conf.get('uploader_client', 'PASSWORD')
    # ОГРН организации, в рамках которой развёрнута Витрина
    RDM_UPLOADER_CLIENT_ORGANIZATION_OGRN = conf.get('uploader_client', 'ORGANIZATION_OGRN')
    # Имя инсталляции в целевой Витрине
    RDM_UPLOADER_CLIENT_INSTALLATION_NAME = conf.get('uploader_client', 'INSTALLATION_NAME')
    # Идентификатор инсталляции в целевой Витрине
    RDM_UPLOADER_CLIENT_INSTALLATION_ID = conf.get('uploader_client', 'INSTALLATION_ID')  
  
    # Директория логов сбора данных, доступных для скачивания
    RDM_COLLECT_LOG_DIR = os.path.join('logs', 'rdm', 'collect')
    os.makedirs(os.path.join(MEDIA_ROOT, RDM_COLLECT_LOG_DIR), exist_ok=True)
    # Директория логов экспорта данных, доступных для скачивания
    RDM_EXPORT_LOG_DIR = os.path.join('logs', 'rdm', 'export')
    os.makedirs(os.path.join(MEDIA_ROOT, RDM_EXPORT_LOG_DIR), exist_ok=True)
    # Директория логов отправки данных в витрину, доступных для скачивания
    RDM_UPLOAD_LOG_DIR = os.path.join('logs', 'rdm', 'upload')
    os.makedirs(os.path.join(MEDIA_ROOT, RDM_UPLOAD_LOG_DIR), exist_ok=True)
    ```

Перечень настроек в settings.py указан в таблице ниже.

| Название настройки в settings                | Описание                                                                                                                           | Значение по умолчанию   |
|----------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| UPLOADS                                      | Основная директория в MEDIA, в которой будет создана директория edu_rdm_integration  для сохранения файлов для дальнейшей выгрузки | 500                     |
| RDM_EXPORT_ENTITY_ID_PREFIX                  | Префикс идентификаторов записей сущностей специфический для продукта                                                               |                         |
| RDM_COLLECT_CHUNK_SIZE                       | Количество записей моделей обрабатываемых за одну итерацию сбора данных                                                            | 500                     |
| RDM_EXPORT_CHUNK_SIZE                        | Количество записей моделей обрабатываемых за одну итерацию экспорта                                                                | 500                     |
| RDM_UPDATE_NON_EXPORTED_CHUNK_SIZE           | # Количество не экспортированных записей моделей обрабатываемых за одну итерацию обновления поля modified                          | 5000                    |
| RDM_UPLOAD_QUEUE_MAX_SIZE                    | Объем очереди файлов в витрину (в байтах).                                                                                         | 500_000_000             |
| RDM_MENU_ITEM                                | Отображение пункта меню Пункт меню "Региональная витрина данных"                                                                   | False                   |
| RDM_TRANSFER_TASK_MINUTE                     | Настройка запуска периодической задачи выгрузки данных. Минута                                                                     | '0'                     |
| RDM_TRANSFER_TASK_HOUR                       | Настройка запуска периодической задачи выгрузки данных. Час                                                                        | '*/4'                   |
| RDM_TRANSFER_TASK_DAY_OF_WEEK                | Настройка запуска периодической задачи выгрузки данных. День недели                                                                | '*'                     |
| RDM_TRANSFER_TASK_LOCK_EXPIRE_SECONDS        | Время по истечении которого, блокировка может быть снята (в секундах)                                                              | 21600                   |
| RDM_FAST_TRANSFER_TASK_MINUTE                | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. Минута                                                   | '*/5'                   |
| RDM_FAST_TRANSFER_TASK_HOUR                  | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. Час                                                      | '*'                     |
| RDM_FAST_TRANSFER_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. День недели                                              | '*'                     |
| RDM_FAST_TRANSFER_TASK_LOCK_EXPIRE_SECONDS   | Время по истечении которого, блокировка может быть снята (в секундах)                                                              | 1800                    |
| RDM_LONG_TRANSFER_TASK_MINUTE                | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. Минута                                                    | 0                       |
| RDM_LONG_TRANSFER_TASK_HOUR                  | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. Час                                                       | '*/6'                   |
| RDM_LONG_TRANSFER_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. День недели                                               | '*'                     |
| RDM_LONG_TRANSFER_TASK_LOCK_EXPIRE_SECONDS   | Время по истечении которого, блокировка может быть снята (в секундах)                                                              | 28800                   |
| RDM_CHECK_SUSPEND_TASK_MINUTE                | Настройка запуска периодической задачи поиска зависших этапов экспорта. Минута                                                     | */10                    |
| RDM_CHECK_SUSPEND_TASK_HOUR                  | Настройка запуска периодической задачи поиска зависших этапов экспорта. Час                                                        | *                       |
| RDM_CHECK_SUSPEND_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи поиска зависших этапов экспорта. День недели                                                | *                       |
| RDM_CHECK_SUSPEND_TASK_LOCK_EXPIRE_SECONDS   | Время по истечении которого, блокировка может быть снята (в секундах).                                                             | 7200                    |
| RDM_CHECK_SUSPEND_TASK_STAGE_TIMEOUT         | Дельта для определения зависшего подэтапа. Минута                                                                                  | 120                     |
| RDM_UPLOAD_DATA_TASK_MINUTE                  | Настройка запуска периодической задачи отправки файлов с данными РВД (минута).                                                     | '0'                     |
| RDM_UPLOAD_DATA_TASK_HOUR                    | Настройка запуска периодической задачи отправки файлов с данными РВД (час).                                                        | '*/2'                   |
| RDM_UPLOAD_DATA_TASK_DAY_OF_WEEK             | Настройка запуска периодической задачи отправки файлов с данными РВД (день недели).                                                | '*'                     |
| RDM_UPLOAD_DATA_TASK_LOCK_EXPIRE_SECONDS     | Время по истечении которого, блокировка может быть снята (в секундах).                                                             | 7200                    |
| RDM_UPLOAD_DATA_TASK_EXPORT_STAGES           | Количество подэтапов для обработки в периодической задаче отправки данных.                                                         | 500                     |
| RDM_UPLOAD_STATUS_TASK_MINUTE                | Настройка запуска периодической задачи статуса загрузки данных в витрину. Минута                                                   | '*/30'                  |
| RDM_UPLOAD_STATUS_TASK_HOUR                  | Настройка запуска периодической задачи статуса загрузки данных в витрину. Час                                                      | '*'                     |
| RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи статуса загрузки данных в витрину. День недели                                              | '*'                     |
| RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS   | Время по истечении которого, блокировка может быть снята (в секундах)                                                              | 3600                    |
| RDM_REDIS_HOST                               | Настройка очереди Redis для формирования файлов РВД (хост).                                                                        |                         |
| RDM_REDIS_PORT                               | Настройка очереди Redis для формирования файлов РВД (порт).                                                                        |                         |
| RDM_REDIS_DB                                 | Настройка очереди Redis для формирования файлов РВД (номер бд).                                                                    |                         |
| RDM_REDIS_PASSWORD                           | Настройка очереди Redis для формирования файлов РВД (пароль).                                                                      |                         |
| RDM_REDIS_CACHE_TIMEOUT_SECONDS              | Таймаут для сохранения параметров в общем кеш (секунды).                                                                           | 7200                    |
| RDM_UPLOADER_CLIENT_URL                      | Адрес витрины (schema://host:port)                                                                                                 | 'http://localhost:8090' |
| RDM_UPLOADER_CLIENT_DATAMART_NAME            | Мнемоника Витрины                                                                                                                  | 'test'                  |
| RDM_UPLOADER_CLIENT_REQUEST_RETRIES          | Количество повторных попыток запроса                                                                                               | 10                      |
| RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT          | Таймаут запроса, сек                                                                                                               | 10                      |
| RDM_UPLOADER_CLIENT_ENABLE_REQUEST_EMULATION | Включить эмуляцию отправки запросов                                                                                                | True                    |
| RDM_RESPONSE_FILE_STATUS                     | Установить тип ответа витрины при проверке статуса отправленного файла                                                             | 'success'               |
| RDM_UPLOADER_CLIENT_USE_PROXY_API            | Использование Proxy API                                                                                                            | False                   |
| RDM_UPLOADER_CLIENT_USERNAME                 | Имя пользователя IAM                                                                                                               |                         |
| RDM_UPLOADER_CLIENT_PASSWORD                 | Пароль пользователя IAM                                                                                                            |                         |
| RDM_UPLOADER_CLIENT_ORGANIZATION_OGRN        | ОГРН организации, в рамках которой развёрнута Витрина                                                                              |                         |
| RDM_UPLOADER_CLIENT_INSTALLATION_NAME        | Имя инсталляции в целевой Витрине                                                                                                  |                         |
| RDM_UPLOADER_CLIENT_INSTALLATION_ID          | Идентификатор инсталляции в целевой Витрине                                                                                        |                         |
| RDM_COLLECT_LOG_DIR                          | Директория логов сбора данных, доступных для скачивания                                                                            |                         |
| RDM_EXPORT_LOG_DIR                           | Директория логов экспорта данных, доступных для скачивания                                                                         |                         |
| RDM_UPLOAD_LOG_DIR                           | Директория логов отправки данных в витрину, доступных для скачивания                                                               |                         |

- В дефолтный конфиг проекта необходимо добавить:

    ```
    # Общие настройки интеграции с РВД
    [rdm_general]
    # Префикс идентификаторов записей сущностей специфический для продукта. Указывается в settings.py и не должен 
    # изменяться. Возможность изменения через конфигурационный файл оставлена для экстренных случаев.
    # EXPORT_ENTITY_ID_PREFIX = 
    # Количество записей моделей обрабатываемых за одну итерацию экспорта данных
    EXPORT_CHUNK_SIZE = 500
    # Количество записей моделей ЭШ обрабатываемых за одну итерацию сбора данных
    COLLECT_CHUNK_SIZE = 500
    # Количество не экспортированных записей моделей обрабатываемых за одну итерацию обновления поля modified
    UPDATE_NON_EXPORTED_CHUNK_SIZE = 5000
    # Объем очереди файлов в витрину (в байтах) - по умолчанию 512 Мбайт.
    UPLOAD_QUEUE_MAX_SIZE = 500000000
    # Отображение пункта меню "Региональная витрина данных"
    RDM_MENU_ITEM = False
    
    # Настройка запуска периодической задачи выгрузки данных
    [rdm_transfer_task]
    MINUTE=*/2
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS=21600
  
    [rdm_transfer_task_fast]
    MINUTE=*/2
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS = 1800

    [rdm_transfer_task_long]
    MINUTE=*/15
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS = 21600
    
    # Настройка запуска периодической задачи поиска зависших этапов экспорта
    [rdm_check_suspend_task]
    MINUTE=*/10
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS=7200
    # Дельта для определения зависшего подэтапа, мин
    STAGE_TIMEOUT=120
  
    # Настройка запуска периодической задачи отправки csv-файлов в витрину.
    [rdm_upload_data_task]
    MINUTE=*/2
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS = 7200
    EXPORT_STAGES = 500
    
    # Настройка запуска периодической задачи статуса загрузки данных в витрину
    [rdm_upload_status_task]
    MINUTE=*/2
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS=7200
  
    # Настройка очереди Redis для формирования файлов РВД.
    [rdm_redis]
    REDIS_HOST = localhost
    REDIS_PORT = 6379
    REDIS_DB = 1
    REDIS_PASSWORD = 
    # Таймаут для сохранения параметров в общем кеш.
    REDIS_CACHE_TIMEOUT_SECONDS = 7200
    
    [uploader_client]
    # Адрес витрины
    URL = http://localhost:8090
    # Мнемоника Витрины
    DATAMART_NAME = test
    # Количество повторных попыток запроса
    REQUEST_RETRIES = 10
    # Таймаут запроса, сек
    REQUEST_TIMEOUT = 10
    # Включить эмуляцию отправки запросов
    ENABLE_REQUEST_EMULATION = True
    # Использовать Proxy API
    USE_PROXY_API = False
    # Имя пользователя IAM
    USERNAME =
    # Пароль пользователя IAM
    PASSWORD =
    # ОГРН организации, в рамках которой развёрнута Витрина
    ORGANIZATION_OGRN =
    # Имя инсталляции в целевой Витрине
    INSTALLATION_NAME =
    # Идентификатор инсталляции в целевой Витрине
    INSTALLATION_ID =
    ```
На основе дефолтного конфига произвести конфигурирование приложений.

## Форматирование

Форматирование исходного кода осуществляется при помощи ruff. Ниже приведены команды для осуществления форматирования.

```bash
$ ruff format src/
$ ruff check --fix --unsafe-fixes src/
```

## Сборка и распространение

Сборка пакета производится при помощи [Job-а в Jenkins M3.build_dist](http://jenkins.py.bars.group/view/PY/job/M3.packages/job/M3.build_dist/).

Пакет выкладывается в глобальный [PYPI](https://pypi.org/project/edu-rdm-integration/) и во внутренний [Nexus](http://nexus.py.bars.group/#browse/browse:pypi-edu-private:edu-rdm-integration) 

## Документация

С документацией можно ознакомиться по ссылке http://docs.py.bars.group/edu-rdm-integration/
