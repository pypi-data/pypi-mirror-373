from django.contrib import admin

from smoothglue.file_uploader.models import Document


class DocumentAdmin(admin.ModelAdmin):
    """
    Custom doc admin
    """

    list_display = ("name", "file_checksum", "uploaded_at")

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Document, DocumentAdmin)
