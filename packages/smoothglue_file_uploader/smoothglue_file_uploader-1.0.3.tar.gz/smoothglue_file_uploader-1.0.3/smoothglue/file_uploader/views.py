from uuid import UUID

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.views import APIView, Response

from smoothglue.file_uploader.exceptions import ServiceUnavailable
from smoothglue.file_uploader.models import Document, DocumentCategory, FileType
from smoothglue.file_uploader.serializers import DocumentSerializer
from smoothglue.file_uploader.storage_providers.base import get_storage_provider
from smoothglue.file_uploader.utils import is_valid_uuid


@extend_schema_view(
    post=extend_schema(
        parameters=[
            OpenApiParameter(
                name="reference_id",
                description=(
                    "Reference Id can be an object ID to be associated"
                    " with the uploaded document"
                ),
                type=UUID,
            ),
            OpenApiParameter(name="type", description="Document Type", type=str),
            OpenApiParameter(name="category", description="Document category", type=str),
        ]
    ),
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="reference_id",
                description=(
                    "Reference Id can be an object ID to be associated"
                    " with the uploaded document"
                ),
                type=UUID,
            ),
            OpenApiParameter(name="type", description="Document Type", type=str),
            OpenApiParameter(name="category", description="Document category", type=str),
        ]
    ),
)
class DocumentList(APIView):
    """View to upload and list uploaded documents."""

    parser_classes = [FormParser, MultiPartParser, JSONParser]

    @staticmethod
    def get(request):
        """Retrieve a detail of Document instance"""
        reference_id = request.query_params.get("reference_id", None)
        if not reference_id or not is_valid_uuid(reference_id):
            return Response(
                "Query parameter must include a valid UUID as 'reference_id'.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        filter_kwargs = {"reference_id": reference_id}
        for filter_param in ["ext", "type", "category"]:
            filter_value = request.query_params.get(filter_param, None)
            if filter_value:
                filter_kwargs[filter_param] = filter_value

        documents = Document.objects.filter(**filter_kwargs)

        serializer = DocumentSerializer(documents, many=True, context={"request": request})
        return Response(serializer.data)

    @staticmethod
    def post(request):
        """
        To upload a document/blob:
        ```
        requirements:
            method: POST
            payload: {
                "file": file-object/blob
                "reference_id": UUID
            }
        ```
        example:
        ```
        import requests
        import uuid
        url = "/documents/"
        requests.post(
            url,
            files={"file": open("/path/to/file", "rb"), reference_id: uuid.uuid4())}
        )
        ```

        note: cannot specify content_type as application/json

        When `UPLOAD_POST_PROCESSORS` is specified in the settings,
        and mapped to a specific category, the uploaded file
        will be post processed after the upload completed.

        example configuration:
        ```
        UPLOAD_POST_PROCESSORS={
            "kml": "smoothglue.file_uploader.post_processor.DefaultUploadProcessor"
        }
        ```
        Where the key will be the file extension of the uploaded file.

        The processor instance implementation
        must have the following signature function:

        ```
        def process_uploaded_file(self, document: Document, file: InMemoryUploadedFile):
        ```

        When `UPLOAD_VALIDATORS` is specified in the settings,
        and mapped to a specific category, the uploaded file
        will be validated prior to upload.

        example configuration:
        ```
        UPLOAD_VALIDATORS={
            "kml": "smoothglue.file_uploader.validators.DefaultValidator"
        }
        ```
        Where the key will be the file extension of the uploaded file.

        The processor instance implementation
        must have the following signature function:

        ```
        def validate_uploaded_file(
            self, document: Document, file: InMemoryUploadedFile
        ) -> bool:
        ```
        """
        file_obj = request.data.get("file")
        # bad request if no file, nothing else to do here
        if not file_obj:
            return Response("Payload must include 'file'.", status=status.HTTP_400_BAD_REQUEST)

        reference_id = request.data.get("reference_id")
        if not reference_id or not is_valid_uuid(reference_id):
            return Response(
                "Payload must include a valid UUID as 'reference_id'.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        category = request.data.get("category")
        if not category:
            category = DocumentCategory.DEFAULT.value

        file_name, file_ext = getattr(file_obj, "name", " ._").rsplit(".", 1)

        data = {
            "reference_id": str(reference_id),
            "name": file_name,
            "ext": file_ext,
            "type": (
                FileType.IMAGE
                if "image" in getattr(file_obj, "content_type", "")
                else FileType.DOCUMENT
            ),
            "bytes": getattr(file_obj, "size", 0),
            "file": file_obj,
            "category": category,
        }

        serializer = DocumentSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            try:
                serializer.save()
            except AssertionError as error:
                if error.args[0] == "`create()` did not return an object instance.":
                    return Response(
                        {"error": "Failed to upload to backend storage"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentView(APIView):
    """View to view, update, and delete specific documents"""

    @staticmethod
    def get(request, document_id: UUID):  # pylint: disable=unused-argument
        """Download the file requested."""
        document = get_object_or_404(Document, pk=document_id)

        if document.store_config:
            storage_provider = document.store_config.get_storage_provider()
        else:
            storage_provider, _ = get_storage_provider()

        document_bytes = storage_provider.download_document(object_name=document.path)

        if document_bytes:
            response = FileResponse(
                document_bytes, filename=f"{document.name}.{document.ext}", as_attachment=True
            )
            response["Access-Control-Expose-Headers"] = "Content-Disposition"

            return response

        raise ServiceUnavailable

    @staticmethod
    def patch(request, document_id: UUID):
        """Update document metadata"""
        document = get_object_or_404(Document, pk=document_id)

        serializer = DocumentSerializer(
            document, context={"request": request}, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request, document_id: UUID):  # pylint: disable=unused-argument
        """Delete document"""
        document = get_object_or_404(Document, pk=document_id)

        if document.store_config:
            storage_provider = document.store_config.get_storage_provider()
        else:
            storage_provider, _ = get_storage_provider()

        if storage_provider.remove_document(document.path):
            document.delete()
            status_code = status.HTTP_204_NO_CONTENT
        else:
            status_code = status.HTTP_404_NOT_FOUND

        return Response(status=status_code)
