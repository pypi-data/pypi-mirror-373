import logging
import os
import sys
from collections import namedtuple
from pathlib import Path

import requests
import yaml
from arkindex import ArkindexClient, options_from_env
from requests import HTTPError, Response
from requests.compat import urljoin
from rich import print

from teklia_toolbox.requests import get_arkindex_client

logger = logging.getLogger("auth")

Profile = namedtuple("Profile", ["slug", "url", "token"])


GITLAB_LIST_SECURE_FILES = "projects/{}/secure_files"
GITLAB_DOWNLOAD_SECURE_FILE = "projects/{}/secure_files/{}/download"


class Profiles(dict):
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (
            Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
            / "arkindex"
            / "cli.yaml"
        )
        self.dir = self.path.parent
        self.default_profile_name = None
        self.gpg_key = None

        if self.path.exists():
            self.load()
        elif path:
            self.load_from_gitlab()
        else:
            # Try loading a default profile using environment variables
            self.load_from_env()

    def load(self) -> None:
        try:
            with self.path.open() as f:
                self.load_from_content(f)
        except OSError as e:
            logger.error(f"Failed to load profiles file: {e}")
            return

    def load_from_env(self) -> None:
        # Try creating a new profile using environment variables
        arkindex_api = os.environ.get("ARKINDEX_API_URL")
        arkindex_token = os.environ.get("ARKINDEX_API_TOKEN")
        if arkindex_api and arkindex_token:
            self.add_profile(slug="env", url=arkindex_api, token=arkindex_token)
            self.set_default_profile("env")

    def load_from_gitlab(self) -> None:
        def make_request(path: str) -> Response:
            response = requests.get(
                urljoin(base_url, path),
                headers={"JOB-TOKEN": job_token},
                allow_redirects=False,
            )

            # Raise 4xx and 5xx errors
            response.raise_for_status()

            # Happens when auth is incorrectly set
            if 300 <= response.status_code < 400:
                raise HTTPError(response.text, response=response)

            return response

        if not os.environ.get("CI"):
            logger.error("Environment variable `CI` is not set")
            return
        if not (base_url := os.environ.get("CI_API_V4_URL")):
            logger.error("Environment variable `CI_API_V4_URL` is not set")
            return
        if not (job_token := os.environ.get("CI_JOB_TOKEN")):
            logger.error("Environment variable `CI_JOB_TOKEN` is not set")
            return
        if not (project_id := os.environ.get("CI_PROJECT_ID")):
            logger.error("Environment variable `CI_PROJECT_ID` is not set")
            return

        # Add trailing slash to avoid the url from being cut off by `urljoin`
        if not base_url.endswith("/"):
            base_url += "/"

        try:
            response = make_request(GITLAB_LIST_SECURE_FILES.format(project_id))
        except HTTPError as e:
            logger.error(f"Failed to list secure files of project {project_id}: {e}")
            return

        if not (
            secure_file := next(
                (
                    secure_file
                    for secure_file in response.json()
                    if secure_file["name"] == str(self.path)
                ),
                None,
            )
        ):
            logger.error(f"Secure file {self.path} not found for project {project_id}")
            return

        try:
            response = make_request(
                GITLAB_DOWNLOAD_SECURE_FILE.format(project_id, secure_file["id"])
            )
        except HTTPError as e:
            logger.error(
                f"Failed to download secure files {self.path} of project {project_id}: {e}"
            )
            return

        self.load_from_content(response.content)

    def load_from_content(self, content: str) -> None:
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            logger.error(f"Failed to load profiles file: {e}")
            return

        for slug, host_data in data.get("hosts", {}).items():
            self[slug] = Profile(slug, host_data["url"], host_data["token"])

        self.default_profile_name = data.get("default_host")
        self.gpg_key = data.get("gpg_key")

    def get_default_profile(self) -> Profile | None:
        if self.default_profile_name in self:
            return self[self.default_profile_name]

    def set_default_profile(self, name: str) -> None:
        assert name in self, f"Profile {name} does not exist"
        self.default_profile_name = name

    def add_profile(self, slug: str, url: str, token: str) -> None:
        self[slug] = Profile(slug, url, token)

    def get_or_exit(self, slug: str | None) -> Profile:
        """
        Get a Profile, or print a user-friendly message for a missing profile and exit
        """
        if slug:
            profile = self.get(slug)
        else:
            profile = self.get_default_profile()

        if profile is None:
            print(
                "[bright_red]Arkindex profile was not found. Try logging in using [white]arkindex login[/] first."
            )
            sys.exit(2)

        return profile

    def get_api_client(
        self, slug: str | Profile | None = None
    ) -> ArkindexClient | None:
        if isinstance(slug, Profile):
            profile = slug
        elif slug:
            profile = self.get(slug)
        else:
            profile = self.get_default_profile()

        if profile:
            logger.debug(f"Using profile {profile.slug} ({profile.url})")
            options = options_from_env()
            options["base_url"] = profile.url
            options["token"] = profile.token
            return get_arkindex_client(**options)

    def get_api_client_or_exit(
        self, slug: str | Profile | None = None
    ) -> ArkindexClient:
        if isinstance(slug, Profile):
            profile = slug
        else:
            profile = self.get_or_exit(slug)
        return self.get_api_client(profile)

    def save(self) -> None:
        data = {
            "default_host": self.default_profile_name,
            "gpg_key": self.gpg_key,
            "hosts": {
                profile.slug: {"url": profile.url, "token": profile.token}
                for profile in self.values()
            },
        }

        # Create parent folders if needed
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)
