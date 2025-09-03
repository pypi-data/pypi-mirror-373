from django.apps import (
    AppConfig,
)


class UploaderLoggerConfig(AppConfig):  # noqa D101
    """Приложение для работы с логами выгрузки данных в РВД."""

    name = 'edu_rdm_integration.stages.upload_data.uploader_log'
    label = 'edu_rdm_integration_uploader_log'
    verbose_name = 'Журнал логов РВД'
