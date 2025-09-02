import os
from pathlib import Path
from unittest import mock

from arkindex_cli.commands.upload import minio_client

MINIO_URL = "ceph.iiif.teklia.com"
ENV_VARIABLES = {
    "MINIO_ACCESS_KEY": "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY": "MINIO_SECRET_KEY",
}


@mock.patch.dict(os.environ, ENV_VARIABLES)
def test_server_url_no_slash(tmpdir):
    cli = minio_client.MinioClient(
        "a_bucket", Path(tmpdir), "http://some.server.com/iiif", MINIO_URL
    )
    assert cli.IIIF_SERVER == "http://some.server.com/iiif/"


@mock.patch.dict(os.environ, ENV_VARIABLES)
def test_server_url_has_slash(tmpdir):
    cli = minio_client.MinioClient(
        "a_bucket", Path(tmpdir), "http://some.server.com/iiif/", MINIO_URL
    )
    assert cli.IIIF_SERVER == "http://some.server.com/iiif/"
