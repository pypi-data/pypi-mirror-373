import logging
from datetime import datetime
from pathlib import Path

from arkindex.exceptions import ErrorResponse
from rich.progress import track

from arkindex_cli.auth import Profiles

logger = logging.getLogger(__name__)


def add_import_parser(subcommands) -> None:
    import_parser = subcommands.add_parser(
        "import",
        help="Add elements to your Arkindex selection, from a list of UUIDs",
        description="""
            Populate your Arkindex selection with elements from a file containing a list of UUIDs.
            The elements are added in batches, 50 elements at time by default.
        """,
    )
    import_parser.add_argument(
        "file",
        type=Path,
        help="Path to a file containing element UUIDs (one per line)",
    )
    import_parser.add_argument(
        "--batch-size",
        default=50,
        type=int,
        help="""
            Size of the batches of elements to be added to the selection. Default to 50 elements.
            Setting this batch size too high might cause the command to fail.
        """,
    )
    import_parser.add_argument(
        "--clear",
        action="store_true",
        help="Empty the selection before adding elements to it",
    )
    import_parser.add_argument(
        "--failures-file",
        type=Path,
        help="""
            Path to the file in which to write the UUIDs of eventual failed elements.
            Defaults to $CURRENT_DIRECTORY/failed_elements_$CURRENT_DATE.txt
        """,
        required=False,
    )
    import_parser.set_defaults(func=run)


def batch(iterable, n=1):
    length = len(iterable)
    if length == 0:
        return
    for ndx in track(range(0, length, n)):
        yield iterable[ndx : min(ndx + n, length)]


def run(
    file: Path,
    batch_size: int | None = 50,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
    clear: bool | None = False,
    failures_file: Path | None = None,
):
    profiles = Profiles(gitlab_secure_file)
    client = profiles.get_api_client_or_exit(profile_slug)

    assert batch_size > 0, "Batch size must be a positive integer superior to 0"

    ids = file.read_text().strip().splitlines()
    total_count = len(ids)
    assert total_count, f"{file} is empty"

    failures = []

    if clear:
        try:
            client.request("RemoveSelection", body={})
            logger.info("Selection cleared!")
        except ErrorResponse as e:
            logger.error(f"Failed clearing selection: {e.status_code} -- {e.content}")
            # Put all the element ids in failures, and empty ids so that the block below is skipped
            failures = ids
            ids = []

    for batch_ids in batch(ids, batch_size):
        try:
            client.request("AddSelection", body={"ids": batch_ids})
        except ErrorResponse as e:
            logger.error(
                f"Failed adding {len(batch_ids)} elements to selection: {e.status_code} -- {e.content}"
            )
            failures.extend(batch_ids)

    if len(failures):
        if not failures_file:
            failures_file = (
                Path.cwd() / f"failed_elements_{datetime.now().isoformat()}.txt"
            )
        failures_file.write_text("\n".join(failures))

        logger.warn(
            f"{len(failures)} elements (out of {total_count}) failed to be added to the selection. Their UUIDs have been written to {failures_file}."
        )

    successes = total_count - len(failures)
    if successes > 0:
        logger.info(f"Successfully added {successes} elements to the selection.")
