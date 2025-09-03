import io
import logging
from abc import abstractmethod
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from django.core.files.uploadedfile import InMemoryUploadedFile

from smoothglue.file_uploader.config import StorageProviderConfig, ProviderConfig
from smoothglue.file_uploader.exceptions import ServiceUnavailable
from smoothglue.file_uploader.storage_providers.base import StorageProvider

logger = logging.getLogger(__name__)


class BaseS3Config(ProviderConfig):
    """
    Configuration common to all S3 storage providers.
    """

    BUCKET_NAME: str


class S3STSConfig(BaseS3Config):
    """
    Configuration common to all S3 storage providers using STS Authentication.
    """

    ROLE_ARN: str


class S3STSWebIdentityConfig(S3STSConfig):
    """
    Configuration for STSWebIdentityS3Provider
    """

    WEB_IDENTITY_TOKEN_FILE: str


class BaseS3StorageProvider(StorageProvider):
    """Base class for S3 storage providers."""

    config_type = BaseS3Config

    def __init__(self, config: StorageProviderConfig):
        super().__init__(config)
        self.client = self.init_s3_client()

        try:
            s3_available = self.client.head_bucket(Bucket=self.config["BUCKET_NAME"])
        except Exception as ex:
            msg = f"Error connecting to S3 client: {ex}"
            logger.warning(msg)

            raise ServiceUnavailable(detail=msg) from ex

        if not s3_available:
            msg = f"Unable to connect to S3 bucket: '{self.config['BUCKET_NAME']}'"
            logger.warning(msg)

            raise ServiceUnavailable(detail=msg)

    @abstractmethod
    def init_s3_client(self):  # pragma: no cover
        """Initializes the boto S3 client"""
        raise NotImplementedError("Must be implemented in subclass")

    def upload_document(self, path: str, data: InMemoryUploadedFile):
        """
        Uploads an object to S3

        Args:
            path(str): The path to upload the file to
            data(InMemoryUploadedFile): file content to upload

        Returns:
            bool: True if the object was uploaded, False otherwise.
        """
        try:
            data.seek(0)

            self.client.put_object(
                Bucket=self.config["BUCKET_NAME"],
                Key=path,
                Body=data.file,
                ContentLength=data.size,
                ContentEncoding=data.content_type,
            )

            return True
        except ClientError as error:
            # Handle client errors (permission errors, invalid input, etc.)
            logger.warning("Error uploading file: %s", error)
            return False

    def download_document(self, object_name: str) -> Optional[io.BytesIO]:
        """
        Downloads a file from S3.

        Args:
            object_name(str): The path of the file to download.

        Returns:
            Optional[io.BytesIO]: The downloaded file. None if unsuccessful
        """
        try:
            response = self.client.get_object(Bucket=self.config["BUCKET_NAME"], Key=object_name)
            body = response["Body"]
            file_like_obj = io.BytesIO(body.read())
            return file_like_obj

        except ClientError as error:
            # Handle client errors (permission errors, invalid input, etc.)
            logger.warning("Error downloading file: %s", error)
            return None

    def remove_document(self, source: str) -> bool:
        """
        Remove a file from S3.

        Args:
            source(str): The path of the file to remove.

        Returns:
            bool: True if the file was removed, False otherwise.
        """
        try:
            self.client.delete_object(Bucket=self.config["BUCKET_NAME"], Key=source)
            return True
        except ClientError as error:
            # Handle client errors (permission errors, invalid input, etc.)
            logger.warning("Error removing object: %s", error)
            return False

    def duplicate_document(self, original_path: str, new_path: str) -> bool:
        """
        Copy a file from S3.

        Args:
            original_path(str): The path of the file to copy.
            new_path(str): The new path for the file to be copied to.

        Returns:
            bool: True if the file was copied, False otherwise.
        """
        try:
            self.client.copy_object(
                Bucket=self.config["BUCKET_NAME"],
                Key=new_path,
                CopySource={"Bucket": self.config["BUCKET_NAME"], "Key": original_path},
            )
            return True
        except ClientError as error:
            # Handle client errors (permission errors, invalid input, etc.)
            logger.warning("Error duplicating object: %s", error)
            return False


class STSS3Provider(BaseS3StorageProvider):
    """Storage provider for AWS S3 using STS auth"""

    config_type = S3STSConfig

    def init_s3_client(self):  # pragma: no cover
        """Initializes the boto S3 client"""
        # Create a session using web identity credentials
        session = boto3.Session()

        # Assume the role using web identity credentials
        sts_client = session.client("sts")

        assumed_role = sts_client.assume_role(
            RoleArn=self.config["ROLE_ARN"], RoleSessionName="AssumeRoleSession"
        )

        # Create a new session using the assumed role credentials
        assumed_session = boto3.Session(
            aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_role["Credentials"]["SessionToken"],
        )

        return assumed_session.client("s3")


class STSWebIdentityS3Provider(BaseS3StorageProvider):
    """Storage provider for AWS S3 using STS Web Identity auth"""

    config_type = S3STSWebIdentityConfig

    def init_s3_client(self):  # pragma: no cover
        """Initializes the boto S3 client"""
        # Create a session using web identity credentials
        session = boto3.Session()

        # Assume the role using web identity credentials
        sts_client = session.client("sts")

        web_identity_token_file = self.config["WEB_IDENTITY_TOKEN_FILE"]
        with open(web_identity_token_file, "r", encoding="utf-8") as file:
            web_identity_token = file.read()

        assumed_role = sts_client.assume_role_with_web_identity(
            RoleArn=self.config["ROLE_ARN"],
            RoleSessionName="AssumeRoleSession",
            WebIdentityToken=web_identity_token,
        )

        # Create a new session using the assumed role credentials
        assumed_session = boto3.Session(
            aws_access_key_id=assumed_role["Credentials"]["AccessKeyId"],
            aws_secret_access_key=assumed_role["Credentials"]["SecretAccessKey"],
            aws_session_token=assumed_role["Credentials"]["SessionToken"],
        )

        return assumed_session.client("s3")
