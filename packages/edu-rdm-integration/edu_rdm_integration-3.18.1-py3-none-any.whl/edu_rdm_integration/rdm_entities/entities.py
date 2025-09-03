from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)
from typing import (
    Optional,
)

from educommon.integration_entities.entities import (
    BaseEntity,
)
from m3_db_utils.models import (
    ModelEnumValue,
)

from edu_rdm_integration.rdm_entities.mixins import (
    EntityEnumRegisterMixin,
)
from edu_rdm_integration.rdm_models.models import (
    RDMModelEnum,
)


@dataclass
class AddressEntity(EntityEnumRegisterMixin, BaseEntity):
    """Сущность РВД 'Адреса'."""

    # Параметры регистрации в модель-перечисление РВД
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    title = 'Адреса'
    # TODO EDUSCHL-20938 Рефакторинг в рамках задачи
    # main_model_enum = RegionalDataMartModelEnum.ADDRESS
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Имена полей объявляются как константы, чтобы можно было выводить списки полей
    ID = 'id'
    USE_ADDRESS = 'use_address'
    TYPE_ADDRESS = 'type_address'
    TEXT = 'text'
    CITY = 'city'
    STATE = 'state'
    DISTRICT = 'district'
    POSTAL_CODE = 'postal_code'
    COUNTRY = 'country'
    START_DATETIME = 'start_datetime'
    FLAT = 'flat'
    BUILDING = 'building'
    HOUSE = 'house'
    STREET = 'street'
    CREATE_DATETIME = 'create_datetime'
    SEND_DATETIME = 'send_datetime'
    END_DATETIME = 'end_datetime'

    id: str
    use_address: int
    type_address: int
    text: str
    city: str
    state: str
    district: str
    postal_code: str
    country: str
    start_datetime: datetime
    flat: str
    building: str
    house: str
    street: str
    create_datetime: datetime
    send_datetime: datetime
    end_datetime: datetime = None

    @classmethod
    def get_required_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж обязательных полей."""
        return cls.ID, cls.TYPE_ADDRESS, cls.TEXT, cls.CREATE_DATETIME, cls.SEND_DATETIME

    @classmethod
    def get_hashable_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей, которые необходимо деперсонализировать (хэшировать)."""
        return tuple()

    @classmethod
    def get_primary_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей первичного ключа."""
        return (cls.ID,)

    @classmethod
    def get_foreign_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей внешних ключей."""
        return ()

    @classmethod
    def get_ordered_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей в правильном порядке."""
        return (
            cls.ID,
            cls.USE_ADDRESS,
            cls.TYPE_ADDRESS,
            cls.TEXT,
            cls.CITY,
            cls.DISTRICT,
            cls.STATE,
            cls.POSTAL_CODE,
            cls.COUNTRY,
            cls.START_DATETIME,
            cls.END_DATETIME,
            cls.FLAT,
            cls.BUILDING,
            cls.HOUSE,
            cls.STREET,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_main_model_enum(cls) -> Optional[ModelEnumValue]:
        """Возвращает значение модели перечисление основной модели сущности.

        В классе определяется поле main_model_enum или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return RDMModelEnum.ADDRESS


@dataclass
class AddressOrganisationEntity(EntityEnumRegisterMixin, BaseEntity):
    """Сущность РВД 'Адреса'."""

    # Параметры регистрации в модель-перечисление РВД
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    title = 'Адреса организаций'
    # TODO EDUSCHL-20938 Рефакторинг в рамках задачи
    # main_model_enum = RegionalDataMartModelEnum.ADDRESS_ORGANISATION
    # TODO EDUSCHL-20938 Рефакторинг в рамках задачи
    # additional_model_enums = (RegionalDataMartModelEnum.ORGANISATION, )
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Имена полей объявляются как константы, чтобы можно было выводить списки полей
    ADDRESS_ID = 'address_id'
    ORGANISATION_ID = 'organisation_id'
    CREATE_DATETIME = 'create_datetime'
    SEND_DATETIME = 'send_datetime'

    address_id: str
    organisation_id: str
    create_datetime: datetime
    send_datetime: datetime

    @classmethod
    def get_required_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж обязательных полей."""
        return cls.ADDRESS_ID, cls.ORGANISATION_ID, cls.CREATE_DATETIME, cls.SEND_DATETIME

    @classmethod
    def get_hashable_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей, которые необходимо деперсонализировать (хэшировать)."""
        return tuple()

    @classmethod
    def get_primary_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей первичного ключа."""
        return (
            cls.ADDRESS_ID,
            cls.ORGANISATION_ID,
        )

    @classmethod
    def get_foreign_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей внешних ключей."""
        return ()

    @classmethod
    def get_ordered_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей в правильном порядке."""
        return (
            cls.ADDRESS_ID,
            cls.ORGANISATION_ID,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_main_model_enum(cls) -> Optional[ModelEnumValue]:
        """Возвращает значение модели перечисление основной модели сущности.

        В классе определяется поле main_model_enum или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return RDMModelEnum.ADDRESS_ORGANISATION

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_additional_model_enums(cls) -> Optional[tuple[ModelEnumValue]]:
        """Возвращает кортеж значений модели-перечисления основной модели сущности.

        В классе определяется поле additional_model_enums или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return (RDMModelEnum.ORGANISATION,)


@dataclass
class TelecomEntity(EntityEnumRegisterMixin, BaseEntity):
    """Сущность РВД "Контактные данные"."""

    # Параметры регистрации в модель-перечисление РВД
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    title = 'Контактные данные'
    # TODO EDUSCHL-20938 Рефакторинг в рамках задачи
    # main_model_enum = RegionalDataMartModelEnum.TELECOM
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # Имена полей объявляются как константы, чтобы можно было выводить списки полей
    ID = 'id'
    TYPE_CONTACT = 'type_contact'
    VALUE_TYPE = 'value_type'
    USE_COD = 'use_cod'
    RANK_CONTACT = 'rank_contact'
    START_DATETIME = 'start_datetime'
    END_DATETIME = 'end_datetime'
    CREATE_DATETIME = 'create_datetime'
    SEND_DATETIME = 'send_datetime'

    id: str
    type_contact: int
    value_type: str
    use_cod: int
    start_datetime: datetime
    create_datetime: datetime
    send_datetime: datetime

    # Данные для полей не собираются
    rank_contact: Optional[int] = None
    end_datetime: datetime = None

    @classmethod
    def get_ordered_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей в правильном порядке."""
        return (
            cls.ID,
            cls.TYPE_CONTACT,
            cls.VALUE_TYPE,
            cls.USE_COD,
            cls.RANK_CONTACT,
            cls.START_DATETIME,
            cls.END_DATETIME,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    @classmethod
    def get_primary_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей первичного ключа."""
        return (cls.ID,)

    @classmethod
    def get_foreign_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей внешних ключей."""
        return ()

    @classmethod
    def get_required_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж обязательных полей."""
        return (
            cls.ID,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    @classmethod
    def get_hashable_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей, которые необходимо деперсонализировать (хэшировать)."""
        return tuple()

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_main_model_enum(cls) -> Optional[ModelEnumValue]:
        """Возвращает значение модели перечисление основной модели сущности.

        В классе определяется поле main_model_enum или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return RDMModelEnum.TELECOM


@dataclass
class OrganisationsEntity(EntityEnumRegisterMixin, BaseEntity):
    """Сущность РВД "Организации"."""

    # Параметры регистрации в модель-перечисление РВД
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    title = 'Организации'
    # TODO EDUSCHL-20938 Рефакторинг в рамках задачи
    # main_model_enum = RegionalDataMartModelEnum.ORGANISATION
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    ID = 'id'
    ROSOBR_ID = 'rosobr_id'
    OGRN = 'ogrn'
    OKPO = 'okpo'
    INN = 'inn'
    KPP = 'kpp'
    ACTIVE = 'active'
    OKPF = 'okpf'
    OKFS = 'okfs'
    OKOGU = 'okogu'
    OKATO = 'okato'
    OKTMO = 'oktmo'
    NAME = 'name'
    PARTOF_ID = 'partof_id'
    EXECUTIVE_NAME = 'executive_name'
    EXECUTIVE_POSITION = 'executive_position'
    MODIFIED = 'modified'
    CREATE_DATETIME = 'create_datetime'
    SEND_DATETIME = 'send_datetime'
    PHONE = 'phone'

    id: str
    rosobr_id: str
    ogrn: str
    okpo: str
    inn: str
    kpp: str
    active: bool
    okpf: str
    okfs: str
    okogu: str
    okato: str
    oktmo: str
    name: str
    partof_id: str
    executive_name: str
    executive_position: str
    modified: datetime
    create_datetime: datetime
    send_datetime: datetime
    phone: str

    @classmethod
    def get_ordered_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей в правильном порядке."""
        return (
            cls.ID,
            cls.ROSOBR_ID,
            cls.OGRN,
            cls.OKPO,
            cls.INN,
            cls.KPP,
            cls.ACTIVE,
            cls.OKPF,
            cls.OKFS,
            cls.OKOGU,
            cls.OKATO,
            cls.OKTMO,
            cls.NAME,
            cls.PARTOF_ID,
            cls.EXECUTIVE_NAME,
            cls.EXECUTIVE_POSITION,
            cls.PHONE,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    @classmethod
    def get_required_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж обязательных полей."""
        return (
            cls.ID,
            cls.ROSOBR_ID,
            cls.OGRN,
            cls.INN,
            cls.KPP,
            cls.OKPF,
            cls.OKFS,
            cls.OKOGU,
            cls.OKATO,
            cls.OKTMO,
            cls.NAME,
            cls.EXECUTIVE_NAME,
            cls.EXECUTIVE_POSITION,
            cls.PHONE,
            cls.CREATE_DATETIME,
            cls.SEND_DATETIME,
        )

    @classmethod
    def get_primary_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей первичного ключа."""
        return (cls.ID,)

    @classmethod
    def get_foreign_key_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей внешних ключей."""
        return (cls.PARTOF_ID,)

    @classmethod
    def get_hashable_fields(cls) -> tuple[str, ...]:
        """Возвращает кортеж полей, которые необходимо деперсонализировать (хэшировать)."""
        return ()

    # TODO EDUSCHL-20938 Удалить в рамках задачи
    @classmethod
    def get_main_model_enum(cls) -> Optional[ModelEnumValue]:
        """Возвращает значение модели перечисление основной модели сущности.

        В классе определяется поле main_model_enum или данный метод.

        !!! Временное решение. Будет удалено в рамках EDUSCHL-20938.
        """
        return RDMModelEnum.ORGANISATION
