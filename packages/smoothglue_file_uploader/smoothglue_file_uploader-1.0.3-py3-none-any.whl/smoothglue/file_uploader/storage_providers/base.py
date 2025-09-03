import importlib
import io
from abc import ABC
from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile

from smoothglue.file_uploader.config import (
    FileUploaderSettings,
    StorageProviderConfig,
    ProviderConfig,
)
from smoothglue.file_uploader.models import DocumentStoreConfiguration
from smoothglue.file_uploader.utils import dict_matches_type


class StorageProvider(ABC):
    """Abstract class for defining a storage provider for uploaded files"""

    config_type = ProviderConfig

    def __init__(self, config: dict):
        self.config = self.validated_config(config)

    @classmethod
    def validated_config(cls, config: dict) -> dict:
        """
        Validates that a config dictionary is appropriate for the storage provider
        Args:
            config (dict): the config to validate

        Returns:
            dict: the validated config
        """
        if dict_matches_type(config, cls.config_type):
            return config
        raise ImproperlyConfigured(f"Configuration for {cls.__name__} is invalid")

    def upload_document(self, path: str, data: InMemoryUploadedFile):
        """
        Uploads a file to the storage provider.

        Args:
            path(str): The path to upload the file to
            data(InMemoryUploadedFile): file content to upload

        Returns:
            bool: True if the file was uploaded, False otherwise.
        """
        raise NotImplementedError

    def download_document(self, object_name: str) -> Optional[io.BytesIO]:
        """
        Downloads a file from the storage provider.

        Args:
            object_name(str): The path of the file to download.

        Returns:
            Optional[io.BytesIO]: The downloaded file. None if unsuccessful
        """
        raise NotImplementedError

    def remove_document(self, source: str) -> bool:
        """
        Remove a file from storage provider.

        Args:
            source(str): The path of the file to remove.

        Returns:
            bool: True if the file was removed, False otherwise.
        """
        raise NotImplementedError

    def duplicate_document(self, original_path: str, new_path: str) -> bool:
        """
        Copy a file from storage provider.

        Args:
            original_path(str): The path of the file to copy.
            new_path(str): The new path for the file to be copied to.

        Returns:
            bool: True if the file was copied, False otherwise.
        """
        raise NotImplementedError


def get_storage_provider(
    config: str = "default",
) -> tuple[StorageProvider, Optional[DocumentStoreConfiguration]]:
    """
    Builds a storage provider instance from the configured class and settings

    Returns:
        StorageProvider: Configured storage provider
    """
    if isinstance(config, str):
        storage_provider_config = FileUploaderSettings.UPLOAD_STORAGE_PROVIDER_CONFIG.get(config)
        if not storage_provider_config:
            raise ImproperlyConfigured(
                f"UPLOAD_STORAGE_PROVIDER_CONFIG has no configuration for {config}"
            )
    else:
        raise ValueError("config must be a string")

    try:
        dict_matches_type(storage_provider_config, StorageProviderConfig)
    except ValueError as e:
        raise ImproperlyConfigured("Storage provider is not properly configured") from e

    module_name, class_name = storage_provider_config["PROVIDER_CLASS"].rsplit(".", 1)
    storage_provider_cls = getattr(importlib.import_module(module_name), class_name)

    if not issubclass(storage_provider_cls, StorageProvider):
        raise ImproperlyConfigured("storage_provider is not a subclass of StorageProvider")

    if storage_provider_config.get("STORE_CONFIG", True):

        storage_model, _ = DocumentStoreConfiguration.objects.get_or_create(
            config_label=config, config=storage_provider_config
        )
    else:
        storage_model = None

    return storage_provider_cls(storage_provider_config["PROVIDER_CONFIG"]), storage_model
