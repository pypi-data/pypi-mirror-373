import logging
from pathlib import Path
from uuid import UUID

from rich.progress import Progress

from arkindex_cli.auth import Profiles
from arkindex_cli.uploads import MultipartUpload, file_digest

logger = logging.getLogger(__name__)


def add_model_version_parser(subcommands):
    model_version_parser = subcommands.add_parser(
        "model_version",
        description="Upload a model version to Arkindex.",
    )
    model_version_parser.add_argument(
        "file_path",
        help="Path to the local file to upload.",
        type=Path,
    )
    model_version_parser.add_argument(
        "--chunk-size",
        help="Upload chunks of a specific size (in MiB).",
        default=None,
        type=int,
    )
    model_version_parser.add_argument(
        "--stream",
        help="Stream the file rather than storing chunks in memory.",
        default=False,
        action="store_true",
    )
    exclusive_model_input = model_version_parser.add_mutually_exclusive_group(
        required=True
    )
    exclusive_model_input.add_argument(
        "--model-version-id",
        help="ID of the Arkindex model version to upload the file for.",
        default=None,
        type=UUID,
    )
    exclusive_model_input.add_argument(
        "--model-id",
        help="ID of the Arkindex model to create a new version on and upload its content.",
        type=UUID,
    )

    model_version_parser.set_defaults(func=run)


def run(
    file_path,
    model_version_id,
    model_id,
    chunk_size,
    stream,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
):
    if not file_path.exists() or not file_path.is_file():
        logger.error(f"Path does not exist or is not a file: {file_path}")
        return 1

    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles(gitlab_secure_file)
        profile = profiles.get_or_exit(profile_slug)
        client = profiles.get_api_client(profile)

    if model_id:
        with file_path.open("rb") as f, Progress(transient=True) as progress:
            progress.add_task(start=False, description="Calculating total MD5 hash")
            md5 = file_digest(f, "md5").hexdigest()
        model_version = client.request(
            "CreateModelVersion",
            id=model_id,
            body={
                "size": file_path.stat().st_size,
                "archive_hash": md5,
            },
        )
        model_version_id = model_version["id"]
        logger.info(f"Created a new model version: {model_version_id}.")

    logger.info(f"Uploading file for model version {model_version_id}")

    multipart = MultipartUpload(
        client=client,
        file_path=file_path,
        object_type="model_version",
        object_id=str(model_version_id),
        use_file_objects=stream,
        chunk_size=chunk_size,
    )
    try:
        multipart.upload()
        multipart.complete()
    except Exception:
        multipart.abort()
        raise
    else:
        logger.info("Successfully uploaded model version.")
