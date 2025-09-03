from django.apps import (
    AppConfig,
)


class RDMEntitiesAppConfig(AppConfig):
    """Приложение для работы с сущностями РВД."""

    name = 'edu_rdm_integration.rdm_entities'
    label = 'edu_rdm_integration_entities'
    verbose_name = 'Сущности РВД'
