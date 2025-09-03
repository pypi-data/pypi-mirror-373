from educommon import (
    ioc,
)

from edu_rdm_integration.pipelines.transfer.actions import (
    EntitySelectPack,
    TransferredEntityPack,
)


def register_actions():
    """Регистрирует паки и экшны."""
    ioc.get('main_controller').packs.extend(
        (
            TransferredEntityPack(),
            EntitySelectPack(),
        )
    )
