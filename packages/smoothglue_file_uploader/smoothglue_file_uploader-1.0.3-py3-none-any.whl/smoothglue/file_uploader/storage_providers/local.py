import io
import logging
import os
import shutil
from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile

from smoothglue.file_uploader.config import ProviderConfig
from smoothglue.file_uploader.storage_providers.base import StorageProvider

logger = logging.getLogger(__name__)


class LocalFileSystemConfig(ProviderConfig):
    """
    Configuration schema for LocalFileSystemProvider
    """

    UPLOAD_PATH: str


class LocalFileSystemProvider(StorageProvider):
    """Storage provider for local file storage"""

    config_type = LocalFileSystemConfig

    @classmethod
    def validated_config(cls, config: dict) -> dict:
        """
        Validates that a path to upload to is configured
        Args:
            config (dict): the config to validate

        Returns:
            dict: the validated config
        """
        try:
            return super().validated_config(config)
        except (ValueError, ImproperlyConfigured) as e:
            if settings.MEDIA_ROOT:
                return LocalFileSystemConfig(UPLOAD_PATH=settings.MEDIA_ROOT)
            raise e

    def upload_document(self, path: str, data: InMemoryUploadedFile):
        """
        Uploads a file to local path.

        Args:
            path(str): The path to upload the file to
            data(InMemoryUploadedFile): file content to upload

        Returns:
            bool: True if the file was uploaded, False otherwise.
        """

        full_path = os.path.join(self.config["UPLOAD_PATH"], os.path.dirname(path))
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        # save the uploaded file inside that folder.
        full_filename = os.path.join(self.config["UPLOAD_PATH"], path)
        with open(full_filename, "wb+") as f_out:
            for chunk in data.chunks():
                f_out.write(chunk)
            f_out.close()

        return True

    def download_document(self, object_name: str) -> Optional[io.BytesIO]:
        """
        Downloads a file from minio.

        Args:
            object_name(str): The path of the file to download.

        Returns:
            Optional[io.BytesIO]: The downloaded file. None if unsuccessful
        """

        full_filename = os.path.join(self.config["UPLOAD_PATH"], object_name)
        try:
            with open(full_filename, "rb") as file:
                buf = io.BytesIO(file.read())
                return buf
        except FileNotFoundError as error:
            logger.warning("Error downloading document: %s", str(error))
        return None

    def remove_document(self, source: str) -> bool:
        """
        Remove a file from local fs.

        Args:
            source(str): The path of the file to remove.

        Returns:
            bool: True if the file was removed, False otherwise.
        """
        try:
            full_filename = os.path.join(self.config["UPLOAD_PATH"], source)
            os.remove(full_filename)
            return True
        except FileNotFoundError as error:
            logger.warning("Error removing document: %s", str(error))
        return False

    def duplicate_document(self, original_path: str, new_path: str) -> bool:
        """
        Copy a file from local fs.

        Args:
            original_path(str): The path of the file to copy.
            new_path(str): The new path for the file to be copied to.

        Returns:
            bool: True if the file was copied, False otherwise.
        """
        try:
            original_filename = os.path.join(self.config["UPLOAD_PATH"], original_path)
            new_filename = os.path.join(self.config["UPLOAD_PATH"], new_path)
            shutil.copy(original_filename, new_filename)

            return True
        except FileNotFoundError as error:
            logger.warning("Error duplicating document: %s", str(error))
        return False
