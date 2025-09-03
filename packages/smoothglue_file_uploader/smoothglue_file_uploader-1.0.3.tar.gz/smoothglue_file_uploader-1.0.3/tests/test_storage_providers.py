import io
import os
from typing import Callable, Union
from unittest.mock import mock_open, patch

from botocore.exceptions import ClientError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from minio import Minio, ServerError
from minio.helpers import ObjectWriteResult
from urllib3 import HTTPResponse

from smoothglue.file_uploader.exceptions import ServiceUnavailable
from smoothglue.file_uploader.storage_providers.base import StorageProvider, get_storage_provider
from smoothglue.file_uploader.storage_providers.local import LocalFileSystemProvider
from smoothglue.file_uploader.storage_providers.minio import MinioProvider
from smoothglue.file_uploader.storage_providers.s3 import STSWebIdentityS3Provider
from tests.utils import get_test_document_and_file


class TestBaseStorageProvider(TestCase):
    def test_base_class_raises_notimplemented(self):
        storage_provider = StorageProvider({})
        _, file = get_test_document_and_file()

        with self.assertRaises(NotImplementedError):
            storage_provider.upload_document("", file)

        with self.assertRaises(NotImplementedError):
            storage_provider.download_document("")

        with self.assertRaises(NotImplementedError):
            storage_provider.remove_document("")

        with self.assertRaises(NotImplementedError):
            storage_provider.duplicate_document("", "")

    def test_get_storage_provider_errors(self):
        self.assertRaises(ImproperlyConfigured, get_storage_provider, "foo")
        self.assertRaises(ValueError, get_storage_provider, 1)

        with override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG={"default": {"FOO": "BAR"}}):
            self.assertRaises(ImproperlyConfigured, get_storage_provider)


class TestLocalStorageProvider(TestCase):
    def setUp(self):
        self.file_content = b"hello world!"
        _, self.file = get_test_document_and_file(file_kwargs={"content": self.file_content})
        self.storage_provider = LocalFileSystemProvider({})

    def test_storage_path(self):
        self.assertEqual(self.storage_provider.config["UPLOAD_PATH"], settings.MEDIA_ROOT)
        storage_provider = LocalFileSystemProvider({"UPLOAD_PATH": "FOO"})
        self.assertEqual(storage_provider.config["UPLOAD_PATH"], "FOO")

        with override_settings(MEDIA_ROOT=None):
            self.assertRaises(ValueError, LocalFileSystemProvider, {})

    def test_upload(self):
        test_path = "foo/bar/hello.txt"
        test_full_path = os.path.join(settings.MEDIA_ROOT, test_path)
        with patch("os.makedirs") as mocked_makedirs:
            with patch("builtins.open", mock_open()) as mocked_open:
                self.storage_provider.upload_document(test_path, self.file)
                mocked_open.assert_called_once_with(test_full_path, "wb+")
                mocked_open().write.assert_called_once_with(self.file_content)
            mocked_makedirs.assert_called_once_with(os.path.dirname(test_full_path))

    def test_download(self):
        with patch("builtins.open", mock_open(read_data=self.file_content)) as mocked_open:
            file_content = self.storage_provider.download_document(self.file.name)
            self.assertEqual(file_content.read(), self.file_content)
            mocked_open.assert_called_once_with(
                os.path.join(settings.MEDIA_ROOT, self.file.name), "rb"
            )

    def test_download_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            file_content = self.storage_provider.download_document(self.file.name)
            self.assertIsNone(file_content)

    def test_delete(self):
        with patch("os.remove") as mock_remove:
            delete_success = self.storage_provider.remove_document(self.file.name)
            mock_remove.assert_called_once_with(os.path.join(settings.MEDIA_ROOT, self.file.name))
            self.assertTrue(delete_success)

    def test_delete_file_not_found(self):
        with patch("os.remove", side_effect=FileNotFoundError) as mock_remove:
            delete_success = self.storage_provider.remove_document(self.file.name)
            mock_remove.assert_called_once_with(os.path.join(settings.MEDIA_ROOT, self.file.name))
            self.assertFalse(delete_success)

    def test_duplicate(self):
        with patch("shutil.copy") as mock_copy:
            copy_file_name = f"{self.file.name}-new"
            copy_success = self.storage_provider.duplicate_document(self.file.name, copy_file_name)
            mock_copy.assert_called_once_with(
                os.path.join(settings.MEDIA_ROOT, self.file.name),
                os.path.join(settings.MEDIA_ROOT, copy_file_name),
            )
            self.assertTrue(copy_success)

    def test_duplicate_file_not_found(self):
        with patch("shutil.copy", side_effect=FileNotFoundError) as mock_copy:
            copy_file_name = f"{self.file.name}-new"
            copy_success = self.storage_provider.duplicate_document(self.file.name, copy_file_name)
            mock_copy.assert_called_once_with(
                os.path.join(settings.MEDIA_ROOT, self.file.name),
                os.path.join(settings.MEDIA_ROOT, copy_file_name),
            )
            self.assertFalse(copy_success)


def mock_minio_put(error: bool = False) -> Callable:
    """
    Mocks minio client's put_object method
    Args:
        error(bool): Whether to raise an error

    Returns:
        Callable: mock put function
    """

    def put(_, **kwargs):
        if error:
            raise ServerError("Test", None)
        return ObjectWriteResult(kwargs["bucket_name"], kwargs["object_name"], None, None, None)

    return put


def mock_minio_get(file_content=None, error: bool = False) -> Callable:
    """
    Mocks minio client's get_object method
    Args:
        error(bool): Whether to raise an error

    Returns:
        Callable: mock get function
    """

    def get(_, **kwargs):
        if error:
            raise ServerError("Test", None)
        return HTTPResponse(body=file_content)

    return get


def mock_minio_remove(error: bool = False) -> Callable:
    """
    Mocks minio client's remove_object method
    Args:
        error(bool): Whether to raise an error

    Returns:
        Callable: mock remove function
    """

    def remove(_, **kwargs):
        if error:
            raise ServerError("Test", None)
        return True

    return remove


def mock_minio_copy(error: bool = False) -> Callable:
    """
    Mocks minio client's copy_object method
    Args:
        error(bool): Whether to raise an error

    Returns:
        Callable: mock copy function
    """

    def copy(_, **kwargs):
        if error:
            raise ServerError("Test", None)
        return ObjectWriteResult(kwargs["bucket_name"], kwargs["object_name"], None, None, None)

    return copy


class TestMinioStorageProvider(TestCase):
    def setUp(self):
        self.file_content = b"hello world!"
        _, self.file = get_test_document_and_file(file_kwargs={"content": self.file_content})
        self.mock_minio_config = {
            "HOST": "",
            "SECURE": True,
            "REGION": "",
            "BUCKET_NAME": "",
            "ACCESS_KEY": "",
            "SECRET_KEY": "",
        }

        with patch.object(Minio, "bucket_exists", lambda _, __: True):
            self.storage_provider = MinioProvider(self.mock_minio_config)

    def test_init(self):
        self.assertTrue(isinstance(self.storage_provider.client, Minio))

    def test_init_with_port_in_hostname(self):
        with patch.object(Minio, "bucket_exists", lambda _, __: True):
            storage_provider = MinioProvider(self.mock_minio_config)
            self.assertTrue(isinstance(storage_provider.client, Minio))

    def test_init_with_error(self):
        with patch.object(Minio, "bucket_exists", side_effect=Exception):
            with self.assertRaises(ServiceUnavailable):
                MinioProvider(self.mock_minio_config)

        with patch.object(Minio, "bucket_exists", lambda _, __: False):
            with self.assertRaises(ServiceUnavailable):
                MinioProvider(self.mock_minio_config)

        with patch.object(Minio, "bucket_exists", lambda _, __: True):
            with self.assertRaises(ValueError):
                MinioProvider({"foo": "bar"})

    @patch.object(Minio, "put_object", mock_minio_put())
    def test_upload(self):
        is_success = self.storage_provider.upload_document(self.file.name, self.file)
        self.assertTrue(is_success)

    @patch.object(Minio, "put_object", mock_minio_put(error=True))
    def test_upload_fail(self):
        is_success = self.storage_provider.upload_document(self.file.name, self.file)
        self.assertFalse(is_success)

    def test_download(self):
        with patch.object(Minio, "get_object", mock_minio_get(self.file_content)):
            file_response = self.storage_provider.download_document(self.file.name)
            self.assertEqual(file_response.read(), self.file_content)

    @patch.object(Minio, "get_object", mock_minio_get(error=True))
    def test_download_error(self):
        file_response = self.storage_provider.download_document(self.file.name)
        self.assertIsNone(file_response)

    @patch.object(Minio, "remove_object", mock_minio_remove())
    def test_remove(self):
        remove_response = self.storage_provider.remove_document(self.file.name)
        self.assertTrue(remove_response)

    @patch.object(Minio, "remove_object", mock_minio_remove(error=True))
    def test_remove_error(self):
        remove_response = self.storage_provider.remove_document(self.file.name)
        self.assertFalse(remove_response)

    @patch.object(Minio, "copy_object", mock_minio_copy())
    def test_duplicate(self):
        duplicate_response = self.storage_provider.duplicate_document(self.file.name, "foo")
        self.assertTrue(duplicate_response)

    @patch.object(Minio, "copy_object", mock_minio_copy(error=True))
    def test_duplicate_error(self):
        duplicate_response = self.storage_provider.duplicate_document(self.file.name, "foo")
        self.assertFalse(duplicate_response)


class MockS3Client:
    # pylint: disable=R0913,R0917
    def __init__(
        self,
        head_bucket_response: Union[Exception, bool] = True,
        put_object_error: bool = False,
        get_object_response: bytes = b"",
        delete_object_error: bool = False,
        copy_object_error: bool = False,
    ):
        self.head_bucket_response = head_bucket_response
        self.put_object_error = put_object_error
        self.get_object_response = get_object_response
        self.delete_object_error = delete_object_error
        self.copy_object_error = copy_object_error

    def head_bucket(self, *args, **kwargs) -> bool:
        """Mock for s3 client head_bucket"""
        if isinstance(self.head_bucket_response, Exception):
            raise self.head_bucket_response
        return self.head_bucket_response

    def put_object(self, *args, **kwargs) -> bool:
        """Mock for s3 client put_object"""
        if self.put_object_error:
            error_response = {"Error": {"Code": "500", "Message": "Internal Server Error"}}
            raise ClientError(error_response, "test")
        return True

    def get_object(self, *args, **kwargs) -> dict[str, io.BytesIO]:
        """Mock for s3 client get_object"""
        if self.get_object_response == b"__error__":
            error_response = {"Error": {"Code": "500", "Message": "Internal Server Error"}}
            raise ClientError(error_response, "test")
        return {"Body": io.BytesIO(self.get_object_response)}

    def delete_object(self, *args, **kwargs) -> bool:
        """Mock for s3 client delete_object"""
        if self.delete_object_error:
            error_response = {"Error": {"Code": "500", "Message": "Internal Server Error"}}
            raise ClientError(error_response, "test")
        return True

    def copy_object(self, *args, **kwargs) -> bool:
        """Mock for s3 client copy_object"""
        if self.copy_object_error:
            error_response = {"Error": {"Code": "500", "Message": "Internal Server Error"}}
            raise ClientError(error_response, "test")
        return True


class TestSTSWebIdentityS3Provider(TestCase):
    def setUp(self):
        self.file_content = b"hello world!"
        _, self.file = get_test_document_and_file(file_kwargs={"content": self.file_content})
        self.mockS3Config = {"BUCKET_NAME": "", "ROLE_ARN": "", "WEB_IDENTITY_TOKEN_FILE": ""}

    def test_init(self):
        with patch.object(STSWebIdentityS3Provider, "init_s3_client", return_value=MockS3Client()):
            # Just test that we can initialize the class
            STSWebIdentityS3Provider(self.mockS3Config)

    def test_init_with_error(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(head_bucket_response=Exception()),
        ):
            with self.assertRaises(ServiceUnavailable):
                STSWebIdentityS3Provider(self.mockS3Config)

        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(head_bucket_response=False),
        ):
            with self.assertRaises(ServiceUnavailable):
                STSWebIdentityS3Provider(self.mockS3Config)

        with self.assertRaises(ValueError):
            STSWebIdentityS3Provider({"foo": "bar"})

    def test_upload(self):
        with patch.object(STSWebIdentityS3Provider, "init_s3_client", return_value=MockS3Client()):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.upload_document(self.file.name, self.file)
            self.assertTrue(response)

    def test_upload_error(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(put_object_error=True),
        ):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.upload_document(self.file.name, self.file)
            self.assertFalse(response)

    def test_download(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(get_object_response=self.file_content),
        ):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.download_document(self.file.name)
            self.assertEqual(response.read(), self.file_content)

    def test_download_error(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(get_object_response=b"__error__"),
        ):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.download_document(self.file.name)
            self.assertIsNone(response)

    def test_remove(self):
        with patch.object(STSWebIdentityS3Provider, "init_s3_client", return_value=MockS3Client()):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.remove_document(self.file.name)
            self.assertTrue(response)

    def test_remove_error(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(delete_object_error=True),
        ):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.remove_document(self.file.name)
            self.assertFalse(response)

    def test_duplicate(self):
        with patch.object(STSWebIdentityS3Provider, "init_s3_client", return_value=MockS3Client()):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.duplicate_document(self.file.name, f"{self.file.name}-new")
            self.assertTrue(response)

    def test_duplicate_error(self):
        with patch.object(
            STSWebIdentityS3Provider,
            "init_s3_client",
            return_value=MockS3Client(copy_object_error=True),
        ):
            storage_provider = STSWebIdentityS3Provider(self.mockS3Config)
            response = storage_provider.duplicate_document(self.file.name, f"{self.file.name}-new")
            self.assertFalse(response)
