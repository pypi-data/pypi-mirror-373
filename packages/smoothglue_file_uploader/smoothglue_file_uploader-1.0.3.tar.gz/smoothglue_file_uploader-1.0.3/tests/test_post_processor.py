from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from smoothglue.file_uploader.post_processor import DefaultUploadProcessor
from tests.utils import get_test_document_and_file


class TestDefaultPostProcessor(TestCase):
    def test_process_uploaded_file(self):
        post_processor_module = "smoothglue.file_uploader.post_processor"
        document, file = get_test_document_and_file()
        file = SimpleUploadedFile(name="hello.txt", content=b"hello world!")
        expected_message = f"DefaultUploadProcessor data: {document} - {file}"
        with self.assertLogs(post_processor_module, level="INFO") as context_manager:
            DefaultUploadProcessor.process_uploaded_file(document, file)
            self.assertEqual(
                context_manager.output,
                [f"INFO:{post_processor_module}:{expected_message}"],
            )
