import base64
import hashlib
import logging

import pytest
import responses
from responses import matchers

from arkindex_cli.uploads import MultipartUpload


@pytest.fixture
def file_to_upload(tmp_path):
    """A 11 MB file sample"""
    path = tmp_path / "file.zst"
    # Fill the file with \x00 so the hash is easily computable
    with path.open("wb") as f:
        f.write(b"\x00" * 11600000)
    return path


def mock_multipart_creation():
    responses.add(
        responses.POST,
        "http://testserver/api/v1/multipart/",
        status=201,
        match=[
            matchers.json_params_matcher(
                {
                    "object_type": "object_type",
                    "object_id": "object_id",
                    "checksum_algorithm": None,
                }
            )
        ],
        json={"upload_id": "upload_id"},
    )


def test_upload_min_chunk_size(api_client, file_to_upload):
    class TestMultipart(MultipartUpload):
        default_min_chunk_size = 100
        default_max_chunk_size = 100

    mock_multipart_creation()
    m = TestMultipart(api_client, file_to_upload, "object_type", "object_id")
    assert m.parts_count == 1
    assert m.chunk_size == 100


def test_upload_max_chunk_size(api_client, file_to_upload):
    class TestMultipart(MultipartUpload):
        default_min_chunk_size = 1
        default_max_chunk_size = 1

    mock_multipart_creation()
    m = TestMultipart(api_client, file_to_upload, "object_type", "object_id")
    assert m.parts_count == 12
    assert m.chunk_size == 1


@pytest.mark.parametrize("use_file_objects", [True, False])
def test_upload(api_client, file_to_upload, use_file_objects, caplog):
    mock_multipart_creation()
    m = MultipartUpload(
        api_client,
        file_to_upload,
        "object_type",
        "object_id",
        use_file_objects=use_file_objects,
    )
    assert m.parts_count == 3
    assert m.chunk_size == 5
    chunks = [
        (1, "XzY+DlipXwbL6bvGYsXftg=="),
        (2, "XzY+DlipXwbL6bvGYsXftg=="),
        (3, "1LF23x1wHJPnN5+E3Iw67g=="),
    ]
    for index, md5 in chunks:
        # Mock Arkindex API
        responses.add(
            responses.POST,
            "http://testserver/api/v1/multipart/part/",
            status=201,
            match=[
                matchers.json_params_matcher(
                    {
                        "part_number": index,
                        "object_type": "object_type",
                        "object_id": "object_id",
                        "upload_id": "upload_id",
                        "md5_hash": md5,
                        "checksum": None,
                        "checksum_algorithm": None,
                    }
                )
            ],
            json={"url": f"https://s3_part_url.test/part_{index}"},
        )

        # Mock the S3 API by validating the payload based on its md5
        def test_data_sum(expected_hash):
            def _check(request):
                digest = hashlib.md5(request.body).digest()
                if base64.b64encode(digest).decode() == expected_hash:
                    return True, "Checksum do match"
                return False, "Checksum do not match"

            return _check

        responses.add(
            responses.PUT,
            f"https://s3_part_url.test/part_{index}",
            headers={"Etag": md5},
            match=[test_data_sum(md5)],
        )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/multipart/complete/",
        status=201,
    )

    m.upload()
    m.complete()
    assert caplog.record_tuples == [
        ("multipart-upload", logging.INFO, "Uploading the file in 3 parts of 5MiB."),
    ]


def test_upload_abort(api_client, file_to_upload, caplog):
    mock_multipart_creation()
    m = MultipartUpload(
        api_client,
        file_to_upload,
        "object_type",
        "object_id",
    )
    abort_url = "http://testserver/api/v1/multipart/abort/"
    responses.add(
        responses.POST,
        abort_url,
        status=204,
        match=[
            matchers.json_params_matcher(
                {
                    "object_type": "object_type",
                    "object_id": "object_id",
                    "upload_id": "upload_id",
                }
            )
        ],
    )
    m.abort()
    assert [call.request.url for call in responses.calls][
        -1
    ] == "http://testserver/api/v1/multipart/abort/"
