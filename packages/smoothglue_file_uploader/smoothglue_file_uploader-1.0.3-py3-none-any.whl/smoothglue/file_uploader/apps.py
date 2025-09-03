from django.apps import AppConfig
from django.db import DatabaseError


class FileUploaderConfig(AppConfig):  # pylint: disable=missing-class-docstring
    name = "smoothglue.file_uploader"

    # # pylint: disable=C0415
    def ready(self):
        """Initializes all DocumentStoreConfigurations that are currently configured"""
        from django.db.migrations.recorder import MigrationRecorder
        from smoothglue.file_uploader.config import FileUploaderSettings
        from smoothglue.file_uploader.models import DocumentStoreConfiguration

        try:
            MigrationRecorder.Migration.objects.all().exists()
        except DatabaseError:
            # Migration table hasn't been populated yet
            return

        minimum_migration_kwargs = {
            "app": "file_uploader",
            "name": "0003_documentstoreconfiguration_document_store_config",
        }

        if MigrationRecorder.Migration.objects.filter(**minimum_migration_kwargs).exists():
            for config_label, config in FileUploaderSettings.UPLOAD_STORAGE_PROVIDER_CONFIG.items():
                if config.get("STORE_CONFIG", True):
                    DocumentStoreConfiguration.objects.get_or_create(
                        config_label=config_label, config=config
                    )
