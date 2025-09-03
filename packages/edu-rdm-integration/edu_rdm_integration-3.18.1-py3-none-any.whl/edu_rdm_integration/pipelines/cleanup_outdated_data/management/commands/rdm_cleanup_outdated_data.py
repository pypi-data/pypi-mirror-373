from django.core.management import (
    BaseCommand,
)

from edu_rdm_integration.stages.service.model_outdated_data.managers import (
    ModelOutdatedDataCleanerManager,
)


class Command(BaseCommand):
    """Ночная команда для очистки устаревших данных РВД."""

    nightly_script = True

    help = 'Ночная команда для очистки устаревших данных РВД.'

    def handle(self, *args, **options):
        """Запуск очистки устаревших данных РВД."""
        model_data_cleaner_manager = ModelOutdatedDataCleanerManager()
        model_data_cleaner_manager.run()
