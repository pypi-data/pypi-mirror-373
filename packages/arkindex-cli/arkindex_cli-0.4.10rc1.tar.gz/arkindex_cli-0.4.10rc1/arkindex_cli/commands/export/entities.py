import argparse
import csv
import logging
import sys
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console
from rich.progress import track

from arkindex_cli.commands.export.utils import MANUAL_SOURCE, uuid_or_manual
from arkindex_export import (
    Element,
    EntityType,
    Transcription,
    TranscriptionEntity,
    WorkerRun,
    open_database,
)
from peewee import Value

logger = logging.getLogger(__name__)


def get_transcription_entities_queries(instance_url, element_type, worker_version_ids):
    query = (
        TranscriptionEntity.select(
            TranscriptionEntity.transcription_id.alias("transcription_id"),
            Transcription.element_id.alias("element_id"),
            (
                Value(f"{instance_url.rstrip('/')}/element/").concat(
                    Transcription.element_id
                )
            ).alias("element_url"),
            TranscriptionEntity.id.alias("transcription_entity_id"),
            EntityType.name.alias("entity_type"),
            TranscriptionEntity.text.alias("entity_value"),
            TranscriptionEntity.confidence,
            TranscriptionEntity.length,
            TranscriptionEntity.offset,
        )
        .join(EntityType)
        .switch(TranscriptionEntity)
        .join(Transcription)
        .order_by(TranscriptionEntity.transcription_id, TranscriptionEntity.id)
        .dicts()
    )
    if element_type:
        query = query.join(Element, on=Transcription.element).where(
            Transcription.element.type == element_type
        )
    for version_id in worker_version_ids:
        if version_id == MANUAL_SOURCE:
            yield query.where(TranscriptionEntity.worker_run_id.is_null())
        else:
            yield (
                query.switch(TranscriptionEntity)
                .join(WorkerRun)
                .where(WorkerRun.worker_version_id == version_id)
            )
    if not len(worker_version_ids):
        yield query


def retrieve_transcription_entities(instance_url, element_type, worker_version_ids):
    queries = get_transcription_entities_queries(
        instance_url, element_type, worker_version_ids
    )
    # Go through the queries until something is found
    for query in queries:
        transcription_entities = list(query)
        if len(transcription_entities):
            return transcription_entities
    return []


def run(
    database_path: Path,
    output_path: Path,
    instance_url: str,
    type: str | None = None,
    worker_version_id: list[str] | None = [],
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
):
    database_path = database_path.absolute()
    assert database_path.is_file(), f"Database at {database_path} not found"

    parsed_url = urlparse(instance_url)
    assert parsed_url.scheme and parsed_url.netloc, f"{instance_url} is not a valid url"

    csv_header = [
        "transcription_id",
        "element_id",
        "element_url",
        "transcription_entity_id",
        "entity_type",
        "entity_value",
        "confidence",
        "length",
        "offset",
    ]

    open_database(database_path)
    tr_entities = retrieve_transcription_entities(instance_url, type, worker_version_id)

    if not len(tr_entities):
        logger.info("No transcription entities to export.")
        return

    writer = csv.DictWriter(output_path, fieldnames=csv_header)
    writer.writeheader()
    for tr_entity in track(
        tr_entities,
        description="Exporting transcription entities",
        total=TranscriptionEntity.select().count(),
        console=Console(file=sys.stderr),
    ):
        writer.writerow(tr_entity)

    logger.info(
        f"Exported transcription entities successfully written to {output_path.name}."
    )


def add_entities_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "entities",
        help="Export entities from a given Arkindex project.",
        description="Export a project's transcription entities.",
    )
    parser.add_argument(
        "--output",
        help="Path to the CSV file which will be created",
        default=sys.stdout,
        type=argparse.FileType("w", encoding="UTF-8"),
        dest="output_path",
    )
    parser.add_argument(
        "--instance-url",
        help="URL of the Arkindex instance of the exported project.",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--type",
        type=str,
        help="Only export entities from elements of the specified type.",
    )
    parser.add_argument(
        "--worker-version-id",
        type=uuid_or_manual,
        help=f"""
            '{MANUAL_SOURCE}' or UUIDs of the worker version(s) that produced the entities to be exported. The order in which
            the worker versions are given as argument acts as a preference order: if there are entities from multiple
            worker versions on an element, the ones from the worker version at the earliest position in this list of UUIDs
            will be exported.
        """,
        nargs="+",
        default=[],
    )
    parser.set_defaults(func=run)
