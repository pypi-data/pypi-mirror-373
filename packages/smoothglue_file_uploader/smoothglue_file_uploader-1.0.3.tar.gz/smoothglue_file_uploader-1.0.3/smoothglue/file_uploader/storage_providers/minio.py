import io
import logging
from typing import Optional, NotRequired

from django.core.files.uploadedfile import InMemoryUploadedFile
from minio import Minio, S3Error, ServerError
from minio.commonconfig import CopySource
from minio.helpers import ObjectWriteResult

from smoothglue.file_uploader.config import ProviderConfig
from smoothglue.file_uploader.exceptions import ServiceUnavailable
from smoothglue.file_uploader.storage_providers.base import StorageProvider

logger = logging.getLogger(__name__)


class MinioConfig(ProviderConfig):
    """
    Configuration schema for Minio
    """

    HOST: str
    PORT: NotRequired[int]
    SECURE: bool
    REGION: str
    BUCKET_NAME: str
    ACCESS_KEY: str
    SECRET_KEY: str


class MinioProvider(StorageProvider):
    """Storage provider for minio block storage"""

    config_type = MinioConfig

    def __init__(self, config: dict):
        super().__init__(config)
        self.client = self.init_minio_client()

        try:
            minio_available = self.client.bucket_exists(self.config["BUCKET_NAME"])
        except Exception as ex:
            msg = f"Error connecting to MinIO client: {ex}"
            logger.warning(msg)

            raise ServiceUnavailable(detail=msg) from ex

        if not minio_available:
            msg = f"Unable to connect to MinIO bucket: '{self.config['BUCKET_NAME']}'"
            logger.warning(msg)

            raise ServiceUnavailable(detail=msg)

    def init_minio_client(self):
        """Initializes the minio client"""
        if self.config.get("PORT"):
            endpoint = f"{self.config['HOST']}:{self.config['PORT']}"
        else:
            endpoint = self.config["HOST"]

        return Minio(
            endpoint,
            region=self.config.get("REGION"),
            access_key=self.config["ACCESS_KEY"],
            secret_key=self.config["SECRET_KEY"],
            secure=self.config["SECURE"],
        )

    def upload_document(self, path: str, data: InMemoryUploadedFile):
        """
        Uploads a file to minio.

        Args:
            path(str): The path to upload the file to
            data(InMemoryUploadedFile): file content to upload

        Returns:
            bool: True if the file was uploaded, False otherwise.
        """
        try:
            data.seek(0)

            res = self.client.put_object(
                bucket_name=self.config["BUCKET_NAME"],
                object_name=path,
                data=data.file,
                length=data.size,
                content_type=data.content_type,
            )
        except (S3Error, ServerError) as exception_message:
            logger.warning("1 Error uploading document: %s", str(exception_message))
            return False

        return isinstance(res, ObjectWriteResult)

    def download_document(self, object_name: str) -> Optional[io.BytesIO]:
        """
        Downloads a file from minio.

        Args:
            object_name(str): The path of the file to download.

        Returns:
            Optional[io.BytesIO]: The downloaded file. None if unsuccessful
        """
        try:
            return io.BytesIO(
                self.client.get_object(
                    bucket_name=self.config["BUCKET_NAME"], object_name=object_name
                ).data
            )
        except (OSError, S3Error, ServerError) as exception_message:
            logger.warning("1 Error downloading document: %s", str(exception_message))
        return None

    def remove_document(self, source: str) -> bool:
        """
        Remove a file from minio.

        Args:
            source(str): The path of the file to remove.

        Returns:
            bool: True if the file was removed, False otherwise.
        """
        try:
            self.client.remove_object(
                bucket_name=self.config["BUCKET_NAME"], object_name=source
            )
            return True
        except (S3Error, ServerError) as exception_message:
            logger.warning("1 Error removing document: %s", str(exception_message))

        return False

    def duplicate_document(self, original_path: str, new_path: str) -> bool:
        """
        Duplicate a file in minio.

        Args:
            original_path(str): The path of the file to copy.
            new_path(str): The new path for the file to be copied to.

        Returns:
            bool: True if the file was copied, False otherwise.
        """
        try:
            self.client.copy_object(
                bucket_name=self.config["BUCKET_NAME"],
                object_name=new_path,
                source=CopySource(self.config["BUCKET_NAME"], original_path),
            )
            return True
        except (S3Error, ServerError) as exception_message:
            logger.warning("1 Error duplicating document: %s", str(exception_message))

        return False
