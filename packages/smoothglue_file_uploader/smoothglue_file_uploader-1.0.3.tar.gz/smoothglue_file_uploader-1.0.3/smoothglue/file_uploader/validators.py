import abc
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.exceptions import ValidationError

from smoothglue.file_uploader.config import FileUploaderSettings
from smoothglue.file_uploader.models import Document

logger = logging.getLogger(__name__)


class BaseUploadValidator(abc.ABC):
    """Abstract class for defining method for validating an uploaded file"""

    @staticmethod
    @abc.abstractmethod
    def validate_uploaded_file(document: Document, file: InMemoryUploadedFile) -> None:
        """
        Validates a submitted file prior to uploading to storage

        Args:
            document(Document): file metadata to validate
            file(InMemoryUploadedFile): file contents to be validated

        Raises:
            ValidationError: If file is not valid
        """


class DefaultValidator(BaseUploadValidator):
    """Example of a Validator implementation that checks for empty filenames"""

    @staticmethod
    def validate_uploaded_file(document: Document, file: InMemoryUploadedFile) -> None:
        if not document.name:
            raise ValidationError("Document name is required")


class DuplicateFileValidator(BaseUploadValidator):
    """Duplicate file validator check using the file_checksum"""

    @staticmethod
    def validate_uploaded_file(document: Document, file: InMemoryUploadedFile) -> None:
        if FileUploaderSettings.CALCULATE_CHECKSUM:
            existing_doc = Document.objects.filter(file_checksum=document.file_checksum).first()
            if existing_doc is not None:
                raise ValidationError(
                    f"Existing file: {existing_doc.name} with the same checksum"
                    + "was previously uploaded"
                )
        else:
            logger.warning("DuplicateFileValidator requires settings CALCULATE_CHECKSUM to be true")
