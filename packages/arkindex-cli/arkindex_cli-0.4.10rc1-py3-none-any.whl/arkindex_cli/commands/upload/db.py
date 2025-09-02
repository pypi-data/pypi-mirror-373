import logging
import uuid
from collections.abc import Iterator
from datetime import datetime
from functools import cache
from operator import itemgetter
from uuid import UUID

from arkindex_export import (
    Element,
    ElementPath,
    Image,
    ImageServer,
    Metadata,
    Transcription,
    WorkerRun,
    WorkerVersion,
    database,
)
from peewee import fn

logger = logging.getLogger(__name__)

# Version of Arkindex export currently supported by the upload command.
EXPORT_VERSION = 10


def is_available() -> bool:
    """
    Check if an Arkindex database is available
    """
    return not database.is_closed()


def in_database(db_objects: list, obj: dict) -> str | None:
    """
    Check if an object exists in the database and return its ID
    """
    for db_object in db_objects:
        if all(getattr(db_object, key) == value for key, value in obj.items()):
            return db_object.id


@cache
def image_id(element_id: str | UUID) -> str | None:
    return Element.get(id=element_id).image


def get_direct_children(parent_id: UUID | str) -> Iterator[str]:
    return ElementPath.select(ElementPath.child).where(ElementPath.parent == parent_id)


def get_or_create_worker_version(worker_version: dict) -> WorkerVersion:
    worker_version, _ = WorkerVersion.get_or_create(
        id=worker_version["id"],
        defaults={
            # Worker info
            "slug": worker_version["worker"]["slug"],
            "name": worker_version["worker"]["name"],
            "type": worker_version["worker"]["type"],
            # Version
            "version": worker_version["version"],
            # Repository info
            **(
                {
                    "repository_url": worker_version["worker"]["repository_url"],
                    "revision": worker_version["revision_url"],
                }
            ),
        },
    )
    return worker_version


def get_or_create_worker_run(worker_run: dict) -> WorkerRun:
    worker_run, _ = WorkerRun.get_or_create(
        id=worker_run["id"],
        defaults={
            "worker_version": worker_run["worker_version"]["id"],
            # Model
            **(
                {
                    "model_version_id": worker_run["model_version"]["id"],
                    "model_id": worker_run["model_version"]["model"]["id"],
                    "model_name": worker_run["model_version"]["model"]["name"],
                }
                if worker_run["model_version"]
                else {}
            ),
            # Configuration
            **(
                {
                    "configuration_id": worker_run["configuration"]["id"],
                    "configuration": worker_run["configuration"]["configuration"],
                }
                if worker_run["configuration"]
                else {}
            ),
        },
    )
    return worker_run


def get_or_create_element(name: str, type: str, worker_run: dict) -> Element:
    element, _ = Element.get_or_create(
        name=name,
        type=type,
        worker_run_id=worker_run["id"],
        defaults={
            "id": str(uuid.uuid4()),
            "created": datetime.now().timestamp(),
            "updated": datetime.now().timestamp(),
        },
    )
    return element


def get_or_create_image(image: dict) -> Image:
    server, _ = ImageServer.get_or_create(
        url=image["server"].pop("url"), defaults=image["server"]
    )
    image, _ = Image.get_or_create(
        id=image["id"],
        defaults={
            "server": server,
            "url": image["url"],
            "width": image["width"],
            "height": image["height"],
        },
    )
    return image


def get_max_ordering(parent_id: UUID | str) -> int:
    max_ordering = (
        ElementPath.select(fn.MAX(ElementPath.ordering))
        .where(ElementPath.parent == parent_id)
        .scalar()
    )

    # There are no children yet
    if max_ordering is None:
        return -1

    # Ordering starts at zero
    return max_ordering


def get_or_create_element_path(parent_id: UUID | str, child_id: str) -> ElementPath:
    element_path, _ = ElementPath.get_or_create(
        parent=parent_id,
        child=child_id,
        defaults={
            "id": str(uuid.uuid4()),
            "ordering": get_max_ordering(parent_id) + 1,
        },
    )
    return element_path


def create_elements(parent_id: UUID | str, elements: list[dict]) -> None:
    date = datetime.now().timestamp()

    with database.atomic():
        Element.insert_many(
            {
                "image": image_id(parent_id),
                "created": date,
                "updated": date,
                **element,
            }
            for element in elements
        ).execute()

        # Create element paths
        max_ordering = get_max_ordering(parent_id)
        ElementPath.insert_many(
            {
                "id": str(uuid.uuid4()),
                "parent": parent_id,
                "child": element_id,
                "ordering": max_ordering + i,
            }
            for i, element_id in enumerate(map(itemgetter("id"), elements), start=1)
        ).execute()


def create_missing_elements(
    parent_id: UUID | str, element_type: str, elements: list[dict]
) -> list[str]:
    date = datetime.now().timestamp()

    existing_elements = list(
        Element.select()
        .join(ElementPath, on=ElementPath.child)
        .where(
            Element.type == element_type,
            Element.image == image_id(parent_id),
            Element.polygon.in_(list(map(itemgetter("polygon"), elements))),
            ElementPath.parent == parent_id,
        )
    )

    missing_data, element_ids = [], []
    for element in elements:
        # We already filter by type, image and parent. We only need to check the polygon
        element_id = in_database(existing_elements, {"polygon": element["polygon"]})
        if not element_id:
            element_id = str(uuid.uuid4())
            missing_data.append(
                {
                    "id": element_id,
                    "type": element_type,
                    "image": image_id(parent_id),
                    "created": date,
                    "updated": date,
                    **element,
                }
            )
        element_ids.append(element_id)

    create_elements(parent_id, missing_data)

    return element_ids


def create_missing_metadata(
    element_id: str, worker_run_id: UUID, metadata_list: list[dict]
) -> None:
    existing_metadata = list(
        Metadata.select().where(
            Metadata.element == element_id,
            Metadata.worker_run == worker_run_id,
        )
    )
    Metadata.insert_many(
        {
            "id": str(uuid.uuid4()),
            "element": element_id,
            "worker_run": worker_run_id,
            **metadata,
        }
        for metadata in metadata_list
        if not in_database(existing_metadata, metadata)
    ).execute()


def create_transcriptions(transcriptions: Iterator[dict] | list[dict]) -> None:
    Transcription.insert_many(transcriptions).execute()
