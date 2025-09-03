from django.urls import path

from smoothglue.file_uploader.views import DocumentList, DocumentView

urlpatterns = [
    path("", DocumentList.as_view(), name="document_list"),
    path("<uuid:document_id>/", DocumentView.as_view(), name="document"),
]
