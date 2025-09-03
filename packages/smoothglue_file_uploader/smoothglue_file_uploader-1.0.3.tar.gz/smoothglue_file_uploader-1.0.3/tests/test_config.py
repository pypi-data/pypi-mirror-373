from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from smoothglue.file_uploader.config import FileUploaderSettings
from smoothglue.file_uploader.models import DocumentStoreConfiguration
from smoothglue.file_uploader.storage_providers.base import get_storage_provider
from tests.utils import TestStorageProvider

TEST_PROVIDER_CLASS = "tests.utils.TestStorageProvider"
NON_PROVIDER_CLASS = "smoothglue.file_uploader.post_processor.DefaultUploadProcessor"

TEST_CONFIG = {
    "default": {
        "PROVIDER_CLASS": "tests.utils.TestStorageProvider",
        "PROVIDER_CONFIG": {},
    },
    "broken": {
        "PROVIDER_CLASS": "smoothglue.file_uploader.post_processor.DefaultUploadProcessor",
        "PROVIDER_CONFIG": {},
    },
    "valid_option": {
        "PROVIDER_CLASS": "tests.utils.TestStorageProvider",
        "PROVIDER_CONFIG": {},
    },
    "valid_option_unsaved": {
        "PROVIDER_CLASS": "tests.utils.TestStorageProvider",
        "PROVIDER_CONFIG": {},
        "STORE_CONFIG": False,
    },
}


class TestFileUploaderSettings(TestCase):
    @override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG={"foo": "bar"})
    def test_settings_passthrough(self):
        self.assertEqual(FileUploaderSettings.UPLOAD_STORAGE_PROVIDER_CONFIG, {"foo": "bar"})

    @override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG=TEST_CONFIG)
    def test_get_storage_provider(self):
        self.assertIsInstance(get_storage_provider()[0], TestStorageProvider)

    @override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG=TEST_CONFIG)
    def test_invalid_storage_provider_config(self):
        self.assertRaises(ImproperlyConfigured, get_storage_provider, "broken")

    @override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG=TEST_CONFIG)
    def test_valid_secondary_storage_provider_config(self):
        storage_provider, storage_config = get_storage_provider("valid_option")
        self.assertIsInstance(storage_provider, TestStorageProvider)
        self.assertIsInstance(storage_config, DocumentStoreConfiguration)

    @override_settings(UPLOAD_STORAGE_PROVIDER_CONFIG=TEST_CONFIG)
    def test_valid_unsaved_secondary_storage_provider_config(self):
        storage_provider, storage_config = get_storage_provider("valid_option_unsaved")
        self.assertIsInstance(storage_provider, TestStorageProvider)
        self.assertIsNone(storage_config)
