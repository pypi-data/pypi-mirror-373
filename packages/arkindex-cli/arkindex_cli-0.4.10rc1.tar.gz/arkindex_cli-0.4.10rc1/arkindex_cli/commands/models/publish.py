import logging
import os
from pathlib import Path
from uuid import UUID

from arkindex import ArkindexClient
from rich.progress import Progress

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.models.utils import (
    create_archive,
    create_model_version,
    create_or_retrieve_model,
    find_model_path,
    upload_to_s3,
    validate_model_version,
)
from arkindex_cli.commands.utils import parse_config

logger = logging.getLogger(__name__)


def add_publish_parser(subcommands) -> None:
    publish_parser = subcommands.add_parser(
        "publish",
        description="Publish every ML models of this git repository.",
        help="Publish ML models to Arkindex.",
    )
    publish_parser.set_defaults(func=run)


def publish_model(
    client: ArkindexClient,
    name: str,
    model_path: Path,
    configuration: dict,
    tag: str | None,
    description_path: Path | None,
    parent: UUID | None,
) -> None:
    """This takes a model and publishes a new version of the model"""
    logger.info(f"Publishing {name}")

    # Find the model file associated
    path_to_model = find_model_path(config_model_path=model_path)

    assert path_to_model, f"The model could not be loaded using {model_path}"

    try:
        # Create or retrieve the parent model
        model_id = create_or_retrieve_model(client=client, name=name)

        # Create a version for this model
        model_version = create_model_version(
            client=client,
            model_id=model_id,
            tag=tag or os.environ.get("CI_COMMIT_TAG"),
            description_path=description_path,
            configuration=configuration,
            parent=parent,
        )
    except (AssertionError, Exception) as e:
        logger.error(str(e))
        logger.error("Skipping this model.")
        return

    # Create the zst archive, get its hash and size
    with create_archive(path=path_to_model) as (
        path_to_archive,
        size,
        archive_hash,
    ):
        upload_to_s3(archive_path=path_to_archive, model_version_details=model_version)

        try:
            # Validate the model version with hash, archive_hash and size
            validate_model_version(
                client=client,
                model_version_id=model_version["id"],
                size=size,
                archive_hash=archive_hash,
            )
        except Exception:
            logger.error("Skipping this model.")
            return


def run(
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> None:
    with Progress(transient=True) as progress:
        progress.add_task(start=False, description="Loading API client")
        client = Profiles(gitlab_secure_file).get_api_client_or_exit(profile_slug)

    # Parse .arkindex.yml => retrieve model name, path and configuration
    models = parse_config(Path.cwd())["models"]
    if not models:
        logger.error("No models found. Skipping...")
        return

    # For each model, do_publish
    for model in models:
        try:
            publish_model(
                client,
                model["name"],
                model["path"],
                model["configuration"],
                model.get("tag"),
                model.get("description"),
                model.get("parent"),
            )
        except Exception as e:
            msg = getattr(e, "content", repr(e))
            logger.exception(f"{model['name']} publishing has failed with error: {msg}")
            logger.error("Skipping this model.")

    logger.info("All done.")
