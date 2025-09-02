import logging
from pathlib import Path
from uuid import UUID

from rich.progress import Progress

import magic
from arkindex_cli.auth import Profiles
from arkindex_cli.uploads import MultipartUpload

logger = logging.getLogger(__name__)


def add_data_file_parser(subcommands):
    data_file_parser = subcommands.add_parser(
        "data_file",
        description="Upload a data file to Arkindex.",
    )
    data_file_parser.add_argument(
        "file_path",
        help="Path to the local file to upload.",
        type=Path,
    )
    data_file_parser.add_argument(
        "--corpus-id",
        help="ID of the Arkindex corpus to upload a data file on.",
        type=UUID,
    )
    data_file_parser.add_argument(
        "--name",
        help="The name of the data file. If left blank, the file name without the extension is used instead.",
        default=None,
        type=str,
    )
    data_file_parser.add_argument(
        "--chunk-size",
        help="Upload chunks of a specific size (in MiB).",
        default=None,
        type=int,
    )
    data_file_parser.add_argument(
        "--stream",
        help="Stream the file rather than storing chunks in memory.",
        default=False,
        action="store_true",
    )
    data_file_parser.set_defaults(func=run)


def run(
    file_path,
    corpus_id,
    name,
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

    name = name or file_path.stem

    corpus = client.request("RetrieveCorpus", id=corpus_id)

    logger.info(f"Creating new data file {name} on corpus {corpus['name']}")

    mime_type = magic.from_file(file_path, mime=True)
    size = file_path.stat().st_size
    datafile = client.request(
        "CreateDataFile",
        body={
            "name": name,
            "corpus": str(corpus_id),
            "content_type": mime_type,
            "size": size,
        },
    )

    logger.info(f"Uploading data to DataFile {datafile['id']}")

    multipart = MultipartUpload(
        client=client,
        file_path=file_path,
        object_type="data_file",
        object_id=datafile["id"],
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
        logger.info("Successfully uploaded data file.")
