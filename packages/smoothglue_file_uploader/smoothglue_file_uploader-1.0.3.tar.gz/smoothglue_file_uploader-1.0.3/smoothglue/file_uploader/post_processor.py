import abc
import logging

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.request import Request

from smoothglue.file_uploader.models import Document

logger = logging.getLogger(__name__)


class BaseUploadProcessor(abc.ABC):
    """Abstract Class for defining method for processing the message."""

    @staticmethod
    @abc.abstractmethod
    def process_uploaded_file(
        document: Document, file: InMemoryUploadedFile, request: Request = None
    ):
        """
        Args:
            document(Document): Document to be processed
            file(InMemoryUploadedFile): document content

        Returns:
            None
        """


class DefaultUploadProcessor(BaseUploadProcessor):
    """Example of how a UploadProcessor implementation that does logging"""

    @staticmethod
    def process_uploaded_file(
        document: Document, file: InMemoryUploadedFile, request: Request = None
    ):
        logger.info("DefaultUploadProcessor data: %s - %s", document, file)
