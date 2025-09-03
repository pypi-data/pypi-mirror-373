# История изменений

Все изменения проекта должны быть отражены в этом файле.

Формат основан на [Keep a Changelog](http://keepachangelog.com/)
и проект следует [Семантическому версионированию](http://semver.org/).

## [x.y.z] - гггг-мм-дд

Здесь должно быть расширенное описание того, что было сделано, какие есть планы у команды по дальнейшему развитию.
Желательно будущие цели привязывать к конкретным задачам. Т.е. на каждую цель нужно поставить отдельную задачу и
отразить ее номер здесь.

### Добавлено

- [ПРОЕКТ-ZZZZ](https://jira.bars.group/browse/ПРОЕКТ-ZZZZ)
  PATCH Название задачи или изменения.

- [ПРОЕКТ-YYYY](https://jira.bars.group/browse/ПРОЕКТ-YYYY)
  MINOR Название задачи или изменения.

- [ПРОЕКТ-XXXX](https://jira.bars.group/browse/ПРОЕКТ-XXXX)
  MAJOR Название задачи или изменения.

### Изменено

### Исправлено

### Удалено


## [3.18.1] - 2025-09-02

Доработки модели перечисления RDMModelEnum для расширения функционала механизма зачистки устаревших данных моделей РВД.

### Добавлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Добавлена базовая модель для определения модели являющейся основной для сущности.
- 
- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Добавлен механизм расчета обратных связей для моделей в модели-перечислении RDMModelEnum.

### Изменено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Изменен алгоритм сортировки моделей с использованием ключей модели-перечисления RDMModelEnum.

### Исправлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  PATCH Исправлена ошибка регистрации сущностей.


## [3.18.0] - 2025-08-29

Добавлено новое приложение `edu_rdm_integration.pipelines.cleanup_outdated_data`, которое необходимо подключить в 
settings.py в установленные приложения.

Реализован механизм создания уборщиков устаревших данных моделей РВД. Их регистрация производится в модели-перечислении 
`RDMModelEnum` при вызове метода `extend` в параметре `outdated_data_cleaners`. Запуск уборщиков производится при помощи 
менеджера, который запускается в команде `rdm_cleanup_outdated_data`. Сама команда используется в качестве ночного 
скрипта. В менеджере производится обход всех зарегистрированных моделей РВД в модели-перечислении `RDMModelEnum`, при 
наличии уборщиков они запускаются.

Изменен алгоритм расчета порядкового номера элемента в модели-перечислении `RDMModelEnum`. Теперь, при расширении 
модели-перечислении производится перерасчет всех порядковых номеров уже зарегистрированных значений, кроме установленных
вручную. Порядковые номера определяются согласно нахождению в последовательности из моделей, отсортированных по 
зависимости между собой - от меньшей зависимости к большей. Такое поведение было достигнуто путем указания моделей в 
фиктивных внешних ключах.

Во всех регистрациях моделей РВД были убраны порядковые номера order_number для автоматического расчета значений. При 
миграции на данную версию, аналогичную работу будет необходимо проделать на продукте.

Повышены минимальные версии пакетов:
- educommon>=3.25.0;
- m3-db-utils>=0.7.0.

### Добавлено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR Топологическая сортировка моделей РВД согласно зависимости между собой.

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR Добавлена команда/ночной скрипт rdm_cleanup_outdated_data`.

### Изменено

- [EDUDEVOPS-94](https://jira.bars.group/browse/EDUDEVOPS-94)
  MINOR Установка значения order_number в элементах RDMModelEnum производится при добавлении в модель перечислении и 
    пересчитывается при добавлении новых значений.


## [3.17.0] - 2025-01-27

Добавлено предупреждение пользователя о недостаточности данных и новая зависимость m3-ui.

### Добавлено
  [EDUCLLG-7932](https://jira.bars.group/browse/EDUCLLG-7932)
  MINOR Добавлена зависимость `m3-ui>=2.2.122,<2.3` в `pyproject.toml`

### Изменено
  [EDUCLLG-7932](https://jira.bars.group/browse/EDUCLLG-7932)
  MINOR `generate` в `generators.py`: изменена логика - вместо создания пустых команд при отсутствии данных теперь возвращается предупреждение


## [3.16.2] - 2025-08-19

Перенес javascript логику из create-collect-command-win.js в collect-command-window.js т.к. темплейт был перекрыт.
Добавлена валидация начала периода < текущая дата и начало периода < конец периода сбора и экспорта данных.

### Добавлено

- [EDUKNDG-15671](https://jira.bars.group/browse/EDUKNDG-15671)
  PATCH Добавлена валидация полей начало и конец периода сбора и экспорта данных.

### Удалено

- [EDUKNDG-15671](https://jira.bars.group/browse/EDUKNDG-15671)
  PATCH Удален темплейт create-collect-command-win.js


## [3.16.1] - 2025-01-27

Улучшена валидация полей формы сбора данных, добавлена логика взаимозависимости полей batch_size и split_by,
оптимизирована производительность bulk_create операций.

### Добавлено

- Добавлен файл validators.js с валидаторами для полей формы
- Добавлен валидатор instituteIdsValidator для поля institute_ids
- Добавлен валидатор instituteCountValidator для поля institute_count
- Добавлен файл collect-command-window.js с JavaScript логикой для формы
- Добавлена логика взаимозависимости полей batch_size и split_by
- Добавлен параметр RDM_COLLECT_PROGRESS_BATCH_SIZE для настройки размера батча

### Изменено

- Поле institute_ids: добавлены label, max_length и client_id
- Поле institute_count: подключен валидатор instituteCountValidator
- Поле split_by: установлено editable=False для ограничения ввода только из списка
- Метод save_row в actions.py: заменена логика сохранения на bulk_create с настраиваемым batch_size
- Добавлена JavaScript логика для корректной проверки обязательности взаимозависимых полей

### Добавлены новые настройки

| Название настройки в settings     | Описание                                                                                | Значение по умолчанию |
|-----------------------------------|-----------------------------------------------------------------------------------------|-----------------------|
| RDM_COLLECT_PROGRESS_BATCH_SIZE   | Размер батча для bulk_create операций при сборе данных РВД.                             | 10000                 |

В settings.py:

- Добавить значение по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rmd_general', 'COLLECT_PROGRESS_BATCH_SIZE'): 10000,
        ...
    })
  ```

- Получить значение настройки из конфигурационного файла:
  ```
    # Размер батча для bulk_create операций при сборе данных РВД.
    COLLECT_PROGRESS_BATCH_SIZE = conf.get_int('rmd_general', 'COLLECT_PROGRESS_BATCH_SIZE')
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [rmd_general]
    # Размер батча для bulk_create операций при сборе данных РВД.
    COLLECT_PROGRESS_BATCH_SIZE = 10000
  ```


## [3.16.0] - 2025-08-13

Добавлена поддержка django 4.2

### Добавлено

- [EDUKNDG-15603](https://jira.bars.group/browse/EDUKNDG-15603)
  MINOR Поднять версию Django до 4.2.23


## [3.15.3] - 2025-08-12

### Добавлено

- [EDUKNDG-15671](https://jira.bars.group/browse/EDUKNDG-15671)
  PATCH Добавлена валидация максимальной даты и времени при формировании команд сбора и экспорта данных.

### Исправлено

- [EDUKNDG-15671](https://jira.bars.group/browse/EDUKNDG-15671)
  PATCH Исправлено определение границ периода при разбиении команд на интервалы или батчи.
  Первый/последний интервал теперь точно начинается/заканчивается с указанным пользователем даты и времени.


## [3.15.2] - 2025-08-07

Повышены минимальные версии educommon. В educommon==3.24.0 произведён переход на пакет pygost при расчёте хэш по ГОСТ 
в классе educommon.utils.crypto.HashData.

### Добавлено

- [EDUSCHL-23907](https://jira.bars.group/browse/EDUSCHL-23907)
  PATCH Повышены минимальные версии educommon до 3.24.0


## [3.15.1] - 2025-07-30

Повышены минимальные версии uploader-client и edu-function-tools

### Добавлено

- [EDUKNDG-15602](https://jira.bars.group/browse/EDUKNDG-15602)
  PATCH Повышены минимальные версии uploader-client до 0.3.0 и edu-function-tools до 0.2.0


## [3.15.0] - 2025-07-29

Добавлена поддержка django 4.1

### Добавлено

- [EDUKNDG-15602](https://jira.bars.group/browse/EDUKNDG-15602)
  MINOR Поддержка Django 4.1.13


## [3.13.1] - 2025-07-25

### Исправлено

- [EDUKNDG-15617](https://jira.bars.group/browse/EDUKNDG-15617)
  PATCH Исправление ошибки доступа к полям связанной модели после переименования.


## [3.13.0] - 2025-07-10

Выполнен переход с внутреннего пакета adapters с компонентами для адаптации библиотеки function-tools на
отдельный пакет edu-function-tools.

### Изменено

- [EDUDEVOPS-91](https://jira.bars.group/browse/EDUDEVOPS-91)
  MINOR Выполнено изменение импортов с edu_rdm_integration.adapters, function_tools на импорты аналогичных классов 
  из edu_function_tools.

### Удалено

- [EDUDEVOPS-91](https://jira.bars.group/browse/EDUDEVOPS-91)
  MINOR Удален внутренний пакет adapters с компонентами для адаптации библиотеки function-tools.


## [3.12.0] - 2025-07-07

Доработка механизма экспорта данных в РВД. Признак успешного экспорта проставляется только тем записям,
которые действительно попадают в файл экспорта. Скорректирована базовая функция экспорта BaseExportDataFunction и
добавлены базовые классы для тестов экспорта.

Для корректной работы, необходимо скорректировать сущности РВД (дата-классы, унаследованные от BaseEntity) - 
убрать поле id - сейчас оно является обязательным. Соответственно на стороне продуктов нужно доработать кеши экспорта - 
обязательно должно выгружаться поле id. 
Для корректного проставления экспорта для составных моделей или моделей, у которых id для витрины формируется 
динамически  - необходимо переопределить свойство  _models_unique_id - поле по которому будут фильтроваться записи на
проставление подэтапа

### Изменено

- [EDUSCHL-23347](https://jira.bars.group/browse/EDUSCHL-23347)
  MINOR Доработка механизма экспорта данных в РВД - изменена логика проставления экспорта в BaseExportDataFunction


## [3.11.4] - 2025-01-27

Улучшена валидация полей формы сбора данных, добавлена логика взаимозависимости полей batch_size и split_by,
оптимизирована производительность bulk_create операций.

### Добавлено

- Добавлен файл validators.js с валидаторами для полей формы
- Добавлен валидатор instituteIdsValidator для поля institute_ids
- Добавлен валидатор instituteCountValidator для поля institute_count
- Добавлен файл collect-command-window.js с JavaScript логикой для формы
- Добавлена логика взаимозависимости полей batch_size и split_by
- Добавлен параметр RDM_COLLECT_PROGRESS_BATCH_SIZE для настройки размера батча

### Изменено

- Поле institute_ids: добавлены label, max_length и client_id
- Поле institute_count: подключен валидатор instituteCountValidator
- Поле split_by: установлено editable=False для ограничения ввода только из списка
- Метод save_row в actions.py: заменена логика сохранения на bulk_create с настраиваемым batch_size
- Добавлена JavaScript логика для корректной проверки обязательности взаимозависимых полей

### Добавлены новые настройки

| Название настройки в settings     | Описание                                                                                | Значение по умолчанию |
|-----------------------------------|-----------------------------------------------------------------------------------------|-----------------------|
| RDM_COLLECT_PROGRESS_BATCH_SIZE   | Размер батча для bulk_create операций при сборе данных РВД.                             | 10000                 |

В settings.py:

- Добавить значение по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rmd_general', 'COLLECT_PROGRESS_BATCH_SIZE'): 10000,
        ...
    })
  ```

- Получить значение настройки из конфигурационного файла:
  ```
    # Размер батча для bulk_create операций при сборе данных РВД.
    COLLECT_PROGRESS_BATCH_SIZE = conf.get_int('rmd_general', 'COLLECT_PROGRESS_BATCH_SIZE')
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [rmd_general]
    # Размер батча для bulk_create операций при сборе данных РВД.
    COLLECT_PROGRESS_BATCH_SIZE = 10000
  ```

## [3.11.3] - 2025-07-25

### Исправлено

- [EDUKNDG-15617](https://jira.bars.group/browse/EDUKNDG-15617)
  PATCH Исправление ошибки доступа к полям связанной модели после переименования.


## [3.11.2] - 2025-07-08

Изменения в зависимостях между миграциями для составления корректной истории.

### Изменено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Изменения в зависимостях между миграциями для составления корректной истории.


## [3.11.1] - 2025-07-04

Изменения в зависимостях между миграциями для составления корректной истории.

### Изменено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Изменения в зависимостях между миграциями для составления корректной истории.


## [3.11.0] - 2025-07-03

Добавлена поддержка django 4.0. Произведено переименование моделей, исправлены проблемы с миграциями.

Для корректной работы, необходимо удалить из истории миграций следующие записи перед раскаткой миграций
```
delete from django_migrations
where app = 'edu_rdm_integration_transfer_pipeline'
    or app = 'edu_rdm_integration_entities'
    or app = 'edu_rdm_integration_models'
    or app = 'edu_rdm_integration_collect_data_stage'
    or app = 'edu_rdm_integration_export_data_stage'
    or app = 'edu_rdm_integration_upload_data_stage';
```
Миграции указанных приложений изменяют только состояние представления БД, без изменений в самой БД.

### Добавлено

- [EDUKNDG-14483](https://jira.bars.group/browse/EDUKNDG-14483)
  MINOR Поднять версию Django до 4.0.10

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Переименованы модели.


## [3.10.4] - 2025-07-01

Исправление получения значений настроек RDM_TRANSFER_TASK_LOCK_EXPIRE_SECONDS, 
RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS, RDM_CHECK_SUSPEND_TASK_LOCK_EXPIRE_SECONDS в README.md.

### Исправлено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Исправлено получение значения настроек в README.md.


## [3.10.3] - 2025-07-01

Заменен битый импорт, внесены правки в README.md.

### Исправлено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Исправлено название настройки RDM_UPLOAD_STATUS_TASK_LOCK_EXPIRE_SECONDS в README.md.

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Исправление битого импорта OPERATIONS_METHODS_MAP.


## [3.10.2] - 2025-06-30

Удален отладочный код, внесены правки в README.md.

### Исправлено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Добавлено приложение edu_rdm_integration.collect_and_export_data в подключаемые приложения.

### Удалено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Отладочный код.


## [3.10.1] - 2025-06-28

Восстановление исходного состояния миграций для совместимости.

### Исправлено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Восстановление исходного состояния миграций для совместимости.


## [3.10.0] - 2025-06-23

Приведение кодовой базы к требованиям прохождения всех проверок ruff. Изменение структуры проекта. В INSTALLED_APPS 
должны быть добавлены:
```
INSTALLED_APPS = (
    'edu_rdm_integration',
    'edu_rdm_integration.core.registry',
    'edu_rdm_integration.rdm_entities',
    'edu_rdm_integration.rdm_models',
    'edu_rdm_integration.pipelines.transfer',
    'edu_rdm_integration.stages.collect_data',
    'edu_rdm_integration.stages.export_data',
    'edu_rdm_integration.stages.service',
    'edu_rdm_integration.stages.upload_data',
    'edu_rdm_integration.stages.upload_data.uploader_log',
    'edu_rdm_integration.stages.collect_data.registry',
    'edu_rdm_integration.stages.export_data.registry',
)
```
Изменения влекут за собой исправления импортов, т.к. компоненты были перенесены в новую структуру.

Необходимо добавить параметр, если требуется отображать пункт меню `Региональная витрина данных` 
```
[rdm_general]
...
RDM_MENU_ITEM = True
...
```

Произведено удаление механизма установки значений параметров интеграции по умолчанию. Это сделано для исключения ошибок 
при конфигурировании интеграции. Необходимо проверить все настройки на их наличие в settings.py. 

### Изменено

- [EDUDEVOPS-88](https://jira.bars.group/browse/EDUDEVOPS-88)
  PATCH Приведение кодовой базы к требованиям прохождения всех проверок ruff.


## [3.9.2] - 2025-06-16

Ограничена длина описания асинхронных задач при экспорте сущностей до максимального количества символов 
допустимых в поле.

### Исправлено

- [EDUSCHL-23636](https://jira.bars.group/browse/EDUSCHL-23636)
  PATCH Ошибка проставления описания в задачу сбора-экспорта РВД


## [3.9.1] - 2025-05-30

Доработан миксин EntityEnumRegisterMixin: атрибут additional_model_enums по умолчанию ().

### Изменено

- [EDUKNDG-15489](https://jira.bars.group/browse/EDUKNDG-15489)
  PATCH Доработан метод get_additional_model_enums.


## [3.9.0] - 2025-05-22

### Добавлено

- [EDUKNDG-15430](https://jira.bars.group/browse/EDUKNDG-15430)
  MAJOR Из проектов вынесен UI в общий пакет (Сбор данных моделей РВД и Экспорт данных сущностей РВД).


## [3.8.1] - 2025-05-20

Доработка журнала логов РВД.

### Добавлено

- [EDUKNDG-14575](https://jira.bars.group/browse/EDUKNDG-14575)
  PATCH Добавлена сортировка в "Журнал логов РВД" по полю "Код статуса загрузки".
  PATCH Добавлена фильтрация в "Журнал логов РВД" по полям "Результат", "Код статуса загрузки".

### Изменено

- [EDUKNDG-14575](https://jira.bars.group/browse/EDUKNDG-14575)
  PATCH Видимость "Журнал логов РВД" в пуске зависит от параметра RDM_MENU_ITEM.

### Удалено

- [EDUKNDG-14575](https://jira.bars.group/browse/EDUKNDG-14575)
  PATCH Удалён UploaderLogListWindow, настройка пагинации перенесена в UploaderLogPack.configure_grid


## [3.8.0] - 2025-05-15

Реализован функционал фильтрации объектов перед сохранением, позволяющий исключать неизменённые данные из операции 
записи. Это позволяет снизить нагрузку на систему и ускорить выполнение функций сбора, особенно при работе с большими 
объёмами данных. 

Для этого создан миксин FilteredSaveEntitiesFunctionMixin, который может быть использован в функциях сбора для 
реализации общей логики фильтрации до сохранения. Также обеспечена гибкость через параметры _ignored_fields 
и _filtered_operations.

### Добавлено

- [EDUSCHL-23441](https://jira.bars.group/browse/EDUSCHL-23441)
  MINOR Реализован миксин FilteredSaveEntitiesFunctionMixin для использования в функциях сбора позволяющий исключать 
  неизмененные объекты перед сохранением.


## [3.7.1] - 2025-05-14

Добавлено описание в README.md по поднятию версии до 3.3.0, 3.3.1, 3.4.2

### Добавлено

- [EDUSCHL-23121](https://jira.bars.group/browse/EDUSCHL-23121)
  PATCH Добавлено описание в README.md


## [3.7.0] - 2025-05-12

### Удалено

- [EDUSCHL-23121](https://jira.bars.group/browse/EDUSCHL-23121)
  MINOR Удалена неиспользуемая модель UploadDataCommand


## [3.6.0] - 2025-04-19

Вводится две новые очереди и соответсвущие этим очередям периодические задачи
сбора и выгрузки данных. Очередь для сущности указывается в реестре "Сущности для сбора и экспорта данных" 
- по умолчанию все сущности относятся к основной очереди.
Итого - нужно настроить три очереди для работы.

 - "Быстрая" очередь - RDM_FAST - для сущностей, по которым данные должны отдаваться каждые 5/10/15 минут по требованиям 
витрины. Периодическая задача - TransferLatestEntitiesDataFastPeriodicTask.
 - Основная очередь (та которая была до версии 3.6) - RDM- ля всех сущностей по умолчанию.
Периодическая задача - TransferLatestEntitiesDataFastPeriodicTask.
 - "Долгая" очередь - RDM_LONG - для сущностей по которым идет долгий сбор, например для расчетных сущностей. 
Периодическая задача - TransferLatestEntitiesDataLongPeriodicTask.

Добавлены новые настройки:

| Название настройки в settings              | Описание                                                                               | Значение по умолчанию |
|--------------------------------------------|----------------------------------------------------------------------------------------|-----------------------|
| RDM_FAST_TRANSFER_TASK_MINUTE              | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. Минута       | '*/5'                 |
| RDM_FAST_TRANSFER_TASK_HOUR                | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. Час          | '*'                   |
| RDM_FAST_TRANSFER_TASK_DAY_OF_WEEK         | Настройка запуска периодической задачи (быстрая очередь) выгрузки данных. День недели  | '*'                   |
| RDM_FAST_TRANSFER_TASK_LOCK_EXPIRE_SECONDS | Время по истечении которого, блокировка может быть снята (в секундах)                  | 1800                  |
| RDM_LONG_TRANSFER_TASK_MINUTE              | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. Минута        | 0                     |
| RDM_LONG_TRANSFER_TASK_HOUR                | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. Час           | '*/6'                 |
| RDM_LONG_TRANSFER_TASK_DAY_OF_WEEK         | Настройка запуска периодической задачи (долгая очередь) выгрузки данных. День недели   | '*'                   |
| RDM_LONG_TRANSFER_TASK_LOCK_EXPIRE_SECONDS | Время по истечении которого, блокировка может быть снята (в секундах)                  | 28800                 |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rdm_transfer_task_fast', 'MINUTE'): '*/5',
        ('rdm_transfer_task_fast', 'HOUR'): '*',
        ('rdm_transfer_task_fast', 'DAY_OF_WEEK'): '*',
        ('rdm_transfer_task_fast', 'LOCK_EXPIRE_SECONDS'): 1800,
        ('rdm_transfer_task_long', 'MINUTE'): '0',
        ('rdm_transfer_task_long', 'HOUR'): '*/6',
        ('rdm_transfer_task_long', 'DAY_OF_WEEK'): '*',
        ('rdm_transfer_task_long', 'LOCK_EXPIRE_SECONDS'): 28800,
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
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
  ```

В дефолтный конфиг проекта необходимо добавить:

  ```
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
  ```

### Добавлено

- [EDUSCHL-23348](https://jira.bars.group/browse/EDUSCHL-23348)
  MINOR Добавлено две дополнительные очереди для сбора и выгрузки данных РВД и соответствующие периодические 
  задачи TransferLatestEntitiesDataFastPeriodicTask и TransferLatestEntitiesDataLongPeriodicTask. Доработан реестр
  Сущности для сбора и экспорта данных - добавлено окно редактирования для возможности выбора очереди.
  

## [3.5.10] - 2025-03-24

### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Переход на pyproject.toml.


## [3.5.9] - 2025-03-14

### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Исправление сборки.


## [3.5.8] - 2025-03-13

### Изменено

- [EDUDEVOPS-66](https://jira.bars.group/browse/EDUDEVOPS-66)
  PATCH Внедрение автоматизации версионирования через setuptools-git-versioning.


## [3.5.7] - 2025-03-03

Испарвлена ошибка импорта в export_manager.

### Исправлено

- [EDUSCHL-22403](https://jira.bars.group/browse/EDUSCHL-22403)
  PATCH Исправлена ошибка импорта в export_manager.


## [3.5.6] - 2025-02-20

Доработана отправка файлов в витрину - добавлена проверка статусов файла и новый статус `Ошибка обработки витриной` для
ExportingDataSubStageStatus. Доработана задача проверки статусов UploadStatusHelper.

Добавлены новые настройки

| Название настройки в settings              | Описание                                                                            | Значение по умолчанию |
|--------------------------------------------|-------------------------------------------------------------------------------------|-----------------------|
| RDM_RESPONSE_FILE_STATUS                   | Установить тип ответа витрины при проверке статуса отправленного файла.             | 'success'             |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('uploader_client', 'RESPONSE_FILE_STATUS'): 'success',
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
    # Установить тип ответа витрины при проверке статуса отправленного файла
    RDM_RESPONSE_FILE_STATUS = conf.get('uploader_client', 'RESPONSE_FILE_STATUS') 
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [uploader_client]
    ...
    RESPONSE_FILE_STATUS=success
    ...
  ``` 

### Исправлено

- [EDUSCHL-22403](https://jira.bars.group/browse/EDUSCHL-22403)
  PATCH Добавлен новый статус Ошибка обработки витриной для ExportingDataSubStageStatus. Добавлена проверка 
  статусов сразу после отправки файлов WorkerSender. Скорректирован статус UploadStatusHelper - при получении статусов 
  ошибки обработки витриной подэтап помечается как PROCESS_ERROR


## [3.5.5] - 2025-02-11

Исправление ошибки в реестре Журнал Логов РВД.

### Исправлено

- [EDUSCHL-23174](https://jira.bars.group/browse/EDUSCHL-23174)
  PATCH Для менеджера UploaderClientLogManager с аннотацией поля attachment_file добавлен output_field=CharField().

- [EDUSCHL-23178](https://jira.bars.group/browse/EDUSCHL-23178)
  PATCH Исправлена команда check_upload_status, в части использования UploadStatusHelper.


## [3.5.4] - 2025-02-07

Внесено исправление в BaseIgnoreLogMixin, в части работы метода _exclude_logs.

### Изменено

- [EDUSCHL-23160](https://jira.bars.group/browse/EDUSCHL-23160)
  PATCH Внесено исправление в BaseIgnoreLogMixin, в части работы метода _exclude_logs.


## [3.5.3] - 2025-01-29

Изменена периодическая задача UploadDataAsyncTask.

### Изменено

- [EDUSCHL-23092](https://jira.bars.group/browse/EDUSCHL-23092)
  PATCH Изменена периодическая задача UploadDataAsyncTask - удалено формирование очереди по сущностям. Сейчас в очередь
  попадает указанное в настройках количество файлов, готовых к отправке в витрину


## [3.5.2] - 2025-02-04

Изменён тип поля institute_ids с django.contrib.postgres.fields.JSONField (поддержка до Django 4.0.)
на django.db.models.JSONField (поддержка с Django 3.1.0).

### Изменено

- [EDUKNDG-15190](https://jira.bars.group/browse/EDUKNDG-15190)
  Для модели AbstractCollectDataCommandProgress изменён тип поля institute_ids на django.db.models.JSONField.


## [3.5.1] - 2025-02-04

Изменена очередность обновления моделей при сборе. Обработка связанных моделей производится ранее основной.

### Изменено

- [EDUSCHL-23133](https://jira.bars.group/browse/EDUSCHL-23133)
  Изменение в периодической задаче TransferLatestEntitiesDataPeriodicTask: добавление связанных моделей перед 
  основной моделью для обеспечения целостности данных при сборе и экспорте.


## [3.5.0] - 2024-12-28

Внесены изменения в CHANGELOG.md для соответствия принятому формату.

### Добавлено

- [EDUCLLG-8818](https://jira.bars.group/browse/EDUCLLG-8818)
  В шаблонах добавлена типизация в `functions` для `helper`-а и в `helpers` - для `cache`.

### Исправлено

- [EDUCLLG-8818](https://jira.bars.group/browse/EDUCLLG-8818)
  Добавлено использование встроенных типов для типизации вместо импортируемых из `typing`.

### Удалено

- [EDUCLLG-8818](https://jira.bars.group/browse/EDUCLLG-8818)
  Убран бесполезный `setUp` в шаблонах `tests.py`.


## [3.4.9] - 2024-12-28

Повышение версии пакета до 3.4.9.

### Исправлено

- Исправлено отображение таблицы в `README.md`;
- Из шаблонов убраны строки, состоящие из пробелов.


## [3.4.8] - 2024-11-14

Повышение версии пакета до 3.4.8.

### Исправлено

- [EDUKNDG-14586](https://jira.bars.group/browse/EDUKNDG-14586)
  Повышение версии пакета до 3.4.8.


## [3.4.7] - 2024-11-14

Добавлена настройка отображения пункта меню "Региональная витрина данных".

Добавлены новые настройки

| Название настройки в settings | Описание                                                         | Значение по умолчанию |
|-------------------------------|------------------------------------------------------------------|-----------------------|
| RDM_MENU_ITEM                 | Отображение пункта меню Пункт меню "Региональная витрина данных" | False                 |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('uploader_client', 'RESPONSE_FILE_STATUS'): 'success',
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
    # Пункт меню "Региональная витрина данных" - Спрятать (False) / Отображать (True)
    RDM_MENU_ITEM = conf.get_bool('rdm_general', 'RDM_MENU_ITEM')
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [rdm_general]
    ...
    RDM_MENU_ITEM = False
    ...
  ``` 

### Добавлено

- [EDUKNDG-14586](https://jira.bars.group/browse/EDUKNDG-14586)
  Добавлена настройка отображения пункта меню "Региональная витрина данных"


## [3.4.6] - 2024-11-12

Исправлена ошибка формирования SQL-запроса с наименованиями таблиц (например, group), 
совпадающими с зарезервированными словами языка SQL.

### Исправлено

- [EDUKNDG-14586](https://jira.bars.group/browse/EDUKNDG-14586)
  Наименование таблицы обернуто в двойные кавычки при формировании строки SQL-запроса.


## [3.4.5] - 2024-11-01

Добавлена обработка ошибок чтения файла при отправке данных в РВД (UploadDataAsyncTask)

### Исправлено

- [EDUSCHL-22734](https://jira.bars.group/browse/EDUSCHL-22734)
  Добавлена обработка ошибок чтения файла при отправке данных в РВД (UploadDataAsyncTask)


## [3.4.4] - 2024-10-23

Добавлена ассинхронная менедж-команда простановки размеров файлов выгрузки в модель ExportingDataSubStageAttachment

### Исправлено

- [EDUSCHL-22651](https://jira.bars.group/browse/EDUSCHL-22651)
  Добавлена ассинхронная менедж-команда простановки размеров файлов выгрузки в модель ExportingDataSubStageAttachment


## [3.4.3] - 2024-10-17

Исправлена миграция простановки размеров файлов выгрузки в модель ExportingDataSubStageAttachment

### Исправлено

- [EDUSCHL-22651](https://jira.bars.group/browse/EDUSCHL-22651)
  Исправлена миграция простановки размеров файлов выгрузки в модель ExportingDataSubStageAttachment


## [3.4.2 ]- 2024-10-15

Добавлены отдельные параметры по управлению временем запуска UploadDataAsyncTask.

| Название настройки в settings              | Описание                                                                               | Значение по умолчанию |
|--------------------------------------------|----------------------------------------------------------------------------------------|-----------------------|
| RDM_UPLOAD_DATA_TASK_MINUTE                | Настройка запуска периодической задачи отправки файлов с данными РВД (минута).         | '0'                   |
| RDM_UPLOAD_DATA_TASK_HOUR                  | Настройка запуска периодической задачи отправки файлов с данными РВД (час).            | '*/2'                 |
| RDM_UPLOAD_DATA_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи отправки файлов с данными РВД (день недели).    | '*'                   |
| RDM_UPLOAD_DATA_TASK_LOCK_EXPIRE_SECONDS   | Время по истечении которого, блокировка может быть снята (в секундах).                 | 7200                  |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rdm_upload_data_task', 'MINUTE'): '0',
        ('rdm_upload_data_task', 'HOUR'): '*/2',
        ('rdm_upload_data_task', 'DAY_OF_WEEK'): '*',
        ('rdm_upload_data_task', 'LOCK_EXPIRE_SECONDS'): 60 * 60 * 2 ,
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
    RDM_UPLOAD_DATA_TASK_MINUTE = conf.get('rdm_upload_data_task', 'MINUTE')
    RDM_UPLOAD_DATA_TASK_HOUR = conf.get('rdm_upload_data_task', 'HOUR')
    RDM_UPLOAD_DATA_TASK_DAY_OF_WEEK = conf.get('rdm_upload_data_task', 'DAY_OF_WEEK')
    RDM_UPLOAD_DATA_TASK_LOCK_EXPIRE_SECONDS = conf.get_int('rdm_upload_data_task', 'LOCK_EXPIRE_SECONDS')  
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    # Настройка запуска периодической задачи отправки csv-файлов в витрину.
    [rdm_upload_data_task]
    MINUTE=*/2
    HOUR=*
    DAY_OF_WEEK=*
    LOCK_EXPIRE_SECONDS = 60 * 60 * 2
  ``` 

### Добавлено

- [EDUSCHL-22166](https://jira.bars.group/browse/EDUSCHL-22166)
  Добавлены отдельные параметры по управлению временем запуска UploadDataAsyncTask


## [3.4.1 ]- 2024-09-26

Добавлена документация по сбору/выгрузке сущностей для ЭДС, ЭК

### Добавлено

- [EDUKNDG-14518](https://jira.bars.group/browse/EDUKNDG-14518)
  Добавлена документация по сбору/выгрузке сущностей для ЭДС, ЭК


## [3.4.0] - 2024-09-25

В базовый класс тестирования функций сбора добавлена поддержка формата PhoneNumber для формирования
экземпляра модели AuditLog.
Повышена версия зависимости educommon >= 3.11.0.
Вынесены утилиты и базовый класс для логирования и сбора по модели в рамках сущности

### Добавлено

- [EDUSCHL-22378](https://jira.bars.group/browse/EDUSCHL-22378)
  Реализация поля моделей Django содержащего номер телефона

### Изменено

- [EDUKNDG-14516](https://jira.bars.group/browse/EDUKNDG-14516)
   PATCH Вынесены утилиты и базовый класс для логирования и сбора по модели в рамках сущности


## [3.3.8] - 2024-10-14

Задача UploadDataAsyncTask изменена с PeriodicAsyncTask на UploadDataAsyncTask

### Изменено

- [EDUSCHL-22519]https://jira.bars.group/browse/EDUSCHL-22519
  PATCH Задача UploadDataAsyncTask изменена с PeriodicAsyncTask на UploadDataAsyncTask


## [3.3.7] - 2024-09-06

Добавлены команда (UploadEntitiesData) и модель (UploadDataCommand) для логирования и запуска выгрузки данных в витрину

### Добавлено

- [EDUSCHL-22042](https://jira.bars.group/browse/EDUSCHL-22042)
  PATCH Добавлены команда (UploadEntitiesData) и модель (UploadDataCommand) для логирования и запуска выгрузки данных 
  в витрину


## [3.3.6] - 2024-09-02

Добавлена фильтрация по дате выгрузки при обновлении данных на экспорт в BaseExportLatestEntitiesData

### Изменено

- [EDUSCHL-22335](https://jira.bars.group/browse/EDUSCHL-22335)
   PATCH Добавлена фильтрация по дате выгрузки при обновлении данных на экспорт в BaseExportLatestEntitiesData


## [3.3.5] - 2024-08-26

Классы UniquePeriodicAsyncTask, PeriodicTaskLocker перенесены в educommon.

### Удалено

- [EDUSCHL-22267](https://jira.bars.group/browse/EDUSCHL-22267)
  MINOR Классы UniquePeriodicAsyncTask, PeriodicTaskLocker перенесены в educommon.


## [3.3.4] - 2024-08-16

Поднята максимальная версия Django (<3.3)

### Изменено

- [EDUKNDG-14560](https://jira.bars.group/browse/EDUKNDG-14560)
  MINOR Добавлена поддержка Django 3.2


## [3.3.3] - 2024-08-19

Изменен порядок запуска сбора и экспорта по сущностям в периодической задаче TransferLatestEntitiesDataPeriodicTask 
с учетом многопоточности, скорректированы номера миграций

### Изменено

- [EDUSCHL-21965](https://jira.bars.group/browse/EDUSCHL-21965)
  PATCH Добавлен параметр export_off в модель TransferredEntity и изменен порядок запуска сбора и экспорта в
  TransferLatestEntitiesDataPeriodicTask. Скорректированы номера миграций


## [3.3.2] - 2024-07-16

Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и logs_period_ended_at

### Изменено

- [EDUSCHL-22070](https://jira.bars.group/browse/EDUSCHL-22070)
  PATCH Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и  logs_period_ended_at


## [3.3.1] - 2024-06-13

Удалён устаревший параметр logs_sub_period_days у базового класса команды сбора данных BaseCollectModelsDataByGeneratingLogsCommand.
Добавлен таймаут для сохранения информации об объемах файла в кеш.

Добавлены новые настройки

| Название настройки в settings              | Описание                                                                               | Значение по умолчанию |
|--------------------------------------------|----------------------------------------------------------------------------------------|-----------------------|
| RDM_REDIS_CACHE_TIMEOUT_SECONDS            | Таймаут для сохранения параметров в общем кеш (секунды).                               | 7200                  |  
  
В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rdm_redis', 'REDIS_CACHE_TIMEOUT_SECONDS'): 60 * 60 * 2,
        ...    
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
    # Таймаут для сохранения параметров в общем кеш.
    RDM_REDIS_CACHE_TIMEOUT_SECONDS = conf.get_int('rdm_redis', 'REDIS_CACHE_TIMEOUT_SECONDS')   
  ```

В дефолтный конфиг проекта необходимо добавить:

  ```
    [rdm_redis]
    ...
    # Таймаут для сохранения параметров в общем кеш.
    REDIS_CACHE_TIMEOUT_SECONDS = 7200
  ```
### Изменено

- [EDUSCHL-20649](https://jira.bars.group/browse/EDUSCHL-20649)
  MINOR Удалён устаревший параметр logs_sub_period_days у базового класса команды сбора данных BaseCollectModelsDataByGeneratingLogsCommand

### Исправлено

- [EDUSCHL-21835](https://jira.bars.group/browse/EDUSCHL-21835)
  PATCH Реализация многопоточной выгрузки


## [3.3.0] - 2024-06-06

Отправка файлов в РВД вынесена в отдельную задачу UploadDataAsyncTask, добавлен кеш файлов и очередь подэтапов отправки,
а также расчет объемов отправляемых файлов.

Добавлены новые настройки

| Название настройки в settings              | Описание                                                                               | Значение по умолчанию |
|--------------------------------------------|----------------------------------------------------------------------------------------|-----------------------|
| RDM_UPLOAD_QUEUE_MAX_SIZE                  | Объем очереди файлов в витрину (в байтах).                                             | 500_000_000           |
| RDM_REDIS_HOST                             | Настройка очереди Redis для формирования файлов РВД (хост).                            |                       |
| RDM_REDIS_PORT                             | Настройка очереди Redis для формирования файлов РВД (порт).                            |                       |
| RDM_REDIS_DB                               | Настройка очереди Redis для формирования файлов РВД (номер бд).                        |                       |
| RDM_REDIS_PASSWORD                         | Настройка очереди Redis для формирования файлов РВД (пароль).                          |                       |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('rdm_general', 'UPLOAD_QUEUE_MAX_SIZE'): 500_000_000,
        ('rdm_redis', 'REDIS_HOST'): 'localhost',
        ('rdm_redis', 'REDIS_PORT'): 6379,
        ('rdm_redis', 'REDIS_DB'): 1,
        ('rdm_redis', 'REDIS_PASSWORD'): '',
        ('rdm_redis', 'REDIS_CACHE_TIMEOUT_SECONDS'): 3600,
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
    # Объем очереди файлов в витрину (в байтах) - по умолчанию 512 Мбайт.
    RDM_UPLOAD_QUEUE_MAX_SIZE = conf.get_int('rdm_general', 'UPLOAD_QUEUE_MAX_SIZE')
    
    # Настройка очереди Redis для формирования файлов РВД.
    RDM_REDIS_HOST = conf.get('rdm_redis', 'REDIS_HOST')
    RDM_REDIS_PORT = conf.get('rdm_redis', 'REDIS_PORT')
    RDM_REDIS_DB = conf.get('rdm_redis', 'REDIS_DB')
    RDM_REDIS_PASSWORD = conf.get('rdm_redis', 'REDIS_PASSWORD')   
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [rdm_general]
    ...
    # Объем очереди файлов в витрину (в байтах) - по умолчанию 512 Мбайт.
    UPLOAD_QUEUE_MAX_SIZE = 500_000_000

    # Настройка очереди Redis для формирования файлов РВД.
    [rdm_redis]
    REDIS_HOST = localhost
    REDIS_PORT = 6379
    REDIS_DB = 1
    REDIS_PASSWORD = 
  ``` 

### Изменено

- [EDUSCHL-21835](https://jira.bars.group/browse/EDUSCHL-21835)
  MINOR Реализация многопоточной выгрузки


## [3.2.8] - 2024-08-02

Исправлена ошибка задвоения сборки и экспорта в периодической задаче TransferLatestEntitiesDataPeriodicTask.

### Изменено

- [EDUSCHL-21965](https://jira.bars.group/browse/EDUSCHL-21965)
  PATCH Исправлена ошибка задвоения сборки и экспорта в периодической задаче TransferLatestEntitiesDataPeriodicTask.


## [3.2.7] - 2024-07-31

Исправлен файл MANIFEST.in для включения в сборку js-шаблонов.

### Изменено

- [EDUSCHL-21965](https://jira.bars.group/browse/EDUSCHL-21965)
  PATCH Добавлено включение js-шаблонов в сборку в файл MANIFEST.in


## [3.2.6] - 2024-07-23

Добавлен параметр export_off (Отключение экспорта для сущности) в модель TransferredEntity
Изменен порядок запуска сбора и экспорта по сущностям в периодической задаче TransferLatestEntitiesDataPeriodicTask

### Изменено

- [EDUSCHL-21965](https://jira.bars.group/browse/EDUSCHL-21965)
  PATCH Добавлен параметр export_off в модель TransferredEntity и изменен порядок запуска сбора и экспорта в
  TransferLatestEntitiesDataPeriodicTask.


## [3.2.5] - 2024-07-16

Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и logs_period_ended_at

### Изменено

- [EDUSCHL-22070](https://jira.bars.group/browse/EDUSCHL-22070)
  PATCH Добавлен параметр use_times_limit в BaseCollectLatestModelsData для использования переданных параметров logs_period_started_at и  logs_period_ended_at


## [3.2.4] - 2024-07-16

Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.

### Изменено

- [EDUSCHL-22217](https://jira.bars.group/browse/EDUSCHL-22217)
  PATCH Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.
  В подзапросах отсутствовало условие фильтрации по статусу.


## [3.2.3] - 2024-06-06

Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.

### Изменено

- [EDUSCHL-21804](https://jira.bars.group/browse/EDUSCHL-21804)
  PATCH Внесены корректировки в запросы используемые в функциях get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates.
  Дата и время окончания предыдущего сбора/экспорта могла быть не корректно определена.


## [3.2.2] - 2024-05-21

Изменения в переодической задаче TransferLatestEntitiesDataPeriodicTask,
Изменено определение даты последнего успешного этапа сбора у менеджеров Функций сбора и экспорта.
Изменения получения крайней даты из переданного поля по указанным моделям в BaseCollectLatestModelsData.
Удалён параметр RDM_TRANSFER_TASK_TIMEDELTA.

### Изменено

- [EDUSCHL-21804](https://jira.bars.group/browse/EDUSCHL-21804)
  PATCH Изменение определения даты последнего успешного этапа сбора у менеджеров Функций сбора и экспорта
  Изменения получения крайней даты из переданного поля по указанным моделям в BaseCollectLatestModelsData.
  Реализованы функции get_collecting_managers_max_period_ended_dates и get_exporting_managers_max_period_ended_dates 
  для получения даты времени успешного этапа сбора/экспорта.


## [3.2.1] - 2024-05-03

Понижен уровень логирования при возникновении ошибки отправки запросов в РВД с ERROR до WARNING

### Изменено

- [EDUSCHL-21903](https://jira.bars.group/browse/EDUSCHL-21903)
  PATCH Понижен уровень логирования при возникновении ошибки отправки запросов в РВД


## [3.2.0] - 2024-05-02

Периодические задачи RDMCheckUploadStatus, CheckSuspendedExportedStagePeriodicTask, 
TransferLatestEntitiesDataPeriodicTask сделаны уникальными.

### Изменено

- [EDUSCHL-21891](https://jira.bars.group/browse/EDUSCHL-21891)
  MINOR Периодические задачи RDMCheckUploadStatus, CheckSuspendedExportedStagePeriodicTask, 
  TransferLatestEntitiesDataPeriodicTask сделаны уникальными. Во время действия блокировки не будет возможности 
  поставить новую подобную задачу.


## [3.1.1] - 2024-05-03

Понижен уровень логирования при возникновении ошибки отправки запросов в РВД с ERROR до WARNING

### Изменено

- [EDUSCHL-21903](https://jira.bars.group/browse/EDUSCHL-21903)
  PATCH Понижен уровень логирования при возникновении ошибки отправки запросов в РВД


## [3.1.0] - 2024-04-23

Добавлена поддержка setuptools 69.*.
Поднята минимальная версия пакета pip 23.2.1

### Изменено

- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  MINOR Добавлена поддержка setuptools 69.*. Поднять минимальную версию pip до 23.2.1.


## [3.0.4] - 2024-04-17

Возвращено проставление подэтапа выгрузки всем записям модели.

### Изменено

- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  PATCH Возвращено проставление подэтапа выгрузки всем записям модели.


## [3.0.3] - 2024-04-11

В классах примесей CollectCommandMixin и ExportCommandMixin указана очередь для celery используемая в рамках пакета.
Указано базовое описание и тип задачи для отражения в реестре "Асинхронные задачи".

### Изменено

- [EDUSCHL-21793](https://jira.bars.group/browse/EDUSCHL-21793)
  PATCH В классах примесей CollectCommandMixin и ExportCommandMixin указана очередь для celery 
  используемая в рамках пакета.


## [3.0.2] - 2024-04-11

Изменены типы полей ОГРН и ОКФС в сущности Organisations на строковые.
Исправлен тип передаваемого параметра institute_ids при выполнении поставленной задачи.
Исправлена ошибка проставления подэтапа выгрузки у неотправленных записей.

### Изменено

- [EDUCLLG-8336](https://jira.bars.group/browse/EDUCLLG-8336)
  PATCH Изменены типы полей ОГРН и ОКФС в сущности Organisations на строковые.

- [EDUSCHL-21743](https://jira.bars.group/browse/EDUSCHL-21743)
  PATCH Исправлен тип передаваемого параметра institute_ids при выполнении поставленной задачи.

- [EDUSCHL-21761](https://jira.bars.group/browse/EDUSCHL-21761)
  PATCH Исправлена ошибка проставления подэтапа.


## [3.0.1] - 2024-04-03

Убрано окружение кавычками пустых необязательных полей.

### Изменено

- [EDUCLLG-8325](https://jira.bars.group/browse/EDUCLLG-8325)
  PATCH Убрано окружение кавычками пустых необязательных полей.


## [3.0.0] - 2024-04-02

Расширены возможности кастомизации поведения метода `BaseExportDataFunctionHelper.prepare_record`.

### Добавлено

- [EDUCLLG-8325](https://jira.bars.group/browse/EDUCLLG-8325)
  MAJOR Добавлена возможность отдельно указывать, как формировать строковое
    представление полей в зависимости от их типа и обязательности. **Требуется добавить
    параметр `required_fields` в метод `prepare_record` helper-а функции**.


## [2.2.1] - 2024-03-28

Исправление наследования Meta в моделях EduRdmCollectDataCommandProgress и EduRdmExportDataCommandProgress

### Исправлено

- [EDUSCHL-21569](https://jira.bars.group/browse/EDUSCHL-21569)
  MINOR Перенести оставшиеся общие асинхронные задачи из ЭШ в пакет edu_rdm_integration


## [2.2.0] - 2024-03-20

Из ЭШ перенесена периодическая задача по сбору и выгрузке данных в РВД.

Также из ЭШ перенесены и переименованы модели:
 - CollectDataCommandProgress перименована в  EduRdmCollectDataCommandProgress
 - ExportDataCommandProgress перименована в EduRdmExportDataCommandProgress
 - Добавлены миксины CollectCommandMixin и ExportCommandMixin

### Добавлено

- [EDUSCHL-21569](https://jira.bars.group/browse/EDUSCHL-21569)
  MINOR Перенести оставшиеся общие асинхронные задачи из ЭШ в пакет edu_rdm_integration


## [2.1.0] - 2024-03-18

Добавлена поддержка Django 3.1.

### Добавлено

- [EDUSCHL-18052](https://jira.bars.group/browse/EDUSCHL-18052)
  MINOR Поднять версию Django до 3.1.14


## [2.0.3] - 2024-03-11

Добавлено сохранение чанка логов в `list` перед его использованием в запускаемых классах в методе `_get_runnable_objects` класса `BaseCollectingDataRunner`.

### Исправлено

- [EDUSCHL-21581](https://jira.bars.group/browse/EDUSCHL-21581)
  PATCH Добавлено сохранение чанка логов в `list` перед его использованием в запускаемых классах в методе `_get_runnable_objects` класса `BaseCollectingDataRunner`.


## [2.0.2] - 2024-03-07

Откатил изменения сделанные в версии 2.0.1. Данные доработки приводили к невозможности отправить данные.

### Исправлено

- [EDUSCHL-21503](https://jira.bars.group/browse/EDUSCHL-21503)
  PATCH Откатил изменения сделанные в версии 2.0.1


## [2.0.1] - 2024-03-01

Изменена работа метода _calculate_last_finished_entity_export класса BaseExportLatestEntitiesData

### Исправлено

- [EDUSCHL-21503](https://jira.bars.group/browse/EDUSCHL-21503)
  PATCH ЭШ. Все модели РВД. Некорректное определение начала периода экспорта командой при сборе 
  командой collect_latest_models_data 


## [2.0.0] - 2024-02-21

Параметр school_ids переименован в institute_ids.

### Изменено

- [EDUSCHL-20485](https://jira.bars.group/browse/EDUSCHL-20485)
  MAJOR Произвести переименование параметра school_ids на institute_ids


## [1.0.2] - 2024-03-06

Добавлено разбиение на чанки запроса на обновление поля modified у невыгруженных записей,
при запуске команды `export_latest_entities_data`.

### Исправлено

- [EDUSCHL-21572](https://jira.bars.group/browse/EDUSCHL-21572)
  PATCH Добавлено разбиение на чанки запроса на обновление в методе `_update_model_modified_field` 
  класса `BaseExportLatestEntitiesData`.


## [1.0.1] - 2024-02-20

Исправлено ограничение сбора логов периодом `RDM_TRANSFER_TASK_TIMEDELTA` в `BaseCollectLatestModelsData`

### Исправлено

- [EDUSCHL-21413](https://jira.bars.group/browse/EDUSCHL-21413)
  PATCH Исправлено ограничение сбора логов периодом `RDM_TRANSFER_TASK_TIMEDELTA` в `BaseCollectLatestModelsData`


## [1.0.0] - 2024-01-31

Удален дублирующийся клаcc `LogChange` из `collect_data.non_calculated.base.caches`.

### Удалено

- [EDUSCHL-21308](https://jira.bars.group/browse/EDUSCHL-21308)
  MAJOR Удален дублирующийся клаcc `LogChange` из `collect_data.non_calculated.base.caches`.


## [0.10.2] - 2024-02-05

Рефакторинг принудительного запуска функций без добавления их в очередь на исполнение.

В класс кеша BaseCollectingExportedDataFunctionCacheStorage расчетных и не расчетных функций добавлен метод _ignore_logs.
Добавлена утилита build_related_model_graph для построения графа связей между моделями. 
Добавлен миксин BaseIgnoreLogMixin, для исключения из обработки логов на основании описанных зависимостей.

### Добавлено

- [EDUSCHL-20550](https://jira.bars.group/browse/EDUSCHL-20550)
  MINOR В класс кеша BaseCollectingExportedDataFunctionCacheStorage добавлен метод _ignore_logs. 
  Добавлена утилита build_related_model_graph. Добавлен миксин BaseIgnoreLogMixin.

### Изменено

- [EDUSCHL-20274](https://jira.bars.group/browse/EDUSCHL-20274)
  MINOR Рефакторинг принудительного запуска функций без добавления их в очередь на исполнение.


## [0.10.1] - 2024-02-02

Изменение в формировании LogChange.
Не формируется LogChange с пустым fields.

### Изменено

- [EDUSCHL-21251](https://jira.bars.group/browse/EDUSCHL-21251)
  PATCH Изменение в формировании LogChange.


## [0.10.0] - 2024-01-19

Добавлена поддержка Django 3.0.
В класс кеша BaseCollectingExportedDataFunctionCacheStorage расчетных и не расчетных функций добавлен метод _ignore_logs.
Добавлена утилита build_related_model_graph для построения графа связей между моделями. 
Добавлен миксин BaseIgnoreLogMixin, для исключения из обработки логов на основании описанных зависимостей.

### Добавлено

- [EDUSCHL-18051](https://jira.bars.group/browse/EDUSCHL-18051)
  MINOR Поднять версию Django до 3.0.14

- [EDUSCHL-20550](https://jira.bars.group/browse/EDUSCHL-20550)
  MINOR В класс кеша BaseCollectingExportedDataFunctionCacheStorage добавлен метод _ignore_logs. 
  Добавлена утилита build_related_model_graph. Добавлен миксин BaseIgnoreLogMixin.


## [0.9.2] - 2024-01-17

Добавлена явная регистрация периодических асинхронных задач Celery.
Поднятие версии зависимостей пакета celery.

### Изменено

- [EDUSCHL-14950](https://jira.bars.group/browse/EDUSCHL-14950)
  PATCH Добавлена явная регистрация периодических асинхронных задач Celery.


## [0.9.1] - 2024-01-11

Добавлен реестр выбора сущностей для сбора и выгрузки данных.
Удалена настройка RDM_TRANSFER_TASK_ENTITIES, вместо перечисления сущностей в конфиге используется реестр и модель
  TransferredEntity.

### Добавлено

- [EDUSCHL-21112](https://jira.bars.group/browse/EDUSCHL-21112)
  MINOR Добавлен реестр выбора сущностей для сбора и выгрузки данных.

### Удалено

- [EDUSCHL-21112](https://jira.bars.group/browse/EDUSCHL-21112)
  MINOR Удалена настройка RDM_TRANSFER_TASK_ENTITIES.


## [0.9.0] - 2023-12-29

Из ЭШ перенесены периодические задачи по сбору статусов загрузки файлов в витрину, а также
по поиску зависших этапов/подэтапов экспорта.

Также из ЭШ перенесены менедж-команды: 
- check_upload_status - проверка состояния отправленных данных в витрину,
- collect_lastest_models_data - сбор на основе логов за период с последней сборки до указанной даты,
- export_latest_entities_data - экспорт данных за период с последней сборки до указанной даты.

Типы получаемых из log_change.fields полей соответствуют типам полей из логируемых моделей.  

### Добавлено

- [EDUSCHL-21013](https://jira.bars.group/browse/EDUSCHL-21013)
  MINOR Перенесена часть асинхронных РВД задач из ЭШ, а также часть менедж-команд

### Изменено

- [EDUSCHL-20793](https://jira.bars.group/browse/EDUSCHL-20793)
  MINOR Типы получаемых из log_change.fields полей должны соответствовать типам полей из логируемых моделей


## [0.8.6] - 2023-12-18

В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  списковому типу (ArrayField).

### Добавлено

- [EDUSCHL-19606](https://jira.bars.group/browse/EDUSCHL-19606)
  PATCH В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  списковому типу (ArrayField).


## [0.8.5] - 2023-12-14

Формирование логов вынесено на уровень команды, а не менеджера.
Добавлено формирование логов на этапе экспорта данных.

### Добавлено

- [EDUSCHL-20073](https://jira.bars.group/browse/EDUSCHL-20073)
  MINOR Логи при экспорте данных

### Изменено

- [EDUSCHL-20073](https://jira.bars.group/browse/EDUSCHL-20073)
  MINOR Формирование логов вынесено на уровень команды, а не менеджера.


## [0.8.4] - 2023-12-13

Создание базовых хэлперов BaseCollectingDataFunctionHelper, BaseCollectingDataRunnerHelper.
Создание нового метода get_filtered_operations в BaseCollectingDataFunctionHelper.

### Добавлено

- [EDUSCHL-21029](https://jira.bars.group/browse/EDUSCHL-21029)
  MINOR Создание базовых хэлперов.


## [0.8.3] - 2023-12-13

Исправление ошибок и несоответствий в журнале логов

### Изменено

- [EDUCLLG-8103](https://jira.bars.group/browse/EDUCLLG-8103)
  MINOR Исправление ошибок и несоответствий в журнале логов .


## [0.8.2] - 2023-12-11

Поднятие версии m3-db-utils,изменение UploaderClientLogManager
### Изменено

- [EDUCLLG-7736](https://jira.bars.group/browse/EDUCLLG-7736)
  MINOR Поднята версии m3-db-utils до 0.3.10, редактирован `UploaderClientLogManager`.


## [0.8.1] - 2023-12-08

Исправлена ошибка внутри EntityEnumRegisterMixin
### Изменено

- [EDUCLLG-8098](https://jira.bars.group/browse/EDUCLLG-8098)
  PATCH Добавлена проверка на наличие атрибута main_model_enum.


## [0.8.0] - 2023-12-08

Вынесен функционал просмотра логов РВД из ЭШ.
Удалено перечисление UploadStatusEnum.
Удалена модель UploadStatus статусов загрузки в витрину. Вместо неё добавлена модель-перечисление DataMartRequestStatus.

### Изменено

- [EDUCLLG-7736](https://jira.bars.group/browse/EDUCLLG-7736)
  MINOR Вынесен функционал просмотра логов РВД из ЭШ.

### Удалено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  MINOR - Удалено перечисление UploadStatusEnum. Удалена модель UploadStatus статусов загрузки в витрину.

### Добавлено

- [EDUSCHL-20965](https://jira.bars.group/browse/EDUSCHL-20965)
  MINOR - Вместо удаленной модели UploadStatus добавлена модель-перечисление DataMartRequestStatus.


## [0.7.3] - 2023-12-07

Исправлена аннотация в шаблоне managers.py-tpl для функции экспорта.

### Исправлено

- [EDUSCHL-19604](https://jira.bars.group/browse/EDUSCHL-19604)
  PATCH Исправлена аннотация в шаблоне managers.py-tpl для функции экспорта.


## [0.7.2] - 2023-12-05

В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  временному типу.
Добавление обработки plugins_info при генерации списка данных формирования команд.

### Добавлено

- [EDUSCHL-19507](https://jira.bars.group/browse/EDUSCHL-19507)
  PATCH В метод _clean_data класса BaseCollectingFunctionTestCase добавлена возможность обрабатывать поля относящиеся к 
  временному типу.

- [EDUSCHL-19507](https://jira.bars.group/browse/EDUSCHL-19507)
  PATCH Добавление обработки plugins_info при генерации списка данных формирования команд.


## [0.7.1] - 2023-12-02

Доработано получение множества моделей на основе данных plugins_info при работе метода _get_loggable_models.

### Изменено

- [EDUSCHL-19576](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Доработано получение множества моделей на основе данных plugins_info при работе метода _get_loggable_models.


## [0.7.0] - 2023-12-02

Добавлено формирование логов для последующего скачивания. 
Доработаны шаблоны реализации Функций сбора и выгрузки данных.
Написана документация для реализации функционала новой Сущности.
Добавлено получение моделей на основе данных plugins_info при работе метода _get_loggable_models.

### Добавлено

- [EDUSCHL-20072](https://jira.bars.group/browse/EDUSCHL-20072)
  MINOR - Реестр сбора и выгрузки. Логи

- [EDUSCHL-20954](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Добавлена документация для реализации функционала новой Сущности.

### Изменено

- [EDUSCHL-20954](https://jira.bars.group/browse/EDUSCHL-20954)
  PATCH Произведена доработка шаблонов Функций сбора и выгрузки данных.

- [EDUSCHL-19576](https://jira.bars.group/browse/EDUSCHL-19576)
  PATCH - Добавлено получение моделей на основе данных plugins_info при работе метода _get_loggable_models.


## [0.6.10] - 2023-11-30

При добавлении префикса RDM_EXPORT_ENTITY_ID_PREFIX в классе BaseExportDataFunctionHelper 
учтены поля из get_ignore_prefix_key_fields.

### Изменено

- [EDUSCHL-20961](https://jira.bars.group/browse/EDUSCHL-20961)
  PATCH - При добавлении префикса RDM_EXPORT_ENTITY_ID_PREFIX в классе BaseExportDataFunctionHelper учтены поля 
        - из get_ignore_prefix_key_fields.


## [0.6.9] - 2023-11-30

Доработка обработки ответа при отправке файлов в РВД.
Добавлены менедж-команды для загрузки данных и запроса статуса загрузки в РВД с использованием uploader-client.
Добавлена инструкция по реализации тестов РВД.
В BaseCollectingFunctionTestCase добавлен метод создания подэтапов сбора данных.

### Добавлено

- [EDUSCHL-20946](https://jira.bars.group/browse/EDUSCHL-20946)
  PATCH - Доработка обработки ответа при отправке файлов в РВД.

- [EDUSCHL-20946](https://jira.bars.group/browse/EDUSCHL-20946)
  MINOR - Добавлены менедж-команды для загрузки данных и запроса статуса загрузки в РВД с использованием uploader-client.

- [EDUSCHL-20951](https://jira.bars.group/browse/EDUSCHL-20951)
  MINOR - Инструкция по реализации тестов РВД

- [EDUSCHL-20951](https://jira.bars.group/browse/EDUSCHL-20951)
  MINOR - Добавлен метод создания подэтапов сбора данных


## [0.6.8] - 2023-11-24

Скорректировано описание сущности РВД TELECOM.
Рефакторинг обновления полей modified у невыгруженных записей при работе экспорта сущностей.
Временное решение обеспечения совместимости регистрации моделей и сущностей старого и нового подхода.
Добавлена возможность отправки запросов в РВД через Proxy API uploader_client.
Изменено формирование логов для последующей обработки.

Добавлены новые настройки

| Название настройки в settings         | Описание                                              | Значение по умолчанию |
|---------------------------------------|-------------------------------------------------------|-----------------------|
| RDM_UPLOADER_CLIENT_USE_PROXY_API     | Использование Proxy API                               | False                 |
| RDM_UPLOADER_CLIENT_USERNAME          | Имя пользователя IAM                                  |                       |
| RDM_UPLOADER_CLIENT_PASSWORD          | Пароль пользователя IAM                               |                       |
| RDM_UPLOADER_CLIENT_ORGANIZATION_OGRN | ОГРН организации, в рамках которой развёрнута Витрина |                       |
| RDM_UPLOADER_CLIENT_INSTALLATION_NAME | Имя инсталляции в целевой Витрине                     |                       |
| RDM_UPLOADER_CLIENT_INSTALLATION_ID   | Идентификатор инсталляции в целевой Витрине           |                       |

В settings.py:

- Добавить значения по умолчанию:
  ```
    PROJECT_DEFAULT_CONFIG.update({
        ...
        ('uploader_client', 'USE_PROXY_API'): False,
        ('uploader_client', 'USERNAME'): '',
        ('uploader_client', 'PASSWORD'): '',
        ('uploader_client', 'ORGANIZATION_OGRN'): '',
        ('uploader_client', 'INSTALLATION_NAME'): '',
        ('uploader_client', 'INSTALLATION_ID'): '',
        ...
    })
  ```

- Получить значения настроек из конфигурационного файла:
  ```
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
  ```
  
В дефолтный конфиг проекта необходимо добавить:

  ```
    [uploader_client]
    ...
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
    ...
  ``` 

### Добавлено

- [EDUSCHL-20854](https://jira.bars.group/browse/EDUSCHL-20854)
  MINOR - Добавлена возможность отправки запросов через Proxy API.

### Изменено

- [EDUSCHL-20808](https://jira.bars.group/browse/EDUSCHL-20808)
  MINOR - При сборе модели командой collect_latest_models_data сжигается память

### Исправлено

- [EDUSCHL-20884](https://jira.bars.group/browse/EDUSCHL-20884)
  PATCH - Изменено название поля rank на rank_contact в сущности РВД TelecomEntity.

- [EDUSCHL-20711](https://jira.bars.group/browse/EDUSCHL-20711)
  PATCH - Доработан метод BaseExportLatestEntitiesData._update_model_modified_field.

- [EDUSCHL-20858](https://jira.bars.group/browse/EDUSCHL-20858)
  PATCH - Временное решение обеспечения совместимости регистрации моделей и сущностей старого и нового подхода.


## [0.6.7] - 2023-11-01

Добавлен миксин EntityEnumRegisterMixin для регистрации сущностей в RegionalDataMartEntityEnum.
Миксин ModelEnumRegisterMixin для регистрации моделей в RegionalDataMartModelEnum.
Добавлены методы для запуска регистрации моделей и сущностей.

### Добавлено

- [EDUCLLG-7632](https://jira.bars.group/browse/EDUCLLG-7632)
  PATCH - Добавлен функционал регистрации моделей и сущностей в моделях-перечислениях.


## [0.6.6] - 2023-10-16

Добавлен базовый класс для тестирования Функций сбора, добавлена явная зависимость Django.

### Добавлено

- [EDUSCHL-20684](https://jira.bars.group/browse/EDUSCHL-20684)
  PATCH - Базовый класс для тестирования Функций сбора;

- [EDUSCHL-20684](https://jira.bars.group/browse/EDUSCHL-20684)
  PATCH - Добавлена зависимость Django.


## [0.6.5] - 2023-10-11

Получение метода генерации логов вынесено в отдельный метод для избавления от необходимости хранить все методы в одном классе.

### Исправлено

- [EDUCLLG-7634](https://jira.bars.group/browse/EDUCLLG-7634)
  PATCH - Получение метода генерации логов вынесено в отдельный метод для избавления от необходимости хранить все методы в одном классе;

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - При сборе актуальных данных моделей отслеживаются уже запущенные сборы и новый сбор по модели не запускается.

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - Указание назначения полей модели-перечисления сущностей RegionalDataMartEntityEnum;

- [EDUSCHL-20571](https://jira.bars.group/browse/EDUSCHL-20571)
  PATCH - Добавление возможности получения значений модели-перечисления RegionalDataMartEntityEnum моделей РВД для указанных сущностей.


## [0.6.4] - 2023-10-09

Исправлена ошибка сборки, из-за которой файлы шаблонов *.py-tpl не попадали в пакет.

### Добавлено

- [EDUCLLG-7634](https://jira.bars.group/browse/EDUCLLG-7634)
  PATCH - Добавлено включение шаблонов *.py-tpl в пакет при сборке.


## [0.6.3] - 2023-10-05

Доработка модели AbstractCollectDataCommandProgress и класса BaseFirstCollectModelsDataCommandsGenerator.

### Добавлено

- [EDUSCHL-20350](https://jira.bars.group/browse/EDUSCHL-20350)
  PATCH - Добавлено формирование id генерации для команд в классе BaseFirstCollectModelsDataCommandsGenerator.
        - Добавлены поля created, generation_id и institute_ids в модель AbstractCollectDataCommandProgress.


## [0.6.2] - 2023-10-04

### Изменено

- [EDUCLLG-7942](https://jira.bars.group/browse/EDUCLLG-7942)
  PATCH Доработка сборки документации.


## [0.6.1] - 2023-10-02

Дополнение поведения BaseExportDataFunctionHelper.

### Изменено

- [EDUSCHL-20535](https://jira.bars.group/browse/EDUSCHL-20535)
  PATCH - В логике BaseExportDataFunctionHelper добавлена очистка строковых полей от управляющих символов.


## [0.6.0] - 2023-09-29

Добавлена функция set_failed_status_suspended_exporting_data_stages для определения и перевода зависших этапов/подэтапов экспорта в статус (FAILED).
Добавлена функция set_failed_status_suspended_collecting_data_stages для определения и перевода зависших этапов/подэтапов сбора в статус (FAILED).

### Добавлено

- [EDUSCHL-20487](https://jira.bars.group/browse/EDUSCHL-20487)
  MINOR Добавлена функция ```set_failed_status_suspended_exporting_data_stages```.

- [EDUSCHL-20487](https://jira.bars.group/browse/EDUSCHL-20487)
  MINOR Добавлена функция ```set_failed_status_suspended_collecting_data_stages```.


## [0.5.9] - 2023-09-25

Повышена версия wheel

### Изменено

- [EDUCLLG-7939](https://jira.bars.group/browse/EDUCLLG-7939)
  PATCH - Повышена версия wheel


## [0.5.8] - 2023-09-13

Исправлена ошибка добавления в описание асинхронной задачи списка выгруженных сущностей
BaseExportLatestEntitiesData._set_description_to_async_task.

### Исправлено

- [EDUSCHL-20334](https://jira.bars.group/browse/EDUSCHL-20334)
  PATCH - Баг с обновлением поля description в BaseExportLatestEntitiesData._set_description_to_async_task.


## [0.5.7] - 2023-09-12

Баг фикс и дополнение поведения BaseExportLatestEntitiesData.

### Изменено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - BaseExportLatestEntitiesData теперь поддерживает выгрузку ни разу невыгруженных сущностей.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Баг с условием в фильтре в BaseExportLatestEntitiesData._update_model_modified_field.


## [0.5.6] - 2023-09-06

Доработаны классы BaseExportLatestEntitiesData и BaseExportEntitiesData.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Исправлено нахождение левой границы в классе ExportLatestEntitiesData;
        - Добавлена проверка на наличие запущенных или готовых к выгрузке сущностей;
        - Добавлен параметр update_modified, который обновляет поле modified у собранных моделей,
          чтобы выгрузить невыгруженные записи.


## [0.5.5] - 2023-09-04

Добавление pip в зависимости сборки пакета.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Добавление pip в зависимости сборки пакета.


## [0.5.4] - 2023-09-04

split_by_days_count переименовал в split_by_quantity.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH split_by_days_count переименовал в split_by_quantity.


## [0.5.3] - 2023-09-03

Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.


## [0.5.2] - 2023-08-28

Замена базового класса функций.

### Изменено

- [EDUSCHL-20344](https://jira.bars.group/browse/EDUSCHL-20344)
  PATCH Замена базового класса функций на WebEduLazySavingPredefinedQueueFunction.


## [0.5.1] - 2023-08-22

Для BaseFirstCollectModelsDataCommandsGenerator добавлено условие - если не заполнен creating_trigger_models,
то словарь с данными для команды не передается.

### Исправлено

- [EDUSCHL-20227](https://jira.bars.group/browse/EDUSCHL-20227)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.

- [EDUSCHL-20229](https://jira.bars.group/browse/EDUSCHL-20229)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.


## [0.5.0] - 2023-08-19

Дополнительная функциональность WebEduEntityValueCache была перенесена в EntityCache в function_tools.

### Удалено

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityValueCache.

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityCacheExtended.


## [0.4.7] - 2023-08-17

Изменено формирование очередности сбора/экспорта моделей/сущностей. Вместо отдельных перечислений используется существующее поле `order_number` модели-перечисления `TitledModelEnum`. В случае, когда `order_number` не указан, т.е. будет использоваться значение по умолчанию `DEFAULT_ORDER_NUMBER`, модель/сущность будет исключена из сбора/экспорта.

### Изменено

- [EDUSCHL-19164](https://jira.bars.group/browse/EDUSCHL-19164)
  MINOR Изменено формирование очередности сбора/экспорта моделей/сущностей.


## [0.4.6] - 2023-08-16

Удален лишний вызов метода _prepare_logs

### Исправлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
  PATCH удален лишний вызов метода ```_prepare_logs``` в методе  ```__init__``` класса ```BaseCollectingCalculatedExportedDataFunctionCacheStorage```


## [0.4.5] - 2023-08-09

Объединение обрабатываемых логов относящихся к одному объекту

### Добавлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
 PATCH Новый миксин ```ReformatLogsMixin``` , новое поле is_merge_logs и новый метод _merge_logs у класса ```BaseCollectingExportedDataFunctionCacheStorage```


## [0.4.4] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.


## [0.4.3] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.


## [0.4.2] - 2023-08-11

Исправление ошибки учета миллисекунд, при генерации скриптов сбора и выгрузки данных. В текущий момент chunk_size все
равно работает некорректно. Это связано с тем, что при обнулении миллисекунд за одной записью выборки может скрываться
большое количество, например, которые были созданы или обновлены скриптами. Проблему необходимо решить в будущем, но
текущего решения хватает для эксплуатации.
В выборках моделей и логов не должна входить правая граница периода выборки.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Исправлена ошибка учета миллисекунд в выборках при генерации скриптов с командами для сбора и выгрузки данных.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH В выборках моделей и логов не должна входить правая граница периода выборки.


## [0.4.1] - 2023-08-09

Доработки для реализации принудительного выполнения функций экспорта данных сущностей.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Доработки для реализации принудительного выполнения функций экспорта данных сущностей.


## [0.4.0] - 2023-08-09

Реализованы общие классы для команд сбора/экспорта.

### Добавлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Добавлены общие модели, методы и классы.

### Изменено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Реализованы общие классы для команд сбора/экспорта.


## [0.3.3] - 2023-08-08

Добавлено принудительное выполнение функций в ранере для экономии памяти.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено принудительное выполнение функций в ранере для экономии памяти.


## [0.3.2] - 2023-08-08

Откат к спискам необработанных логов. Исправлена ошибка бесконечного создания чанков логов.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Откат к спискам необработанных логов.


## [0.3.1] - 2023-08-08

Организована передача необработанных логов в виде генератора.

### Изменено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Организована передача необработанных логов в виде генератора.


## [0.3.0] - 2023-08-06

Добавление функциональности для отложенного заполнения кешей. Заполнение производится перед началом работы запускаемого
объекта.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено отложенное заполнение кешей хелперов функций.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  MINOR Добавлено проставление подэтапа выгрузки данных у записей моделей.


## [0.2.2] - 2023-08-06

Для API РВД добавлена поддержка параметра типа операции для загрузки данных.

### Добавлено

- [EDUSCHL-19920](https://jira.bars.group/browse/EDUSCHL-19920)
  PATCH Для API РВД добавлена поддержка параметра типа операции для загрузки данных.


## [0.2.1] - 2023-08-05

Восстановление сборки пакета после ухода с poetry.

### Исправлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Восстановление сборки пакета после миграции с poetry.


## [0.2.0] - 2023-08-04

Перенос стратегий формирования Функций используемых в генерации исходников.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенесены стратегии создания Функций из ЭШ.


## [0.1.4] - 2023-08-03

Возвращение ранее удаленных зависимостей миграции

### Изменено

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Возвращение зависимостей миграции.

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Доработки по формированию документации.

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  Закреплены версии зависимостей, добавлена ссылка на uploader-client


## [0.1.3] - 2023-07-24

Для раскатки миграций на ЭШ, пришлось закомментировать зависимости в initial-миграции.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.


## [0.1.2] - 2023-07-23

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.


## [0.1.0] - 2023-07-18

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенос базовых компонентов интеграции с РВД из ЭШ.
