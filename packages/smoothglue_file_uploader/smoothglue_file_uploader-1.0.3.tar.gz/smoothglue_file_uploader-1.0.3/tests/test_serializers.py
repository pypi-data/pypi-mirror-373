import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError

from smoothglue.file_uploader.models import FileType, DocumentStoreConfiguration
from smoothglue.file_uploader.serializers import DocumentSerializer
from tests.utils import (
    TestStorageProvider,
    get_test_document_and_file,
    get_test_storage_provider,
)


class TestDocumentSerializer(TestCase):
    def setUp(self):
        self.reference_id = str(uuid.uuid4())
        _, self.file = get_test_document_and_file()

    @override_settings(UPLOAD_VALIDATORS={"*": "tests.utils.TestValidator"})
    @patch("tests.utils.TestValidator", spec_set=True)
    def test_validation(self, mocked_validator):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }

        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        mocked_validator.validate_uploaded_file.assert_called_once()

    @override_settings(UPLOAD_VALIDATORS={"*": "tests.utils.TestValidator"})
    @patch("tests.utils.TestValidator", spec_set=True)
    def test_validation_exception(self, mocked_validator):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }
        mocked_validator.validate_uploaded_file.side_effect = ValidationError("Fail")
        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors["non_field_errors"][0], "Fail")

    @override_settings(UPLOAD_VALIDATORS={"*": "tests.utils.TestValidator"})
    @patch("tests.utils.TestValidator", spec_set=True)
    def test_validation_other_exception(self, mocked_validator):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }
        mocked_validator.validate_uploaded_file.side_effect = Exception("Fail")
        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        self.assertTrue(
            "Failed to execute validation for" in serializer.errors["non_field_errors"][0]
        )

    @override_settings(UPLOAD_POST_PROCESSORS={"*": "tests.utils.TestPostProcessor"})
    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    @patch("tests.utils.TestPostProcessor", spec_set=True)
    def test_post_processing(self, mocked_processor):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }

        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        mocked_processor.process_uploaded_file.assert_called_once()

    @override_settings(UPLOAD_POST_PROCESSORS={"*": "tests.utils.TestPostProcessor"})
    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    @patch("tests.utils.TestPostProcessor", spec_set=True)
    def test_post_processing_exception(self, mocked_processor):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }

        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        mocked_processor.process_uploaded_file.side_effect = Exception()
        with self.assertLogs("smoothglue.file_uploader.serializers") as log:
            serializer.save()
            self.assertTrue("Failed to execute post processing for" in log.output[0])

    @patch(
        "smoothglue.file_uploader.serializers.get_storage_provider",
        get_test_storage_provider({"UPLOAD_RETURN": False}),
    )
    def test_file_upload_failed(self):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }
        serializer = DocumentSerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.create(serializer.validated_data), None)

    @patch("smoothglue.file_uploader.serializers.get_storage_provider")
    def test_valid_upload(self, mocked_get_storage_provider):
        storage_provider = MagicMock(spec=TestStorageProvider)
        mocked_get_storage_provider.return_value = (storage_provider, None)

        # have a successful upload
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }

        serializer = DocumentSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertTrue(obj.pk)
        self.assertEqual(data["name"], obj.name)
        self.assertEqual(data["bytes"], obj.bytes)
        self.assertFalse(obj.store_config)

        # check upload called
        storage_provider.upload_document.assert_called_once()

    @patch("smoothglue.file_uploader.serializers.get_storage_provider")
    def test_valid_upload_with_saved_config(self, mocked_get_storage_provider):
        test_stored_config = DocumentStoreConfiguration.objects.create(
            config_label="test_config", config={"foo": "bar"}
        )
        storage_provider = MagicMock(spec=TestStorageProvider)
        mocked_get_storage_provider.return_value = (storage_provider, test_stored_config)

        # have a successful upload
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": self.file.size,
            "file": self.file,
        }

        serializer = DocumentSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertTrue(obj.pk)
        self.assertEqual(data["name"], obj.name)
        self.assertEqual(data["bytes"], obj.bytes)
        self.assertTrue(obj.store_config)
        self.assertEqual(obj.store_config, test_stored_config)

        # check upload called
        storage_provider.upload_document.assert_called_once()
