from typing import (
    TYPE_CHECKING,
)

import uploader_client
from django.core.cache import (
    DEFAULT_CACHE_ALIAS,
    caches,
)
from django.core.management import (
    BaseCommand,
)
from uploader_client.adapters import (
    UploaderAdapter,
)
from uploader_client.contrib.rdm.interfaces.configurations import (
    RegionalDataMartUploaderConfig,
)


if TYPE_CHECKING:
    from uploader_client.interfaces import (
        OpenAPIRequest,
    )


class BaseDatamartClientCommand(BaseCommand):
    """Базовая команда для загрузки данных/получение статуса в РВД с использованием uploader_client."""

    TIMEOUT = 300
    REQUEST_RETRIES = 1

    def add_arguments(self, parser):
        """Добавление параметров."""
        parser.add_argument(
            '--url',
            type=str,
            required=True,
            help='url хоста Datamart Studio',
        )
        parser.add_argument(
            '--datamart_mnemonic',
            type=str,
            required=True,
            help='мнемоника Витрины',
        )
        parser.add_argument(
            '--organization_ogrn',
            type=str,
            required=True,
            help='ОГРН организации, в рамках которой развёрнута Витрина',
        )
        parser.add_argument(
            '--installation_name',
            type=str,
            required=True,
            help='имя инсталляции в целевой Витрине',
        )
        parser.add_argument(
            '--installation_id',
            type=int,
            required=True,
            help='идентификатор инсталляции (присутствует в её названии)',
        )
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='имя пользователя IAM',
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='пароль пользователя IAM',
        )

    def _configure_agent_client(
        self,
        url,
        datamart_mnemonic,
        organization_ogrn,
        installation_name,
        installation_id,
        username,
        password,
    ):
        """Конфигурирование клиента загрузчика данных в Витрину."""
        uploader_client.set_config(
            RegionalDataMartUploaderConfig(
                interface='uploader_client.contrib.rdm.interfaces.rest.ProxyAPIInterface',
                cache=caches[DEFAULT_CACHE_ALIAS],
                url=url,
                datamart_name=datamart_mnemonic,
                organization_ogrn=organization_ogrn,
                installation_name=installation_name,
                installation_id=installation_id,
                username=username,
                password=password,
                timeout=self.TIMEOUT,
                request_retries=self.REQUEST_RETRIES,
            )
        )

    def _get_request(self, **options) -> 'OpenAPIRequest':
        """Возвращает запрос для отправки в РВД."""
        raise NotImplementedError

    def handle(self, *args, **options):
        """Выполнение действий команды."""
        self._configure_agent_client(
            url=options['url'],
            datamart_mnemonic=options['datamart_mnemonic'],
            organization_ogrn=options['organization_ogrn'],
            installation_name=options['installation_name'],
            installation_id=options['installation_id'],
            username=options['username'],
            password=options['password'],
        )

        request = self._get_request(**options)

        result = UploaderAdapter().send(request)

        if result.error:
            self.stdout.write(self.style.ERROR('ERROR:\n'))
            self.stdout.write(
                f'{result.error}\nREQUEST:\n"{result.log.request}"\n\nRESPONSE:\n"{result.log.response}"\n'
            )
        else:
            self.stdout.write(self.style.SUCCESS('SUCCESS:\n'))
            self.stdout.write(
                f'Response with {result.response.status_code} code and content:\n{result.response.text}\n'
            )
