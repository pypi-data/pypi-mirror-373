import logging
from pathlib import Path

from arkindex.exceptions import ErrorResponse

from arkindex_cli.auth import Profiles
from arkindex_cli.commands.utils import parse_config
from arkindex_cli.git import LocalGitRepository

logger = logging.getLogger(__name__)


def add_publish_parser(subcommands) -> None:
    publication_parser = subcommands.add_parser(
        "publish",
        description="Publish an available worker version, creating its Git stack (repository, revision, worker) if required",
        help="Publish an available worker version, creating its Git stack (repository, revision, worker) if required",
    )
    publication_parser.add_argument(
        "docker_image_tag",
        help="Tag of the Docker image to be published on the new worker version",
    )
    publication_parser.add_argument(
        "--repository-url",
        help=(
            "URL of the Git project repository containing the worker. "
            "If unset, the repository is automatically detected from the current directory."
        ),
    )
    publication_parser.add_argument(
        "--revision-url",
        help=(
            "URL of the Git revision on which the worker version is published. "
            "If unset, it is built from the repository and the hash of the current commit."
        ),
    )
    publication_parser.add_argument(
        "--revision-branch",
        help="Name of a branch to assign to the worker version."
        "If unset, it is automatically detected from the current commit.",
    )
    publication_parser.add_argument(
        "--revision-tag",
        help=(
            "Single tag to assign to the worker version. "
            "If unset, it is automatically detected from the current commit."
        ),
        default=None,
    )
    publication_parser.set_defaults(func=run)


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
    workers_data = parse_config(Path.cwd())["workers"]
    if not workers_data:
        logger.error("No workers found. Skipping...")
        return

    local_repo = LocalGitRepository()

    if repository_url is None:
        logger.info("Identifying repository from the current directory")
        repository_url = local_repo.url
    if revision_url is None:
        revision_url = local_repo.commit_url
    if revision_branch is None:
        revision_branch = local_repo.branch
    if revision_tag is None:
        tags = local_repo.tags
        if len(tags) >= 1:
            revision_tag = tags[0]

    logger.info("Building a new worker version:")
    logger.info(f" * Repository: {repository_url}")
    logger.info(f" * Revision URL: {revision_url}")
    logger.info(f" * Branch: {revision_branch}")
    logger.info(f" * Tag: {revision_tag}")

    logger.info("Pushing new version to Arkindex")

    profiles = Profiles(gitlab_secure_file)
    profile = profiles.get_or_exit(profile_slug)
    api_client = profiles.get_api_client(profile)

    failures = 0
    for worker_data in workers_data:
        payload = {
            "name": worker_data["name"],
            "type": worker_data["type"],
            "slug": worker_data["slug"],
            "repository_url": repository_url,
        }
        description_path = worker_data.pop("description")
        if description_path:
            assert (
                description_path.exists()
            ), f"Worker description was not found @ {description_path}"
            payload["description"] = description_path.read_text()

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
            worker[field] != payload.get(field, worker[field])
            for field in ("name", "type", "description")
        ):
            logger.info("Updating attributes of the existing worker")
            try:
                worker = api_client.request(
                    "PartialUpdateWorker",
                    id=worker["id"],
                    body={
                        "name": payload["name"],
                        "type": payload["type"],
                        "description": payload.get(
                            "description", worker["description"]
                        ),
                    },
                )
            except ErrorResponse as e:
                logger.error(f"An error occurred: [{e.status_code}] {e.content}")
                failures += 1
                continue

        logger.info(f"Creating or retrieving version based on worker {worker['id']}")
        payload = {
            "configuration": worker_data,
            "revision_url": revision_url,
            "docker_image_iid": docker_image_tag,
            "state": "available",
        }
        if gpu_usage := worker_data.pop("gpu_usage", None):
            payload["gpu_usage"] = gpu_usage
        if model_usage := worker_data.pop("model_usage", None):
            payload["model_usage"] = model_usage
        if revision_branch:
            payload["branch"] = revision_branch
        if revision_tag:
            payload["tag"] = revision_tag
        try:
            worker_version = api_client.request(
                "CreateWorkerVersion", id=worker["id"], body=payload
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

        logger.info(f"Successfully pushed version {worker_version['id']}")

    if failures > 0:
        return 1
    return 0
