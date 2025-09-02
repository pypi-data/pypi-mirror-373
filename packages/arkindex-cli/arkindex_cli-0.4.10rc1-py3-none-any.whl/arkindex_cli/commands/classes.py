import argparse
import csv
from pathlib import Path
from uuid import UUID

from arkindex.exceptions import ErrorResponse
from rich import print
from rich.progress import Progress, track

from arkindex_cli.auth import Profiles


def add_classes_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "classes",
        help="Manage ML classes on an Arkindex instance.",
        description="Manage ML classes on an Arkindex instance.",
    )
    parser.add_argument(
        "corpus_id",
        help="The ID of the corpus whose classes you want to list",
        type=UUID,
    )
    parser.add_argument(
        "--output",
        type=argparse.FileType("w", encoding="UTF-8"),
        help="Path to the CSV file which will be created",
        default=f"{Path.cwd()}/classes.csv",
    )
    parser.set_defaults(func=run)


def run(
    corpus_id: UUID,
    output: Path,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        profiles = Profiles(gitlab_secure_file)
        client = profiles.get_api_client_or_exit(profile_slug)

    # Load all ML classes in the corpus
    # They are immediately written to the file
    writer = csv.writer(output)
    # Write header
    writer.writerow(("class_id", "class_name"))
    try:
        paginator = client.paginate("ListCorpusMLClasses", id=corpus_id)
        for cls in track(paginator, description="Loading ML Classes"):
            writer.writerow((cls["id"], cls["name"]))
    except ErrorResponse as e:
        # Handle Api errors
        if e.status_code == 404:
            print(f"[yellow]:warning: The corpus {corpus_id} was not found")
        else:
            print(f"[red]An API error occurred: {e.content}")
