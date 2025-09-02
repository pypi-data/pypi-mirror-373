import logging
import os
from pathlib import Path
from unittest import mock

import pytest
import responses
import yaml

from arkindex_cli.auth import Profile, Profiles

yaml_sample = yaml.dump(
    {
        "default_host": "toast",
        "gpg_key": "DEADBEEF",
        "hosts": {"toast": {"url": "https://devnull", "token": "c0ffee"}},
    }
)

ENV_VARIABLES = {
    # load
    "XDG_CONFIG_HOME": "/invalid/path",
    # load_from_env
    "ARKINDEX_API_URL": "https://arkindex.url",
    "ARKINDEX_API_TOKEN": "deadbeeftoken",
    # load_from_gitlab
    "CI": "True",
    "CI_API_V4_URL": "https://gitlab.fake.com/api/v4/",
    "CI_JOB_TOKEN": "s3cret_tok3n",
    "CI_PROJECT_ID": "42",
}


def test_profiles_auto_load(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    # Nothing is loaded
    assert len(profiles) == 0

    (tmp_path / "file.yml").write_text(yaml_sample)

    profiles = Profiles(tmp_path / "file.yml")
    assert len(profiles) == 1
    assert profiles["toast"] == Profile("toast", "https://devnull", "c0ffee")
    assert profiles.get_default_profile() == profiles["toast"]


def test_profiles_load(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    assert len(profiles) == 0

    (tmp_path / "file.yml").write_text(yaml_sample)

    profiles.load()
    assert len(profiles) == 1
    assert profiles["toast"] == Profile("toast", "https://devnull", "c0ffee")
    assert profiles.get_default_profile() == profiles["toast"]


def test_profiles_load_empty(tmp_path):
    (tmp_path / "file.yml").write_text("{}")
    profiles = Profiles(tmp_path / "file.yml")
    assert len(profiles) == 0
    assert profiles.get_default_profile() is None


def _assert_error_log(caplog):
    log = caplog.record_tuples[-1]
    assert log[0] == "auth"
    assert log[1] == logging.ERROR
    assert "Failed to load profiles file:" in log[2]


def test_profiles_load_not_found(tmp_path, caplog):
    profiles = Profiles(tmp_path / "file.yml")
    profiles.load()

    _assert_error_log(caplog)
    assert len(profiles) == 0
    assert profiles.get_default_profile() is None


def test_profiles_yaml_error(tmp_path, caplog):
    (tmp_path / "file.yml").write_text("!!")
    profiles = Profiles(tmp_path / "file.yml")

    _assert_error_log(caplog)
    assert len(profiles) == 0
    assert profiles.get_default_profile() is None


def test_profiles_default_profile(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    assert profiles.get_default_profile() is None

    profiles.add_profile("toast", "https://devnull", "c0ffee")
    profiles.set_default_profile("toast")
    assert profiles.get_default_profile() == Profile(
        "toast", "https://devnull", "c0ffee"
    )

    with pytest.raises(AssertionError, match="Profile something does not exist"):
        profiles.set_default_profile("something")

    profiles.default_profile_name = "unexpected"
    assert profiles.get_default_profile() is None


def test_profiles_add_profile(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    assert "toast" not in profiles
    profiles.add_profile("toast", "https://devnull", "c0ffee")
    assert profiles["toast"] == Profile("toast", "https://devnull", "c0ffee")


def test_profiles_save(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    profiles.add_profile("toast", "https://devnull", "c0ffee")
    profiles.set_default_profile("toast")
    profiles.gpg_key = "DEADBEEF"
    profiles.save()
    assert (tmp_path / "file.yml").read_text() == yaml_sample


def test_profiles_save_empty(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")
    profiles.save()
    assert yaml.safe_load((tmp_path / "file.yml").read_text()) == {
        "default_host": None,
        "hosts": {},
        "gpg_key": None,
    }


def test_profiles_get_or_exit(tmp_path):
    profiles = Profiles(tmp_path / "file.yml")

    with pytest.raises(SystemExit) as excinfo:
        profiles.get_or_exit("toast")

    # Should exit with code 2
    assert excinfo.value.code == 2

    profiles.add_profile("toast", "https://devnull", "c0ffee")
    assert profiles.get_or_exit("toast") == Profile(
        "toast", "https://devnull", "c0ffee"
    )


@mock.patch.dict(os.environ, ENV_VARIABLES)
def test_profile_load_from_env():
    profiles = Profiles()
    profile = profiles.get_default_profile()
    assert profile == Profile(
        "env",
        ENV_VARIABLES.get("ARKINDEX_API_URL"),
        ENV_VARIABLES.get("ARKINDEX_API_TOKEN"),
    )


@mock.patch.dict(os.environ, ENV_VARIABLES)
def test_profile_load_from_gitlab():
    responses.add(
        responses.GET,
        "https://gitlab.fake.com/api/v4/projects/42/secure_files",
        json=[{"id": 1, "name": "other_file.yml"}, {"id": 8, "name": "file.yml"}],
    )
    responses.add(
        responses.GET,
        "https://gitlab.fake.com/api/v4/projects/42/secure_files/8/download",
        body=yaml_sample,
    )

    profiles = Profiles(Path("file.yml"))
    assert len(profiles) == 1
    assert profiles["toast"] == Profile("toast", "https://devnull", "c0ffee")
    assert profiles.get_default_profile() == profiles["toast"]

    assert [call.request.url for call in responses.calls] == [
        "https://gitlab.fake.com/api/v4/projects/42/secure_files",
        "https://gitlab.fake.com/api/v4/projects/42/secure_files/8/download",
    ]
