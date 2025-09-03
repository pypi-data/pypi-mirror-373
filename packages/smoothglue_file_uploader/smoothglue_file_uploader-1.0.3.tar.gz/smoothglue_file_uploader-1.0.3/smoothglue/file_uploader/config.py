from typing import NotRequired, TypedDict

from django.conf import settings


# Common class for all provider-specific configs to inherit from
class ProviderConfig(TypedDict):
    pass


class StorageProviderConfig(TypedDict):
    """Structure for settings.UPLOAD_STORAGE_PROVIDER_CONFIG values"""

    PROVIDER_CLASS: str
    PROVIDER_CONFIG: dict  # ProviderConfig
    STORE_CONFIG: NotRequired[bool]


class FileUploaderSettingsMeta(type):
    """Facilitates retrieving settings from django settings for FileUploaderSettings"""

    def __getattribute__(cls, key):
        return getattr(settings, key, super().__getattribute__(key))


class FileUploaderSettings(metaclass=FileUploaderSettingsMeta):  # pylint: disable=R0903
    """Proxy for django.conf.settings, setting defaults where settings are missing"""

    # Package settings
    UPLOAD_STORAGE_PROVIDER_CONFIG: dict[str, StorageProviderConfig] = {}
    UPLOAD_POST_PROCESSORS: dict = {}
    UPLOAD_VALIDATORS: dict = {}
    CALCULATE_CHECKSUM: bool = True
