import django.db.models.deletion
from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):
    """Миграция."""

    dependencies = [
        ('edu_rdm_integration', '0007_delete_upload_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransferredEntity',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'entity',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='edu_rdm_integration.RegionalDataMartEntityEnum',
                        verbose_name='Сущность',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Сущность, по которой должен быть произведен сбор и экспорт данных',
                'verbose_name_plural': 'Сущности, по которым должен быть произведен сбор и экспорт данных',
                'db_table': 'rdm_transferred_entity',
            },
        ),
    ]
