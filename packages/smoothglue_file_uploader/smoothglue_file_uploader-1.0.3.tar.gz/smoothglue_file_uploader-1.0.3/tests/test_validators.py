from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError

from smoothglue.file_uploader.models import Document
from tests.utils import get_test_document_and_file
from smoothglue.file_uploader.validators import DefaultValidator, DuplicateFileValidator


class TestDefaultValidator(TestCase):
    def test_process_uploaded_file(self):
        document, file = get_test_document_and_file()
        self.assertIsNone(DefaultValidator.validate_uploaded_file(document, file))

    def test_process_no_name(self):
        document, file = get_test_document_and_file(document_kwargs={"name": None})
        with self.assertRaises(ValidationError):
            self.assertIsNone(DefaultValidator.validate_uploaded_file(document, file))


class TestDuplicateFileValidator(TestCase):
    def setUp(self):
        self.document, self.file = get_test_document_and_file()

    def test_checksum_passes(self):
        self.assertIsNone(DuplicateFileValidator.validate_uploaded_file(self.document, self.file))

    @override_settings(CALCULATE_CHECKSUM=False)
    def test_calculate_checksum_disabled(self):
        validator_module = "smoothglue.file_uploader.validators"
        with self.assertLogs(validator_module, level="INFO") as context_manager:
            self.assertIsNone(
                DuplicateFileValidator.validate_uploaded_file(self.document, self.file)
            )
            self.assertEqual(
                context_manager.output,
                [
                    f"WARNING:{validator_module}:DuplicateFileValidator requires "
                    f"settings CALCULATE_CHECKSUM to be true"
                ],
            )

    def test_checksum_duplicate(self):
        document_checksum = "foo"
        Document.objects.create(name="foo", ext=".txt", file_checksum=document_checksum)

        with self.assertRaises(ValidationError):
            DuplicateFileValidator.validate_uploaded_file(self.document, self.file)
