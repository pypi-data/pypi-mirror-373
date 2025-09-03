import logging
import uuid
from io import BytesIO
from unittest.mock import ANY, create_autospec, patch

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import reverse
from minio import Minio
from minio.helpers import ObjectWriteResult
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient, APITestCase

from smoothglue.file_uploader.config import FileUploaderSettings
from smoothglue.file_uploader.models import Document, FileType, DocumentStoreConfiguration
from smoothglue.file_uploader.serializers import DocumentSerializer
from tests.utils import (
    TestStorageProvider,
    get_test_document_and_file,
    get_test_storage_provider,
)
from smoothglue.file_uploader.utils import generate_checksum


# pylint: disable=missing-function-docstring
def apply_jwt_token_to_client(client, username="test_user", **kwargs):
    existing_user_jwt = {
        "preferred_username": username,
        "given_name": "foo",
        "affiliation": "bar",
        "organization": "Test",
        "name": "Test",
        "usercertificate": "TEST.USER.123451",
        "rank": "N/A",
        "family_name": "Commander",
        "email": "test_user@test.com",
        "iss": "https://test.io/",
        "aud": "1234-foo-test",
    }

    encoded_jwt = jwt.encode(existing_user_jwt, settings.SECRET_KEY)

    client.credentials(HTTP_AUTHORIZATION="Bearer " + encoded_jwt)


class TestDocumentList(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.reference_id = str(uuid.uuid4())
        Group.objects.create(name="TestUsers")
        _, self.text_file = get_test_document_and_file()
        self.user = get_user_model().objects.create_superuser(username="user1")
        self.client.force_login(self.user)
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("document_list")
        apply_jwt_token_to_client(self.client, username=self.user.username)
        self.data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "pdf",
            "type": FileType.DOCUMENT,
            "bytes": self.text_file.size,
            "file": self.text_file,
        }

    def test_get(self):
        resp = self.client.get("/", {"reference_id": self.reference_id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

        # create an uploaded document
        document = Document.objects.create(
            reference_id=self.reference_id,
            name="hello",
            ext="pdf",
            type=FileType.DOCUMENT,
            bytes=1234,
        )
        # call endpoint again
        resp = self.client.get("/", {"reference_id": self.reference_id})
        self.assertEqual(
            resp.json(),
            [
                {
                    "id": str(document.pk),
                    "reference_id": str(self.reference_id),
                    "name": "hello",
                    "ext": "pdf",
                    "type": "document",
                    "bytes": 1234,
                    "size": "1.21 KB",
                    "uploaded_at": ANY,
                    "modified_at": ANY,
                    "category": "default",
                    "store_config": None,
                }
            ],
        )

    def test_get_invalid_reference_id(self):
        resp = self.client.get("/", {"reference_id": "foo"})
        self.assertEqual(400, resp.status_code)

    def test_filter_params(self):
        # create an uploaded document
        document = Document.objects.create(
            reference_id=self.reference_id,
            name="hello",
            ext="pdf",
            type=FileType.DOCUMENT,
            bytes=1234,
        )
        # call endpoint again
        for param in ["ext", "type", "category"]:
            resp = self.client.get(
                "/", {"reference_id": self.reference_id, param: getattr(document, param)}
            )
            self.assertEqual(len(resp.json()), 1)

            resp = self.client.get("/", {"reference_id": self.reference_id, param: ""})
            self.assertEqual(len(resp.json()), 1)

            resp = self.client.get(
                "/", {"reference_id": self.reference_id, param: "foo" + getattr(document, param)}
            )
            self.assertEqual(len(resp.json()), 0)

    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    def test_post_happy_path(self):
        # check initial models
        self.assertEqual(0, Document.objects.count())
        resp = self.client.get(self.list_url, {"reference_id": self.reference_id})
        self.assertEqual(200, resp.status_code)
        self.assertEqual([], resp.json())

        # have a successful upload
        resp = self.client.post(self.list_url, data=self.data)
        self.assertEqual(201, resp.status_code)
        doc = Document.objects.filter(reference_id=self.data.get("reference_id")).first()
        self.assertIsNotNone(doc)
        self.assertIsNotNone(doc.file_checksum, "checksum should be populated")
        self.assertEqual(len(doc.file_checksum), 64)

    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    @patch.object(
        FileUploaderSettings,
        "UPLOAD_VALIDATORS",
        {"*": "smoothglue.file_uploader.validators.DuplicateFileValidator"},
    )
    def test_post_duplicated_checksum(self):
        Document.objects.create(
            **{
                "reference_id": self.reference_id,
                "name": "hello",
                "ext": "pdf",
                "type": FileType.DOCUMENT,
                "file_checksum": generate_checksum(self.text_file),
            }
        )
        resp = self.client.post(self.list_url, data=self.data)
        self.assertEqual(400, resp.status_code, "Upload should be rejected due to same checksum")

    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    @patch.object(FileUploaderSettings, "UPLOAD_VALIDATORS", {})
    def test_post_duplicated_checksum_should_be_ok_when_validation_disabled(self):
        resp = self.client.post(self.list_url, data=self.data)
        self.assertEqual(201, resp.status_code)

        resp = self.client.post(self.list_url, data=self.data)
        self.assertEqual(201, resp.status_code, "Upload should succeed when validation is disabled")

    def test_post_without_file(self):
        data = {"reference_id": self.reference_id}
        resp = self.client.post(self.list_url, data=data)
        self.assertEqual(400, resp.status_code)

    def test_post_invalid_reference_id(self):
        data = {"file": self.text_file}
        resp = self.client.post(self.list_url, data=data)
        self.assertEqual(400, resp.status_code)

    @patch(
        "smoothglue.file_uploader.serializers.get_storage_provider",
        get_test_storage_provider({"UPLOAD_RETURN": False}),
    )
    def test_post_file_save_error(self):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "pdf",
            "type": FileType.DOCUMENT,
            "bytes": 1234,
            "file": self.text_file,
        }

        resp = self.client.post(self.list_url, data=data)
        self.assertEqual(400, resp.status_code)

    @patch.object(DocumentSerializer, "validate", side_effect=ValidationError("Fail"))
    def test_post_validation_error(self, _):
        data = {
            "reference_id": self.reference_id,
            "name": "hello",
            "ext": "pdf",
            "type": FileType.DOCUMENT,
            "bytes": 1234,
            "file": self.text_file,
        }

        resp = self.client.post(self.list_url, data=data)
        self.assertEqual(400, resp.status_code)
        self.assertEqual(resp.json()["non_field_errors"], ["Fail"])

    @patch("smoothglue.file_uploader.serializers.get_storage_provider", get_test_storage_provider())
    def test_post_gif(self):
        # middleware runs into an issue as of
        # this writing where it breaks when
        # dealing with a non text file
        gif = SimpleUploadedFile(
            name="small.gif",
            content=(
                b"GIF89a\x01\x00\x01\x00\x00\xff\x00,"
                b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x00;"
            ),
        )
        data = {"file": gif, "reference_id": self.reference_id}
        minio_client = create_autospec(spec=Minio, spec_set=True)
        object_result = create_autospec(spec=ObjectWriteResult, spec_set=True)

        # mock the get_object return value
        minio_client.put_object.return_value = object_result
        response = self.client.post(self.list_url, data=data)
        self.assertEqual(201, response.status_code)


class TestDocumentDetail(APITestCase):  # pylint: disable=too-many-instance-attributes
    def setUp(self):
        self.client = APIClient()
        self.file_kwargs = {"name": "hello.txt", "content": b"hello world"}
        document_kwargs = {
            "reference_id": str(uuid.uuid4()),
            "name": self.file_kwargs["name"],
            "ext": "txt",
            "type": FileType.DOCUMENT,
            "bytes": len(self.file_kwargs["content"]),
        }
        self.document, self.text_file = get_test_document_and_file(
            document_kwargs=document_kwargs, file_kwargs=self.file_kwargs
        )
        self.stored_config_document, _ = get_test_document_and_file(
            document_kwargs=document_kwargs, file_kwargs=self.file_kwargs
        )
        self.document.save()
        test_stored_config = DocumentStoreConfiguration.objects.create(
            config_label="test_config", config={"foo": "bar"}
        )
        self.stored_config_document.store_config = test_stored_config
        self.stored_config_document.save()
        self.url = reverse("document", args=[self.document.pk])
        self.storedDocumentUrl = reverse("document", args=[self.stored_config_document.pk])
        self.user = get_user_model().objects.create_superuser(username="user1")
        self.client.force_login(self.user)
        apply_jwt_token_to_client(self.client, username=self.user.username)

        Group.objects.create(name="TestUsers")

    @patch("smoothglue.file_uploader.views.get_storage_provider")
    def test_get(self, mocked_get_storage_provider):
        mocked_get_storage_provider.return_value = (
            TestStorageProvider({"DOWNLOAD_RETURN": BytesIO(self.file_kwargs["content"])}),
            None,
        )
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.as_attachment)
        self.assertEqual(b"".join(response.streaming_content), self.text_file.read())

        # unable to download
        mocked_get_storage_provider.return_value = (
            TestStorageProvider({"DOWNLOAD_RETURN": None}),
            None,
        )
        # Disable logging for unit test
        logging.disable(logging.CRITICAL)
        response = self.client.get(self.url)
        logging.disable(logging.NOTSET)
        self.assertEqual(503, response.status_code)

    def test_patch(self):
        data = {"name": "hello2"}
        response = self.client.patch(self.url, data)

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json()["name"], data["name"])

        # send a bad request
        response = self.client.patch(self.url, {"bytes": "x"})
        self.assertEqual(400, response.status_code)

    @patch("smoothglue.file_uploader.views.get_storage_provider")
    def test_delete(self, mocked_get_storage_provider):
        mocked_get_storage_provider.return_value = (
            TestStorageProvider({"REMOVE_RETURN": True}),
            None,
        )

        response = self.client.delete(self.url)
        self.assertEqual(204, response.status_code)

        # unable to remove because Document does not exist
        response = self.client.delete(self.url)
        self.assertEqual(404, response.status_code)

    @patch(
        "smoothglue.file_uploader.views.get_storage_provider",
        get_test_storage_provider({"REMOVE_RETURN": False}),
    )
    def test_delete_storage_error(self):
        response = self.client.delete(self.url)
        self.assertEqual(404, response.status_code)

    @patch("smoothglue.file_uploader.models.DocumentStoreConfiguration.get_storage_provider")
    def test_get_with_stored_config(self, mocked_get_storage_provider):
        mocked_get_storage_provider.return_value = TestStorageProvider(
            {"DOWNLOAD_RETURN": BytesIO(self.file_kwargs["content"])}
        )

        response = self.client.get(self.storedDocumentUrl)
        self.assertEqual(200, response.status_code)
        self.assertTrue(response.as_attachment)
        self.assertEqual(b"".join(response.streaming_content), self.text_file.read())

    @patch("smoothglue.file_uploader.models.DocumentStoreConfiguration.get_storage_provider")
    def test_delete_with_stored_config(self, mocked_get_storage_provider):
        mocked_get_storage_provider.return_value = TestStorageProvider({"REMOVE_RETURN": True})

        response = self.client.delete(self.storedDocumentUrl)
        self.assertEqual(204, response.status_code)

        # unable to remove because Document does not exist
        response = self.client.delete(self.storedDocumentUrl)
        self.assertEqual(404, response.status_code)
