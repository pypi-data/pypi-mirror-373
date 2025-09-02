import base64
import hashlib
import logging
import math
import os
from dataclasses import dataclass
from datetime import datetime
from io import BufferedReader
from pathlib import Path

import requests
from arkindex import ArkindexClient
from arkindex.exceptions import ErrorResponse
from requests.exceptions import ConnectionError, HTTPError, Timeout
from rich.progress import track

from teklia_toolbox.requests import should_verify_cert
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger("multipart-upload")


@dataclass
class UploadPart:
    part_number: int
    etag: str
    # sha256 hex digest
    checksum: str | None
    # md5 hex digest
    md5_hash: str


def is_500_error(exception: Exception):
    return (
        # Error 500 from Arkindex's backend
        isinstance(exception, ErrorResponse)
        and 500 <= exception.status_code
        # Error 500 from a HTTP request
        or isinstance(exception, HTTPError)
        and (resp := exception.response) is not None
        and 500 <= resp.status_code
        # Other unexpected errors
        or isinstance(exception, ConnectionError | Timeout)
    )


def file_digest(file_obj, digest):
    # hashlib.file_digest is available on Python 3.11+
    if hasattr(hashlib, "file_digest"):
        return hashlib.file_digest(file_obj, digest)

    # Simplified reimplementation for Python 3.10
    # https://github.com/python/cpython/blob/c730952aa64b790c75c437cb63a1242dc08c2e97/Lib/hashlib.py#L231
    digest_obj = digest() if callable(digest) else hashlib.new(digest)

    buffer = bytearray(2**18)
    view = memoryview(buffer)

    while True:
        size = file_obj.readinto(buffer)
        if size == 0:
            break
        digest_obj.update(view[:size])

    return digest_obj


class PartialFileObject:
    """
    File object like, allowing to seek and read inside the part only.
    """

    # Inner reference to what has been read already
    _pointer = 0

    def __init__(self, file: BufferedReader, offset: int, size: int):
        self.file_obj = file
        self.offset = offset
        self.size = size
        self.seek(0)

    def readable(self):
        return self.file_obj.readable()

    def read(self, size: int = -1):
        if size < 0:
            size = self.size
        if size + self._pointer > self.size:
            size = self.size - self._pointer
        self._pointer += size
        return self.file_obj.read(size)

    def readinto(self, b: bytearray):
        read_bytes = len(b)
        if (read_bytes + self._pointer) > self.size:
            read_bytes = self.size - self._pointer
        self._pointer += read_bytes
        self.file_obj.readinto(b)
        return read_bytes

    def seek(self, target: int, whence: int = os.SEEK_SET):
        if whence == os.SEEK_END:
            whence = os.SEEK_SET
            target = self.size
        self._pointer = target
        self.file_obj.seek(self.offset + target, whence)

    def tell(self):
        return self.file_obj.tell() - self.offset


class MultipartUpload:
    """
    Upload a file using the S3 protocol, based on Arkindex backend API for multipart upload.
    """

    checksum_algorithm = None
    # Default minimum and maximum size for each chunk, in MiB
    default_min_chunk_size = 5
    default_max_chunk_size = 50
    # Base number of chunks used to upload a file
    default_file_parts = 5
    uploaded_parts: list[UploadPart]

    @retry(
        retry=retry_if_exception(is_500_error),
        wait=wait_exponential(multiplier=2, min=1),
        stop=stop_after_attempt(4),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def __init__(
        self,
        client: ArkindexClient,
        file_path: Path,
        object_type: str,
        object_id: str,
        chunk_size: int | None = None,
        use_file_objects: bool = False,
    ):
        """
        If the `chunk_size` parameter is not set, the file will be split into <default_file_parts> parts,
        with a minimum size of <default_min_chunk_size> MB and a maximum size of <default_max_chunk_size> MB.
        If the `use_file_objects` parameter is set to True, the upload will be performed by reading the
        content of each part as a file like object, thus avoiding storing each chunk of data in memory.
        Each uploaded part is verified based on an MD5 sum of its contents. An additional checksum
        algorithm, such as sha256, is supported by the backend but not implemented in the client yet.
        """
        if not file_path.exists() or not file_path.is_file():
            raise ValueError("file_path must be a valid file path")

        self.total_bytes = file_path.stat().st_size
        total_mb = self.total_bytes / 1024 / 1024

        if not chunk_size:
            chunk_size = math.ceil(total_mb / self.default_file_parts)
            chunk_size = max(chunk_size, self.default_min_chunk_size)
            chunk_size = min(chunk_size, self.default_max_chunk_size)

        # Ensure we have no more than 10000 chunks
        self.parts_count = math.ceil(total_mb / chunk_size)
        if self.parts_count > 10000:
            raise ValueError(
                "Uploading file with this configuration would generate more than 10000 chunks."
            )

        self.client = client
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_size_bytes = chunk_size * 1024 * 1024
        self.object_type = object_type
        self.object_id = object_id
        self.upload_id = self.create_multipart()
        self.completed = None
        self.uploaded_parts = []
        self.use_file_objects = use_file_objects

    def create_multipart(self) -> str:
        resp = self.client.request(
            "CreateMultipartUpload",
            body={
                "object_type": self.object_type,
                "object_id": self.object_id,
                "checksum_algorithm": self.checksum_algorithm,
            },
        )
        return resp["upload_id"]

    def build_digest(self, data: bytes, hash_function) -> str:
        digest = hash_function(data).digest()
        return base64.b64encode(digest).decode()

    def build_digest_from_file(self, file_obj: BufferedReader, hash_function) -> str:
        digest = file_digest(file_obj, hash_function).digest()
        return base64.b64encode(digest).decode()

    @retry(
        retry=retry_if_exception(is_500_error),
        wait=wait_exponential(multiplier=2, min=1),
        stop=stop_after_attempt(4),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def upload_part(
        self,
        part_number: int,
        content_length: int,
        *,
        data: bytes | None = None,
        file_obj: PartialFileObject | None = None,
    ) -> UploadPart:
        """
        Perform Arkindex-based S3 upload of the current part.
        See https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPart.html for the protocol details.

        When using a file-like object, the content is read twice in order to
        build the hash and perform the upload but it is never kept in memory.
        """
        assert (data is None) ^ (
            file_obj is None
        ), "Exactly one of data or file_obj parameter can be set"

        if data:
            md5 = self.build_digest(data, hashlib.md5)
        else:
            md5 = self.build_digest_from_file(file_obj, hashlib.md5)
            file_obj.seek(0)

        sha256 = None

        payload = {
            "object_type": self.object_type,
            "object_id": self.object_id,
            "upload_id": self.upload_id,
            "checksum_algorithm": self.checksum_algorithm,
            "part_number": part_number,
            "checksum": sha256,
            "md5_hash": md5,
        }

        # Retrieve the upload part PUT URL from the backend
        backend_part = self.client.request("CreateMultipartUploadPart", body=payload)
        resp = requests.put(
            url=backend_part["url"],
            data=data or file_obj,
            headers={
                "Content-Length": str(content_length),
                "Content-MD5": md5,
            },
            verify=should_verify_cert(backend_part["url"]),
        )
        if not resp.ok:
            logger.error(f"Chunk could not be uploaded: {resp.content}")
        resp.raise_for_status()

        if "Etag" not in resp.headers:
            raise Exception("The Etag header is missing from the S3 response")

        return UploadPart(
            part_number=part_number,
            etag=resp.headers["Etag"],
            checksum=sha256,
            md5_hash=md5,
        )

    def upload(self):
        """
        Perform a complete upload of the file by iterating over chunks.
        """
        logger.info(
            f"Uploading the file in {self.parts_count} "
            f"part{'s' if self.parts_count > 1 else ''} "
            f"of {self.chunk_size}MiB."
        )
        with self.file_path.open("rb") as fp:
            for index in track(
                range(1, self.parts_count + 1), description="Uploading parts…"
            ):
                offset = (index - 1) * self.chunk_size_bytes
                # The last chunk will be whatever is left of the file and not the normal chunk size
                content_length = min(self.chunk_size_bytes, self.total_bytes - offset)
                if self.use_file_objects:
                    filepart = PartialFileObject(
                        file=fp, offset=offset, size=content_length
                    )
                    part = self.upload_part(index, content_length, file_obj=filepart)
                else:
                    fp.seek(offset)
                    data = fp.read(content_length)
                    part = self.upload_part(index, content_length, data=data)
                self.uploaded_parts.append(part)

    @retry(
        retry=retry_if_exception(is_500_error),
        wait=wait_exponential(multiplier=2, min=1),
        stop=stop_after_attempt(4),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def complete(self):
        """
        Perform backend validation of the upload.
        This step is required in order for the file to be available in S3.
        """
        assert self.uploaded_parts, "No part has been uploaded yet"
        assert not self.completed, "This upload already completed"

        self.client.request(
            "CompleteMultipartUpload",
            body={
                "object_type": self.object_type,
                "object_id": self.object_id,
                "upload_id": self.upload_id,
                "checksum_algorithm": self.checksum_algorithm,
                "parts": [vars(p) for p in self.uploaded_parts],
            },
        )
        self.completed = datetime.now().isoformat()

    @retry(
        retry=retry_if_exception(is_500_error),
        wait=wait_exponential(multiplier=2, min=1),
        stop=stop_after_attempt(4),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def abort(self):
        """
        Abort the current upload.
        This step notifies the backend that the upload could not
        be completed, which cleans up the temporary files in S3.
        """
        assert not self.completed, "This upload already completed"
        self.client.request(
            "AbortMultipartUpload",
            body={
                "object_type": self.object_type,
                "object_id": self.object_id,
                "upload_id": self.upload_id,
            },
        )
