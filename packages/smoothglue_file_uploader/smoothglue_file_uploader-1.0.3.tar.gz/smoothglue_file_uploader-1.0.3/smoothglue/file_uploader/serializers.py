import importlib
import logging

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from smoothglue.file_uploader.config import FileUploaderSettings
from smoothglue.file_uploader.models import Document, DocumentStoreConfiguration
from smoothglue.file_uploader.storage_providers.base import get_storage_provider
from smoothglue.file_uploader.utils import generate_checksum

logger = logging.getLogger(__name__)


class DocumentStoreConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentStoreConfiguration
        fields = ["id", "created", "config_label", "config"]


class DocumentSerializer(serializers.ModelSerializer):
    """
    Uploads to the minio and creates a new Document object
    When UPLOAD_POST_PROCESSORS is specified in the settings,
    and mapped to a specific category, the uploaded file will be
    post processed after the upload completed.

    example configuration:
    ```
    UPLOAD_POST_PROCESSORS={
        "kml": "smoothglue.file_uploader.post_processor.DefaultUploadProcessor"
    }
    ```
    Where the key will be the file extension of the uploaded file.

    The processor instance implementation must have the following signature function:

    ```
    def process_message(self, document: Document, file: InMemoryUploadedFile):
    ```

    """

    store_config = DocumentStoreConfigurationSerializer(required=False)

    class Meta:
        model = Document
        fields = [
            "id",
            "reference_id",
            "name",
            "ext",
            "type",
            "bytes",
            "size",
            "uploaded_at",
            "modified_at",
            "category",
            "store_config",
        ]

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        if (
            self.context.get("request")
            and self.context["request"].method == "POST"
            and FileUploaderSettings.CALCULATE_CHECKSUM
        ):
            validated_data["file_checksum"] = generate_checksum(self.initial_data["file"])

        if not self.instance:
            document = Document(**validated_data)
            for file_ext in [document.ext.lower(), "*"]:
                if class_name := FileUploaderSettings.UPLOAD_VALIDATORS.get(file_ext):
                    self._run_validator(class_name, document, file_ext)
        return validated_data

    def create(self, validated_data):
        storage_provider, config_model = get_storage_provider()

        request = self.context.get("request")
        if request:
            validated_data["created_by"] = request.user
            validated_data["updated_by"] = request.user

        document = Document.objects.create(**validated_data)

        is_upload_successful = storage_provider.upload_document(
            document.path, self.initial_data["file"]
        )
        if not is_upload_successful:
            Document.objects.get(id=document.id).delete()
            document = None

        if document:
            if config_model:
                document.store_config = config_model
                document.save()
            for file_ext in [document.ext.lower(), "*"]:
                if cls_name := FileUploaderSettings.UPLOAD_POST_PROCESSORS.get(file_ext):
                    self._run_post_processor(cls_name, document, file_ext, request)

        return document

    def _run_post_processor(
        self, class_str: str, document: Document, file_ext: str, request: Request
    ) -> None:
        """
        Get a processor class from a python module string

        Args:
            class_str(str): python module representation for the class.
            document(Document): document to run post-processing on
            file_ext(str): file extension corresponding to post processor
        """
        try:
            module_name, class_name = class_str.rsplit(".", 1)
            processor = getattr(importlib.import_module(module_name), class_name)
            processor.process_uploaded_file(document, self.initial_data["file"], request)

        except Exception as error:  # pylint: disable=broad-except
            logger.warning("Failed to execute post processing for %s: %s", file_ext, error)

    def _run_validator(self, class_str: str, document: Document, file_ext: str) -> None:
        """
        Runs a given validator class on a given document

        Args:
            class_str(str): python module representation for the class.
            document(Document): Document to be validated.
            file_ext(str): file extension corresponding to validator
        """
        try:
            module_name, class_name = class_str.rsplit(".", 1)
            validator = getattr(importlib.import_module(module_name), class_name)
            validator.validate_uploaded_file(document, self.initial_data["file"])
        except ValidationError as error:
            raise error
        except Exception as error:  # pylint: disable=broad-except
            raise ValidationError(
                f"Failed to execute validation for {file_ext}: {error}"
            ) from error
