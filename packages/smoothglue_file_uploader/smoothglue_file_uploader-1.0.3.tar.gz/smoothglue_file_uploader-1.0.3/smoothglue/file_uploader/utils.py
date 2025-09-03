import logging
from hashlib import file_digest
from typing import Optional, Any, TypedDict, _TypedDictMeta
from uuid import UUID

import math

logger = logging.getLogger(__name__)


def convert_bytes_to_file_size(bytes_size: Optional[int]) -> str:
    """
    Build human-readable file size
    Args:
        bytes_size(Optional[int]): file size in bytes

    Returns:
        str: Human-readable file size
    """
    if not bytes_size or bytes_size <= 0:
        return "0 B"

    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(bytes_size, 1024)))

    if i >= len(size_name):
        return "Very Large"

    power = math.pow(1024, i)
    size = round(bytes_size / power, 2)

    return f"{size} {size_name[i]}"


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """
    Determines if a UUID is valid

    Args:
        uuid_to_test: Value to validate
        version: UUID version

    Returns:
        bool: True if UUID is valid, else False
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test


BUF_SIZE = 65536


def generate_checksum(file):
    """
    Calculate sha256 file checksum for a file object
    """
    file.seek(0)
    file_hash = file_digest(file, "sha256").hexdigest()
    file.seek(0)
    return file_hash


def check_type(value: Any, type_def: type, error_str: str = "{value} is not of type {type}"):
    """
    Checks that a given value is of a given type

    Args:
        value (Any): Value to check
        type_def (type): Type to check
        error_str (str, optional): Error message. Defaults to "{value} is not of type {type}"

    Raises:
        ValueError: If value is not the provided type

    Returns:

    """
    if isinstance(type_def, _TypedDictMeta):
        dict_matches_type(value, type_def, raise_exception=True)
    elif not isinstance(value, type_def):
        raise ValueError(error_str.format(value=value, type_def=type_def))


def dict_matches_type(value: dict, typed_dict: type[TypedDict], raise_exception=True) -> bool:
    """
    Checks if a dictionary matches the structure of a given TypedDict

    Args:
        value (dict): Value to check
        typed_dict (type[TypedDict]): TypedDict to check against
        raise_exception (bool, optional): Raise exception if value does not match. Defaults to True.

    Raises:
        ValueError: If value does not match the TypedDict specification

    Returns:
        bool: True if value matches the TypedDict specification, else False
    """
    try:
        check_type(value, dict)
        # Check that only keys defined are on the dict
        if undefined_keys := set(value.keys()) - set(typed_dict.__annotations__.keys()):
            raise ValueError(f"Key(s) not valid for {typed_dict.__name__}: {undefined_keys}")

        # Check that all values are the correct type
        for key, type_def in typed_dict.__annotations__.items():
            # Key is required
            if isinstance(type_def, type):
                if key not in value:
                    raise ValueError(f"Missing required key for {typed_dict.__name__}: {key}")
                check_type(
                    value[key], type_def, error_str=f"Value of {key} is not of type {'{type_def}'}"
                )
            # Key is not required
            elif type_def.__name__ == "NotRequired":
                if key in value:
                    check_type(
                        value[key],
                        type_def.__args__[0],
                        error_str=f"Value of {key} is not of type {'{type_def}'}",
                    )
            # TypedDict is misconfigured
            else:
                raise ValueError(f"{key} on {type_def.__name__} is not a type or NotRequired[type]")
        return True
    except ValueError as e:
        if raise_exception:
            raise e
        return False
