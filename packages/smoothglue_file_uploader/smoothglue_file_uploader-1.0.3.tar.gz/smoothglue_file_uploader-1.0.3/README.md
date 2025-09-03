# SmoothGlue Django File Uploader

A Django app providing secure, pluggable uploads to S3, MinIO, or local storage with validation, checksums, and post-processing. Built for regulated and edge environments from the ground up.

## Overview

`smoothglue_file_uploader` simplifies the process of handling file uploads in a Django project. The core problem it solves is abstracting the storage backend, allowing developers to switch between local development, staging, and production environments without changing application code. You can configure it once in `settings.py` and have your file uploads seamlessly route to the correct storage solution.

### Key Features

* **Multiple Storage Backends:** Natively supports Local Filesystem, Amazon S3, and MinIO.
* **Easy Configuration:** A single settings dictionary to control all storage options.
* **On-the-fly Validation:** Allows custom configurations to validate files prior to them being uploaded.
* **Ease of Access:** Easily upload, download, delete or duplicate files in any supported files stores.

## Installation

### Prerequisites

* Python 3.12+
* Django 4.2+
* Django REST Framework 3.14+

### Install App From PyPI Package (Official Use)

1. Before installing the package, make sure that there is a virtual environment set up inside of the Django project you want to install the app into.

2. Use pip and the following command inside the Django project:
   ```python
   pip install smoothglue_file_uploader
   ```

3. Update the `settings.py` file inside that Django project to point to the new app name:

   ```python
   INSTALLED_APPS = [
     "smoothglue_file_uploader",
     ...,
   ]
   ```


4. Update the `urls.py` file inside that Django project to point to the new app name: :

   ```python
   urlpatterns = [
     path("", include("smoothglue_file_uploader.urls")),
     ...,
   ]
   ```

5. Run the development server to confirm the project continues to work.

## Examples

### Usage Examples

#### Download
```python
    storage_provider, _ = get_storage_provider()
    doc = Document.objects.get(id=instance.id)

    data = storage_provider.download_document(doc.path)
```

#### Upload
```python
    storage_provider, _ = get_storage_provider()
    path = "foo/bar"
    storage_provider.upload_document(path, file_obj)
```

#### Delete
```python
    storage_provider, _ = get_storage_provider()
    doc = Document.objects.get(id=instance.id)

    storage_provider.delete_document(doc.path)
```

#### Duplicate
```python
    storage_provider, _ = get_storage_provider()
    old_doc = Document.objects.get(id=instance.id)
    new_uuid = str(uuid.uuid4())
    new_path = f"path/{new_uuid}"

    duplicate_success = storage_provider.duplicate_document(old_doc.path, new_path)
```

### API Examples

| URL Path    | HTTP Method | Description |
| -------- | ------- | ------- |
| `/`  | `GET`    | Lists documents. A `reference_id` (UUID) must be provided as a query parameter to retrieve all files associated with that ID. |
| `/` | `POST`     | Uploads a new file. The request must be a multipart form containing a `file` and a `reference_id`. |
| `/<uuid:file_id>/` | `GET`     | Downloads the content of the specified file as a file attachment. |
| `/<uuid:file_id>/` | `PATCH`     | Updates the metadata (e.g., name, category) of the specified file. |
| `/<uuid:file_id>/` | `DELETE`     | Deletes the specified file from the backend storage and the database. |


### Settings Example

``` python
UPLOAD_STORAGE_PROVIDER_CONFIG = {
    "minio": {
        "PROVIDER_CLASS": "smoothglue.file_uploader.storage_providers.minio.MinioProvider",
        "PROVIDER_CONFIG": {
            "ACCESS_KEY": os.getenv("ACCESS_KEY"),
            "HOST": os.getenv("HOST"),
            "PORT": int(os.getenv("MINIO_PORT")),
            "SECRET_KEY": os.getenv("SECRET_KEY"),
            "SECURE": True if os.getenv("MINIO_PROTOCOL") == "https" else False,
            "BUCKET_NAME": os.getenv("BUCKET_NAME"),
            "REGION": os.getenv("REGION"),
        },
    },
    "s3-sts-web-id": {
        "PROVIDER_CLASS": "smoothglue.file_uploader.storage_providers.s3.STSWebIdentityS3Provider",
        "PROVIDER_CONFIG": {
            "ROLE_ARN": os.getenv("ROLE_ARN", None),
            "WEB_IDENTITY_TOKEN_FILE": os.getenv("WEB_IDENTITY_TOKEN_FILE", None),
            "BUCKET_NAME": os.getenv("BUCKET_NAME", None),
        },
    },
    "local": {
        "PROVIDER_CLASS": "smoothglue.file_uploader.storage_providers.local.LocalFileSystemProvider",
        "PROVIDER_CONFIG": {},
    },
}

SELECTED_STORAGE_PROVIDER = os.getenv("DEFAULT_STORAGE_PROVIDER")

UPLOAD_STORAGE_PROVIDER_CONFIG["default"] = UPLOAD_STORAGE_PROVIDER_CONFIG[
    SELECTED_STORAGE_PROVIDER
]
```

## Settings Overview
```python
# This setting defines the configs for the stores of smoothglue.file_uploader.storage_providers.base.StorageProvider
# which provides an interface for interacting with some storage providers. Each storage provider may come with its own
# required settings in the PROVIDER_CONFIG.

# "default" is what all files will be uploaded to without specifying a different key
UPLOAD_STORAGE_PROVIDER_CONFIG = {
   "default": {
   "PROVIDER_CLASS": "smoothglue.file_uploader.storage_providers.s3.BaseS3StorageProvider",
   "PROVIDER_CONFIG": {...}
},
...}

# Required keys for smoothglue.file_uploader.storage_providers.s3.BaseS3StorageProvider
"BUCKET_NAME" = "..." # S3 bucket to store uploaded files in

# Required keys for smoothglue.file_uploader.storage_providers.s3.STSS3Provider
"ROLE_ARN" = "..." # IAM role for the credentials used to access S3
"BUCKET_NAME" = "..." # S3 bucket to store uploaded files in

# Required keys for smoothglue.file_uploader.storage_providers.s3.STSWebIdentityS3Provider
"ROLE_ARN" = "..." # IAM role for the credentials used to access S3
"WEB_IDENTITY_TOKEN_FILE" = "/path/to/identity/token.file"
"BUCKET_NAME" = "..." # S3 bucket to store uploaded files in

# Required keys for smoothglue.file_uploader.storage_providers.minio.MinioProvider
"ACCESS_KEY" = "..." # Access key for minio "user"
"HOST" = "minio.example.com" # Hostname or ip address of minio server
"PORT" = "1234" # (Optional) port minio service listens on if different from default
"SECRET_KEY" = "..." # Secret key for minio "user"
"SECURE" = True # True if Minio uses SSL, false otherwise
"BUCKET_NAME" = "..." # Minio bucket to store uploaded files in

# A dictionary of file extensions to post-processor classes. These post-processor classes are ran after a file has been
# successfully uploaded to the configured storage provider
UPLOAD_POST_PROCESSORS = {
    # Will be applied to EVERY file uploaded
    "*": "smoothglue.file_uploader.post_processor.DefaultUploadProcessor",
    # Will be applied to all files uploaded that end in `.txt`
    "txt": "some.other.post.processing.class"
}

# A dictionary of file extensions to file validator classes. These file validator classes are ran before a file is
# uploaded and may raise a validation error (resulting in 400 response).
UPLOAD_VALIDATORS = {
    # Will be applied to EVERY file uploaded
    "*": "smoothglue.file_uploader.validators.DefaultValidator",
    # Will be applied to all files uploaded that end in `.txt`
    "txt": "some.other.validation.class",
}
```

**Local File System Storage Provider**

Used for running a simple upload to the file system. Defaults go to the Django MEDIA_ROOT configuration, otherwise you can specify the location using `UPLOAD_PATH` in the config.

```
UPLOAD_STORAGE_PROVIDER_CONFIG = {
   "default": {
   "PROVIDER_CLASS": "smoothglue.file_uploader.storage_providers.local.LocalFileSystemProvider",
   "PROVIDER_CONFIG": {"UPLOAD_PATH": "/tmp/uploaded_files"}
},
...
}
```

**Optional File Checksum validation**

```
# calculate sha256 file checksum and inserts it to the db. May cause performance issue for large file uploads
CALCULATE_CHECKSUM: bool = True

# Enforce checksum validation if an existing file with the same checksum exist in the document table.

UPLOAD_VALIDATORS={
    "*": "smoothglue.file_uploader.validators.DuplicateFileValidator"
}
```

## License

This project is licensed under a Proprietary License. See the [LICENSE](./LICENSE) file for more details.
