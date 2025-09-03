import uuid

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from smoothglue.file_uploader.admin import DocumentAdmin
from smoothglue.file_uploader.models import Document, DocumentStoreConfiguration
from tests.utils import TestStorageProvider


class TestDocument(TestCase):
    def test_create(self):
        name = "hello.txt"
        file_bytes = 6
        reference_id = uuid.uuid4()
        Document.objects.create(reference_id=reference_id, name=name, bytes=file_bytes)
        obj = Document.objects.first()
        self.assertTrue(obj.pk)
        self.assertEqual(reference_id, obj.reference_id)
        self.assertEqual(6, obj.bytes)
        self.assertEqual(name, str(obj))

    def test_admin(self):
        self.assertFalse(DocumentAdmin(Document, None).has_add_permission(None, None))


class TestDocumentStoreConfiguration(TestCase):
    def test_create(self):
        DocumentStoreConfiguration.objects.create(config_label="test", config={"foo": "bar"})
        obj = DocumentStoreConfiguration.objects.first()
        self.assertTrue(obj.pk)
        self.assertEqual(obj.config_label, "test")
        self.assertEqual(obj.config, {"foo": "bar"})

    def test_valid_get_storage_provider(self):
        valid_instance = DocumentStoreConfiguration.objects.create(
            config_label="test",
            config={
                "PROVIDER_CLASS": "tests.utils.TestStorageProvider",
                "PROVIDER_CONFIG": {},
            },
        )
        storage_class = valid_instance.get_storage_provider()
        self.assertIsInstance(storage_class, TestStorageProvider)

    def test_invalid_get_storage_provider(self):
        invalid_instance = DocumentStoreConfiguration.objects.create(
            config_label="test",
            config={
                "PROVIDER_CLASS": "smoothglue.file_uploader.post_processor.DefaultUploadProcessor",
                "PROVIDER_CONFIG": {},
            },
        )
        self.assertRaises(ImproperlyConfigured, invalid_instance.get_storage_provider)
