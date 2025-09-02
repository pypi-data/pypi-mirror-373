import errno
import logging
from pathlib import Path

from arkindex.exceptions import ErrorResponse

from arkindex_cli.auth import Profiles
from arkindex_cli.git import LocalGitRepository
from worker_configuration.validator import validate_file

logger = logging.getLogger(__name__)


def add_import_parser(subcommands) -> None:
    parser = subcommands.add_parser(
        "import",
        description="Import a worker and worker version in the Arkindex worker configuration format",
        help="Import a worker and worker version in the Arkindex worker configuration format",
    )
    parser.add_argument(
        "docker_image_tag",
        help="Tag of the Docker image to be published on the new worker version",
    )
    parser.add_argument(
        "--repository-url",
        help=(
            "URL of the Git project repository containing the worker. "
            "If unset, the repository is automatically detected from the current directory."
        ),
    )
    parser.add_argument(
        "--revision-url",
        help=(
            "URL of the Git revision on which the worker version is published. "
            "If unset, it is built from the repository and the hash of the current commit."
        ),
    )
    parser.add_argument(
        "--revision-branch",
        help="Name of a branch to assign to the worker version."
        "If unset, it is automatically detected from the current commit.",
    )
    parser.add_argument(
        "--revision-tag",
        help=(
            "Single tag to assign to the worker version. "
            "If unset, it is automatically detected from the current commit."
        ),
        default=None,
    )
    parser.set_defaults(func=run)


def run(
    *,
    docker_image_tag: str,
    repository_url: str | None,
    revision_url: str | None,
    revision_branch: str | None,
    revision_tag: str | None,
    profile_slug: str | None = None,
    gitlab_secure_file: Path | None = None,
) -> int:
    config_dir = Path.cwd() / "arkindex"
    files = [*config_dir.glob("*.yaml"), *config_dir.glob("*.yml")]
    if not files:
        logger.error(f"No YAML files found under the {config_dir} directory.")
        return errno.ENOENT

    local_repo = LocalGitRepository()

    if repository_url is None:
        repository_url = local_repo.url
        if repository_url:
            logger.info(f"Detected repository URL: {repository_url}")
    if revision_url is None:
        revision_url = local_repo.commit_url
        if revision_url:
            logger.info(f"Detected revision URL: {revision_url}")
    if revision_branch is None:
        revision_branch = local_repo.branch
        if revision_branch:
            logger.info(f"Detected branch: {revision_branch}")
    if revision_tag is None:
        tags = local_repo.tags
        if len(tags) >= 1:
            revision_tag = tags[0]
        if revision_tag:
            logger.info(f"Detected tag: {revision_tag}")

    profiles = Profiles(gitlab_secure_file)
    profile = profiles.get_or_exit(profile_slug)
    api_client = profiles.get_api_client(profile)

    failures = 0
    for file in files:
        logger.info(f"Processing {file}")
        config = validate_file(file)

        payload = {
            "name": config["display_name"],
            "type": config["type"],
            "slug": config["slug"],
            "description": config["description"],
            "repository_url": repository_url,
        }

        logger.info(
            f"Creating or retrieving worker {payload['slug']} @ {repository_url}"
        )
        try:
            worker = api_client.request("CreateWorker", body=payload)
        except ErrorResponse as e:
            logger.error(f"An error occurred: [{e.status_code}] {e.content}")
            failures += 1
            continue

        # In case the worker exists, ensure all its fields are up to date
        if any(
            worker[field] != payload[field] for field in ("name", "type", "description")
        ):
            logger.info("Updating attributes of the existing worker")
            try:
                worker = api_client.request(
                    "PartialUpdateWorker",
                    id=worker["id"],
                    body={
                        "name": payload["name"],
                        "type": payload["type"],
                        "description": payload["description"],
                    },
                )
            except ErrorResponse as e:
                logger.error(f"An error occurred: [{e.status_code}] {e.content}")
                failures += 1
                continue

        logger.info(f"Importing worker version based on worker {worker['id']}")
        payload = {
            "yaml": file.read_text(),
            "revision_url": revision_url,
            "docker_image_iid": docker_image_tag,
        }
        if revision_branch:
            payload["branch"] = revision_branch
        if revision_tag:
            payload["tag"] = revision_tag
        try:
            worker_version = api_client.request(
                "ImportWorkerVersion", id=worker["id"], body=payload
            )
        except ErrorResponse as e:
            if all(
                "already exists" not in message
                for message in e.content.get("revision_url", [])
            ) or not (
                worker_version := next(
                    filter(
                        lambda version: version["revision_url"]
                        == payload["revision_url"],
                        api_client.paginate("ListWorkerVersions", id=worker["id"]),
                    ),
                    None,
                )
            ):
                logger.error(f"An error occurred: [{e.status_code}] {e.content}")
                failures += 1
                continue

            # In case the worker version exists, ensure all its fields are up to date
            if any(
                worker_version[field] != payload.get(field, worker_version[field])
                for field in ("tag", "branch")
            ):
                logger.info("Updating attributes of the existing worker version")
                try:
                    worker_version = api_client.request(
                        "PartialUpdateWorkerVersion",
                        id=worker_version["id"],
                        body={
                            **({"tag": payload["tag"]} if payload.get("tag") else {}),
                            **(
                                {"branch": payload["branch"]}
                                if payload.get("branch")
                                else {}
                            ),
                        },
                    )
                except ErrorResponse as e:
                    logger.error(f"An error occurred: [{e.status_code}] {e.content}")
                    failures += 1
                    continue

        logger.info(f"Successfully imported version {worker_version['id']}")

    return failures > 0
