import logging
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import responses
from arkindex.exceptions import ErrorResponse
from responses import matchers

from arkindex_cli.commands.models.utils import (
    DEFAULT_MODEL_DIR,
    create_archive,
    create_model_version,
    create_or_retrieve_model,
    find_model_path,
    upload_to_s3,
    validate_model_version,
)

model_version_details = {
    "id": "fake_model_version_id",
    "model_id": "fake_model_id",
    "tag": "A tag",
    "description": "Something",
    "s3_etag": None,
    "archive_hash": None,
    "s3_url": None,
    "s3_put_url": "http://hehehe.com",
}


def test_create_archive_path_to_file():
    with pytest.raises(AssertionError):
        with create_archive(path=Path("tests/samples/model_file.pth")) as _:
            pass


def test_create_archive():
    model_file_dir = Path("tests/samples/model_files")

    with create_archive(path=model_file_dir) as (
        zst_archive_path,
        size,
        archive_hash,
    ):
        assert os.path.exists(zst_archive_path), "The archive was not created"
        assert 300 < size < 700

    assert not os.path.exists(zst_archive_path), "Auto removal failed"


@pytest.mark.parametrize("status", [200, 400])
def test_create_or_retrieve_new_model(api_client, status):
    model_name = "U-FCN best"
    fake_model_id = "fe226ded-44b2-4850-b79e-30711174c555"
    responses.add(
        responses.POST,
        "http://testserver/api/v1/models/",
        status=status,
        match=[matchers.json_params_matcher({"name": model_name})],
        json={
            "id": fake_model_id,
            "created": "20220408-17:27:00",
            "updated": "20220408-17:27:00",
            "name": model_name,
            "description": "The best model ever created on Earth",
        },
    )

    model_id = create_or_retrieve_model(api_client, model_name)
    assert model_id == fake_model_id


def test_retrieve_model_no_access(api_client):
    """Raise 403 because no rights on existing model"""
    model_name = "U-FCN best"
    responses.add(
        responses.POST,
        "http://testserver/api/v1/models/",
        status=403,
        match=[matchers.json_params_matcher({"name": model_name})],
    )
    with pytest.raises(
        Exception,
        match=f"You do not have the required rights to create a new model version for model {model_name}.",
    ):
        create_or_retrieve_model(api_client, model_name)
    assert len(responses.calls) == 1
    assert responses.calls[0].request.method == responses.POST
    assert responses.calls[0].request.url == "http://testserver/api/v1/models/"


def test_description_file_not_found(api_client):
    with pytest.raises(
        AssertionError,
        match="Model version description was not found @ path/to/desc.md",
    ):
        create_model_version(
            api_client, "fake_model_id", description_path=Path("path/to/desc.md")
        )


def test_create_model_version(samples_dir, api_client):
    """A new model version is returned"""
    responses.add(
        responses.POST,
        "http://testserver/api/v1/model/fake_model_id/versions/",
        status=200,
        match=[
            matchers.json_params_matcher(
                {
                    "tag": "A tag",
                    "description": "something",
                    "configuration": {},
                }
            )
        ],
        json=model_version_details,
    )

    assert (
        create_model_version(
            api_client,
            "fake_model_id",
            tag="A tag",
            description_path=samples_dir / "description.txt",
        )
        == model_version_details
    )


def test_validate_model_version(api_client):
    """
    The validated worker version is returned
    """
    validation_args = {
        "size": 8,
        "archive_hash": "b" * 32,
    }
    expected_model_version = {
        **model_version_details,
        **validation_args,
        "s3_url": "http://hehehe.com",
        "s3_put_url": None,
    }

    responses.add(
        responses.PATCH,
        "http://testserver/api/v1/modelversion/fake_model_version_id/",
        status=200,
        match=[matchers.json_params_matcher({**validation_args, "state": "available"})],
        json=expected_model_version,
    )

    assert (
        validate_model_version(api_client, "fake_model_version_id", **validation_args)
        == expected_model_version
    )


@pytest.mark.parametrize(
    "resp,messages",
    [
        (
            {"size": ["Archive has not been uploaded"]},
            [
                (
                    "arkindex_cli.commands.models.utils",
                    40,
                    "Failed to check model version archive size: Archive has not been uploaded.",
                )
            ],
        ),
        (
            {
                "size": ["Uploaded file size is 12 bytes, expected 13 bytes"],
                "archive_hash": [
                    "No file content, assert file has been correctly uploaded"
                ],
            },
            [
                (
                    "arkindex_cli.commands.models.utils",
                    40,
                    "Failed to check model version archive size: Uploaded file size is 12 bytes, expected 13 bytes.",
                ),
                (
                    "arkindex_cli.commands.models.utils",
                    40,
                    "Failed to check model version archive hash: No file content, assert file has been correctly uploaded.",
                ),
            ],
        ),
        (
            {
                "state": [
                    "You can only update a model version's state from Created to Available, not Error to Available."
                ]
            },
            [
                (
                    "arkindex_cli.commands.models.utils",
                    40,
                    "You can only update a model version's state from Created to Available, not Error to Available.",
                )
            ],
        ),
    ],
)
def test_validate_model_version_errors(api_client, caplog, resp, messages):
    caplog.set_level(logging.ERROR)
    validation_args = {
        "size": 8,
        "archive_hash": "b" * 32,
    }

    responses.add(
        responses.PATCH,
        "http://testserver/api/v1/modelversion/fake_model_version_id/",
        status=400,
        match=[matchers.json_params_matcher({**validation_args, "state": "available"})],
        json=resp,
    )

    with pytest.raises(Exception):
        validate_model_version(api_client, "fake_model_version_id", **validation_args)
    assert caplog.record_tuples == messages


def test_validate_model_version_unhandled_error(api_client, caplog, monkeypatch):
    caplog.set_level(logging.ERROR)
    monkeypatch.setattr(api_client.request.retry, "wait", None)
    validation_args = {
        "size": 8,
        "archive_hash": "b" * 32,
    }

    responses.add(
        responses.PATCH,
        "http://testserver/api/v1/modelversion/fake_model_version_id/",
        status=500,
        match=[matchers.json_params_matcher({**validation_args, "state": "available"})],
        json={"something": ["oh no"]},
    )

    with pytest.raises(ErrorResponse):
        validate_model_version(api_client, "fake_model_version_id", **validation_args)
    assert caplog.record_tuples == [
        (
            "arkindex_cli.commands.models.utils",
            40,
            "Failed validating model version: 500 -- {'something': ['oh no']}",
        )
    ]


def test_retrieve_available_model_version(api_client, samples_dir):
    """Raise error when there is an existing model version in Available mode"""
    model_id = "fake_model_id"
    # Create a model archive and keep its hash and size.
    with create_archive(path=samples_dir) as (
        zst_archive_path,
        size,
        archive_hash,
    ):
        responses.add(
            responses.POST,
            f"http://testserver/api/v1/model/{model_id}/versions/",
            status=403,
            match=[
                matchers.json_params_matcher(
                    {"archive_hash": archive_hash, "size": size}
                )
            ],
        )

    with pytest.raises(Exception):
        create_model_version(api_client, model_id, hash, size, archive_hash)


def test_handle_s3_uploading_errors(samples_dir):
    s3_endpoint_url = "http://s3.localhost.com"
    responses.add_passthru(s3_endpoint_url)
    responses.add(responses.Response(method="PUT", url=s3_endpoint_url, status=400))
    file_path = samples_dir / "model_file.pth"
    with pytest.raises(Exception):
        upload_to_s3(file_path, {"s3_put_url": s3_endpoint_url})


@patch("pathlib.Path.exists")
def test_find_docker_model_path(exists):
    """If the path that uses teklia's convention exists, use that path"""
    # The following works because teklia's convention is the first path tested by the function
    exists.return_value = True

    file_path = Path(DEFAULT_MODEL_DIR / "models/model.pth")
    assert find_model_path(file_path) == file_path


def test_find_local_model_path():
    """If the local path exists, use that path"""
    file_path = Path("tests/samples/model_file.pth")
    assert find_model_path(file_path) == file_path


@patch("pathlib.Path.exists")
def test_cannot_find_path(exists):
    """If the path using  exists, use that path"""
    file_path = Path("model_file.pth")
    # Make sure the file is never found
    exists.return_value = False
    assert find_model_path(file_path) is None
