import errno
import logging
import urllib.parse
from pathlib import Path
from uuid import UUID

from arkindex.exceptions import ErrorResponse
from rich.progress import Progress

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.upload import db
from arkindex_cli.commands.upload.alto import get_element_type
from arkindex_cli.commands.upload.cache import Cache
from arkindex_cli.commands.upload.exceptions import UploadProcessingError
from arkindex_cli.commands.upload.mets.parser import RootMetsElement
from arkindex_export import create_database

logger = logging.getLogger(__name__)


def trailing_slash_url(value):
    """Check an URL ends with a /"""
    assert isinstance(value, str)
    parts = urllib.parse.urlparse(value)
    assert parts.scheme in ("http", "https")
    if parts.path:
        assert parts.path.endswith("/"), "Must end with a /"
    return value


def trailing_slash_str(value):
    """Check an optional string ends with a /"""
    if value:
        assert isinstance(value, str)
        assert value.endswith("/"), "Must end with a /"
    return value


def add_mets_parser(subcommands):
    mets = subcommands.add_parser(
        "mets",
        description="Upload METS XML documents to Arkindex.",
        help="Upload METS XML documents to Arkindex.",
    )
    mets.add_argument(
        "path",
        help="Path to a METS file.",
        type=Path,
    )

    destination = mets.add_mutually_exclusive_group(required=True)
    destination.add_argument(
        "--parent-id",
        help="UUID of a parent folder under which elements will be created.",
        type=UUID,
    )
    destination.add_argument(
        "--db",
        dest="database_path",
        help="Path to a SQLite database to upload METS XML documents instead of using the Arkindex API.",
        type=Path,
    )
    mets.add_argument(
        "--parent-name",
        help="Name of a parent folder under which elements will be created. Only used when creating a SQLite database.",
        type=str,
        default="METS upload from CLI",
    )

    mets.add_argument(
        "--iiif-base-url",
        help="Base URL of the IIIF server where the images used by the METS file are exposed",
        type=trailing_slash_url,
        default="https://europe-gamma.iiif.teklia.com/iiif/2/",
    )
    mets.add_argument(
        "--iiif-prefix",
        help="Prefix on the IIIF server behind which the images used by the METS file are exposed",
        type=trailing_slash_str,
    )
    mets.add_argument(
        "--dpi-x",
        help="Horizontal resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    mets.add_argument(
        "--dpi-y",
        help="Vertical resolution of the image, in dots per inch, to be used for ALTO files using coordinates in tenths of millimeters.\n"
        "Strictly positive integer. Ignored for files using coordinates in pixels.",
        type=int,
    )
    mets.add_argument(
        "--skip-metadata",
        help="Skipping METS metadata publication, speeds up a lot the execution time",
        action="store_true",
    )
    mets.add_argument(
        "--worker-run-id",
        help="Worker Run used to publish elements, transcriptions and metadata in bulk.",
        type=UUID,
        required=True,
    )
    mets.add_argument(
        "--alto",
        action="store_true",
        help="Whether or not to publish ALTO files as well",
    )
    mets.add_argument(
        "--ignore-types",
        help="Element types found in the METS file to ignore.",
        type=str,
        nargs="+",
        default=[],
    )
    mets.set_defaults(func=run)


def run(
    path: Path,
    iiif_base_url: str,
    worker_run_id: UUID,
    parent_id: UUID | None = None,
    parent_name: str | None = "METS upload from CLI",
    database_path: Path | None = None,
    iiif_prefix: str | None = None,
    dpi_x: int | None = None,
    dpi_y: int | None = None,
    skip_metadata: bool = False,
    alto: bool = False,
    ignore_types: list[str] = [],
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
):
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles(gitlab_secure_file).get_api_client_or_exit(profile_slug)

    # Parse TOC
    if not path.exists():
        logger.error(f"Cannot find METS at {path}")
        return errno.ENOENT
    root = RootMetsElement(path, iiif_base_url, iiif_prefix, dpi_x, dpi_y)

    corpus_id = None
    if database_path:
        database_path.parent.mkdir(exist_ok=True, parents=True)
        create_database(database_path, db.EXPORT_VERSION)

        # Create a worker run (and its worker version)
        worker_run = client.request("RetrieveWorkerRun", id=worker_run_id)
        db.get_or_create_worker_version(worker_run["worker_version"])
        db.get_or_create_worker_run(worker_run)

        # Get or create a fake parent folder
        parent_id = UUID(
            db.get_or_create_element(
                name=parent_name, type="folder", worker_run=worker_run
            ).id
        )
    else:
        # Check the existence of the top element
        with Progress(transient=True) as progress:
            progress.add_task(start=False, description="Fetching parent element")
            try:
                parent = client.request("RetrieveElement", id=parent_id)
            except ErrorResponse as e:
                logger.error(
                    f"Could not retrieve parent element {parent_id}: HTTP {e.status_code} - {e.content}"
                )
                return errno.EREMOTEIO

        corpus_id = parent["corpus"]["id"]

    # Check that every type used by the tree is available on the corpus
    for type_slug in root.list_required_types():
        get_element_type(
            client, type_slug, corpus_id, types_dict=None, create_types=True
        )

    # Publish ALTO files
    if alto:
        try:
            root.publish_alto(
                arkindex_client=client,
                parent_id=parent_id,
                corpus_id=corpus_id,
                publish_metadata=not skip_metadata,
                worker_run_id=worker_run_id,
                ignore_types=ignore_types,
            )
        except UploadProcessingError:
            logger.error(f"Failed to publish ALTO file @ {path}")
            return

    # Setup cache next to mets file
    cache = Cache(path.with_suffix(".json"))

    # Publish all elements recursively starting from root
    logger.info(f"Publishing METS file @ {path}…")
    try:
        root.publish(
            cache=cache,
            arkindex_client=client,
            parent_id=parent_id,
            corpus_id=corpus_id,
            publish_metadata=not skip_metadata,
            worker_run_id=worker_run_id,
            ignore_types=ignore_types,
        )
    except UploadProcessingError:
        logger.error(f"Failed to publish METS file @ {path}")
