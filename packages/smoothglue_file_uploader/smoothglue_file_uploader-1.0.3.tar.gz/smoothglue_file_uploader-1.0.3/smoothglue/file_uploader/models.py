import importlib
import uuid

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from smoothglue.file_uploader.utils import convert_bytes_to_file_size


class FileType(models.TextChoices):
    """Choices for file_uploader.models.Document.type"""

    DOCUMENT = "document"
    IMAGE = "image"


class DocumentCategory(models.TextChoices):
    """Choices for file_uploader.models.Document.category"""

    DEFAULT = "default"
    ATO = "ato"
    ACO = "aco"
    BRIEF = "brief"
    KML = "kml"
    JADOC = "jadoc"
    OTHER = "other"


class DocumentStoreConfiguration(models.Model):
    """Model used to save the store configuration for documents"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    config_label = models.CharField(max_length=255, blank=True)
    config = models.JSONField(default=dict)

    def get_storage_provider(self):
        """
        Builds a storage provider instance from the stored config dict

        Returns:
            StorageProvider: Configured storage provider
        """
        # Import here to avoid circular import
        # pylint: disable=C0415,R0401
        from smoothglue.file_uploader.storage_providers.base import StorageProvider

        module_name, class_name = self.config["PROVIDER_CLASS"].rsplit(".", 1)
        storage_provider_cls = getattr(importlib.import_module(module_name), class_name)

        if not issubclass(storage_provider_cls, StorageProvider):
            raise ImproperlyConfigured("PROVIDER_CLASS is not a subclass of StorageProvider")

        return storage_provider_cls(self.config["PROVIDER_CONFIG"])


class Document(models.Model):
    """The primary document that gets uploaded to the S3 service."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.UUIDField(null=True)
    name = models.CharField(max_length=256)
    ext = models.CharField(max_length=32)
    type = models.CharField(max_length=32, choices=FileType.choices, default=FileType.DOCUMENT)
    bytes = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss_created",
        blank=True,
        null=True,
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss_updated",
        blank=True,
        null=True,
    )
    category = models.CharField(
        max_length=32, choices=DocumentCategory.choices, default=DocumentCategory.DEFAULT
    )

    file_checksum = models.CharField(
        max_length=64, blank=True, help_text="sha256 file checksum"
    )
    store_config = models.ForeignKey(
        DocumentStoreConfiguration, on_delete=models.SET_NULL, null=True, default=None
    )

    @property
    def size(self) -> str:
        """Human-readable file size"""
        return convert_bytes_to_file_size(self.bytes)

    @property
    def path(self):
        """Document path on storage provider"""
        return f"{self.reference_id}/{self.id}"

    def __str__(self):
        return self.name
