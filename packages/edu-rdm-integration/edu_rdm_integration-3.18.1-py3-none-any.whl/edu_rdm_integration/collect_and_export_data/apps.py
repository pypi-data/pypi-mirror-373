from django.apps import (
    AppConfig as AppConfigBase,
)


class AppConfig(AppConfigBase):
    """Базовые компоненты для запуска сбора и выгрузки данных через пользовательский интерфейс."""

    name = __package__
    label = 'rdm_collect_and_export_data'
