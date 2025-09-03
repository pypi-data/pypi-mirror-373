import uuid
from typing import TypedDict, Callable

from django.test import TestCase

from tests.utils import (
    TestPostProcessor,
    TestValidator,
    get_test_document_and_file,
    SimpleTestTypedDict,
    ComplexTestTypedDict,
    TestStorageProvider,
)
from smoothglue.file_uploader.utils import (
    check_type,
    convert_bytes_to_file_size,
    dict_matches_type,
    is_valid_uuid,
)


class TestUtils(TestCase):
    def test_convert_bytes_to_file_size(self):
        self.assertEqual("0 B", convert_bytes_to_file_size(None))
        self.assertEqual("0 B", convert_bytes_to_file_size(-1))
        self.assertEqual("0 B", convert_bytes_to_file_size(0))
        self.assertEqual("99.0 B", convert_bytes_to_file_size(99))
        self.assertEqual("97.66 KB", convert_bytes_to_file_size(99999))
        self.assertEqual("95.37 MB", convert_bytes_to_file_size(99999999))
        self.assertEqual("93.13 GB", convert_bytes_to_file_size(99999999999))
        self.assertEqual("90.95 TB", convert_bytes_to_file_size(99999999999999))
        self.assertEqual("1024.0 TB", convert_bytes_to_file_size(1125899906842620))
        self.assertEqual("Very Large", convert_bytes_to_file_size(1125899906842621))

    def test_is_valid_uuid(self):
        self.assertTrue(is_valid_uuid(str(uuid.uuid4())))
        self.assertFalse(is_valid_uuid("foo"))

    def test_check_type_valid(self):
        self.assertIsNone(check_type(10, int))
        self.assertIsNone(check_type("test", str))
        self.assertIsNone(check_type([1, 2], list))
        self.assertIsNone(check_type({"a": 1}, dict))

    def test_check_type_invalid(self):
        with self.assertRaises(ValueError):
            check_type(10, str, "Error")
        with self.assertRaises(ValueError):
            check_type("test", int, "Error")

    def test_check_type_valid_typeddict(self):
        data = {"name": "Tony", "age": 30}
        self.assertIsNone(check_type(data, SimpleTestTypedDict))

    def test_check_type_invalid_typeddict_value_type(self):
        data = {"name": "Bruce", "age": "30"}  # age should be int
        self.assertRaises(ValueError, check_type, data, SimpleTestTypedDict)

    def test_dict_matches_type_valid(self):
        data = {"name": "Steve", "age": 40}
        self.assertTrue(dict_matches_type(data, SimpleTestTypedDict))

    def test_dict_matches_type_valid_complex(self):
        data = {
            "id": 1,
            "user_data": {"name": "Diana", "age": 35},
            "is_active": True,
            "description": "A test user",
            "tags": ["python", "test"],
        }
        self.assertTrue(dict_matches_type(data, ComplexTestTypedDict))

    def test_dict_matches_type_complex_optional_keys_missing(self):
        data = {
            "id": 1,
            "user_data": {"name": "Diana", "age": 35},
            "is_active": True,
        }  # description and tags are missing
        self.assertTrue(dict_matches_type(data, ComplexTestTypedDict))

    def test_dict_matches_type_invalid_complex(self):
        data = {
            "id": 1,
            "user_data": {"name": "Diana", "age": "35"},
            "is_active": True,
            "description": "A test user",
            "tags": ["test"],
        }
        self.assertRaises(ValueError, dict_matches_type, data, ComplexTestTypedDict)

    def test_dict_matches_type_invalid_typedef(self):
        class BadType(TypedDict):
            foo: Callable

        self.assertRaises(ValueError, dict_matches_type, {"foo": "bar"}, BadType)

    def test_dict_matches_type_no_raise_error(self):
        class BadType(TypedDict):
            foo: Callable

        self.assertFalse(dict_matches_type({"foo": "bar"}, BadType, False))


class TestTestUtils(TestCase):
    def setUp(self):
        self.document, self.file = get_test_document_and_file()

    def test_test_validator(self):
        self.assertTrue(TestValidator.validate_uploaded_file(self.document, self.file))

    def test_test_post_processor(self):
        # Just checking that it runs without error
        TestPostProcessor.process_uploaded_file(self.document, self.file)

    def test_test_storage_provider(self):
        self.assertTrue(
            TestStorageProvider({"DUPLICATE_RETURN": True}).duplicate_document("foo", "bar")
        )
        self.assertFalse(
            TestStorageProvider({"DUPLICATE_RETURN": False}).duplicate_document("foo", "bar")
        )
