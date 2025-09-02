import os
import uuid
from pathlib import Path

import pytest
import responses
from arkindex import ArkindexClient

from arkindex_cli.commands.upload.cache import Cache
from arkindex_export import create_database, database


@pytest.fixture(scope="session")
def api_client():
    schema_url = os.environ.get("ARKINDEX_API_SCHEMA_URL")
    local_path = Path("schema.yml")
    if not schema_url and local_path.exists():
        with local_path.open("rb") as f:
            schema_url = "http://testserver/schema.yml"
            responses.add(
                responses.GET,
                schema_url,
                body=f.read(),
            )
    else:
        # Default to production API schema
        schema_url = (
            schema_url
            or "https://arkindex.teklia.com/api/v1/openapi/?format=openapi-json"
        )
        responses.add_passthru(schema_url)
    return ArkindexClient(base_url="http://testserver", schema_url=schema_url)


@pytest.fixture(scope="session")
def fixtures_dir():
    return Path(__file__).absolute().parent / "fixtures"


@pytest.fixture(scope="session")
def samples_dir():
    return Path(__file__).absolute().parent / "samples"


@pytest.fixture
def export_db_path(tmp_path, fixtures_dir):
    db_path = tmp_path / "arkindex_cli.export_test.db"
    create_database(db_path)

    fixtures_path = fixtures_dir / "structure.sql"
    database.cursor().executescript(fixtures_path.read_text())

    yield db_path

    database.close()


@pytest.fixture
def mock_corpus():
    # Generate random corpus UUID to avoid cache issues while creating types
    return {
        "id": str(uuid.uuid4()),
        "types": [
            {"slug": "page", "folder": False},
            {"slug": "text_line", "folder": False},
        ],
    }


@pytest.fixture
def cache(tmp_path, monkeypatch):
    # Do not save cache
    class MockCache(Cache):
        def __del__(self):
            return

    monkeypatch.setattr("arkindex_cli.commands.upload.alto.Cache", MockCache)

    # Setup fresh cache used during publication
    return MockCache(tmp_path / "cache.json")


@pytest.fixture
def gitlab_ci_env(monkeypatch):
    """
    Sets environment variables that simulate any GitLab CI job
    that runs after a `git push` command.
    """
    # Reference: https://docs.gitlab.com/ee/ci/variables/predefined_variables.html
    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("GITLAB_CI", "true")
    monkeypatch.setenv(
        "CI_PROJECT_URL", "https://gitlab.teklia.com/arkindex/cryptominer"
    )
    monkeypatch.setenv("CI_COMMIT_MESSAGE", "this code very faster\n\nCloses #9001")
    # 40-character SHA1 hash
    monkeypatch.setenv("CI_COMMIT_SHA", "decafbadcafefacedeadbeef1337c0de4242f00d")
    # Always follows the format `Name <email>`
    monkeypatch.setenv("CI_COMMIT_AUTHOR", "Teklia Bot <beepboop@teklia.com>")


@pytest.fixture
def gitlab_ci_branch(monkeypatch, gitlab_ci_env):
    """
    Sets environment variables that simulate a GitLab CI job
    that runs after a `git push` on a branch.
    """
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "fix-all-the-bugs")
    monkeypatch.setenv("CI_COMMIT_REF_SLUG", "fix-all-the-bugs")
    monkeypatch.setenv("CI_COMMIT_BRANCH", "fix-all-the-bugs")


@pytest.fixture
def gitlab_ci_tag(monkeypatch, gitlab_ci_env):
    """
    Sets environment variables that simulate a GitLab CI job
    that runs after a `git push` on a tag.
    """
    monkeypatch.setenv("CI_COMMIT_REF_NAME", "v9.9.9")
    monkeypatch.setenv("CI_COMMIT_REF_SLUG", "v9.9.9")
    monkeypatch.setenv("CI_COMMIT_TAG", "v9.9.9")
