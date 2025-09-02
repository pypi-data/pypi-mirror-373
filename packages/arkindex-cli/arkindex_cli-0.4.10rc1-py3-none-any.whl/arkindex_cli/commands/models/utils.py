import hashlib
import logging
import os
import tarfile
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import NewType
from uuid import UUID

import requests
import zstandard as zstd
from arkindex import ArkindexClient
from arkindex.exceptions import ErrorResponse

from teklia_toolbox.requests import should_verify_cert

logger = logging.getLogger(__name__)
CHUNK_SIZE = 1024


FilePath = NewType("FilePath", Path)
Hash = NewType("Hash", str)
FileSize = NewType("FileSize", int)
Archive = tuple[FilePath, FileSize, Hash]

# Teklia's convention
DEFAULT_MODEL_DIR = Path("/usr/share/teklia")


def build_clean_payload(**kwargs):
    """
    Remove null attributes from an API body payload
    """
    return {key: value for key, value in kwargs.items() if value is not None}


def find_model_path(config_model_path: Path) -> Path:
    """We try the following paths in that order and return the first that exists
    - /usr/share/teklia/${config_model_path}
    - ${config_model_path}
    - ./models/${config_model_path}
    """

    # Get relative path to model
    relative_path = config_model_path
    # If it follows Teklia's convention, we remove the prefix
    if str(relative_path).startswith(str(DEFAULT_MODEL_DIR)):
        relative_path = Path(relative_path).relative_to(DEFAULT_MODEL_DIR)

    # Tested paths
    possible_paths = [
        DEFAULT_MODEL_DIR / relative_path,
        Path(".") / relative_path,
        Path("models") / relative_path,
    ]
    for path_to_model in possible_paths:
        if path_to_model.exists():
            logger.info(f"Found model in {path_to_model}.")
            return path_to_model


@contextmanager
def create_archive(
    path: FilePath,
) -> Archive:
    """
    Create tar archive with everything that's in the folder at path
    Keep the hierarchy but parent folder should not be included
    Save the absolute path of each file added to compute their hash later
    """

    assert path.is_dir(), "This path must resolve to a directory"

    # Remove extension from the model filename
    _, path_to_tar_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar")

    with tarfile.open(path_to_tar_archive, "w") as tar:
        tar.add(name=path, arcname=".")

    # Compress the archive
    _, path_to_zst_archive = tempfile.mkstemp(prefix="teklia-", suffix=".tar.zst")

    compressor = zstd.ZstdCompressor(level=3)
    archive_hasher = hashlib.md5()
    with (
        open(path_to_zst_archive, "wb") as archive_file,
        open(path_to_tar_archive, "rb") as model_data,
    ):
        for model_chunk in iter(lambda: model_data.read(CHUNK_SIZE), b""):
            compressed_chunk = compressor.compress(model_chunk)
            archive_hasher.update(compressed_chunk)
            archive_file.write(compressed_chunk)

    # Remove the tar archive
    os.remove(path_to_tar_archive)

    # Get archive size and hash
    size = os.path.getsize(path_to_zst_archive)
    archive_hash = archive_hasher.hexdigest()

    yield path_to_zst_archive, size, archive_hash

    # Remove the zstd archive
    os.remove(path_to_zst_archive)


def create_or_retrieve_model(client: ArkindexClient, name: str):
    """Create a new model or retrieve the id of the existing one (with the same name)"""
    try:
        r = client.request("CreateModel", body={"name": name})
        # New model was created
        return r["id"]
    except ErrorResponse as e:
        r = e.content
        status = e.status_code
        if status == 400:
            # Model already exists and user has access to it. The model id was returned in payload
            return r["id"]
        elif status == 403:
            # Model exists but user has no access to it, raise
            raise Exception(
                f"You do not have the required rights to create a new model version for model {name}."
            )
        else:
            raise


def create_model_version(
    client: ArkindexClient,
    model_id: str,
    tag: str | None = None,
    description_path: Path | None = None,
    configuration: dict | None = {},
    parent: UUID | None = None,
) -> dict:
    model_version_body = build_clean_payload(
        tag=tag,
        configuration=configuration,
        parent=str(parent) if parent else None,
    )
    if description_path:
        assert (
            description_path.exists()
        ), f"Model version description was not found @ {description_path}"
        model_version_body["description"] = description_path.read_text()

    # Create a new model version with optional base attributes
    try:
        return client.request(
            "CreateModelVersion",
            id=model_id,
            body=model_version_body,
        )
    except ErrorResponse as e:
        if e.status_code == 400:
            if "model" in e.content:
                raise Exception(
                    f"Model ({model_id}) is archived. You cannot create a new model version."
                )
            elif "non_field_errors" in e.content:
                raise Exception(
                    f"A version for this model ({model_id}) with this tag ({tag}) already exists."
                )
        raise e


def upload_to_s3(archive_path: str, model_version_details: dict) -> None:
    s3_put_url = model_version_details.get("s3_put_url")
    logger.info("Uploading to s3...")
    # Upload the archive on s3
    with open(archive_path, "rb") as archive:
        r = requests.put(
            url=s3_put_url,
            data=archive,
            headers={"Content-Type": "application/zstd"},
            verify=should_verify_cert(s3_put_url),
        )
    r.raise_for_status()


def validate_model_version(
    client: ArkindexClient,
    model_version_id: str | UUID,
    size: int,
    archive_hash: str,
) -> dict:
    # Sets the model version as `Available`, once its archive has been uploaded to S3.
    logger.info("Validating the model version...")

    try:
        return client.request(
            "PartialUpdateModelVersion",
            id=model_version_id,
            body={
                "state": "available",
                "size": size,
                "archive_hash": archive_hash,
            },
        )
    except ErrorResponse as e:
        if e.status_code != 400:
            logger.error(
                f"Failed validating model version: {e.status_code} -- {e.content}"
            )

        if "state" in e.content:
            logger.error(e.content["state"][0])
        if "size" in e.content:
            for error in e.content["size"]:
                logger.error(f"Failed to check model version archive size: {error}.")
        if "archive_hash" in e.content:
            for error in e.content["archive_hash"]:
                logger.error(f"Failed to check model version archive hash: {error}.")

        raise
