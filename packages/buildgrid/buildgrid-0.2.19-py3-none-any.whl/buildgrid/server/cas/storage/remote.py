# Copyright (C) 2018 Bloomberg LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  <http://www.apache.org/licenses/LICENSE-2.0>
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
RemoteStorage
==================

Forwwards storage requests to a remote storage.
"""

import io
import logging
from tempfile import NamedTemporaryFile
from typing import IO, Any, Sequence

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2, remote_execution_pb2_grpc
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2, status_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.client.authentication import ClientCredentials
from buildgrid.server.client.cas import download, upload
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.context import current_instance
from buildgrid.server.decorators import timed
from buildgrid.server.exceptions import GrpcUninitializedError, NotFoundError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metadata import metadata_list
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.settings import HASH, MAX_IN_MEMORY_BLOB_SIZE_BYTES

from .storage_abc import StorageABC

LOGGER = buildgrid_logger(__name__)


class RemoteStorage(StorageABC):
    TYPE = "Remote"

    def __init__(
        self,
        remote: str,
        instance_name: str | None = None,
        channel_options: Sequence[tuple[str, Any]] | None = None,
        credentials: ClientCredentials | None = None,
        retries: int = 0,
        max_backoff: int = 64,
        request_timeout: float | None = None,
    ) -> None:
        self._remote_instance_name = instance_name
        self._remote = remote
        self._channel_options = channel_options
        if credentials is None:
            credentials = {}
        self.credentials = credentials
        self.retries = retries
        self.max_backoff = max_backoff
        self._request_timeout = request_timeout

        self._stub_cas: remote_execution_pb2_grpc.ContentAddressableStorageStub | None = None
        self.channel: grpc.Channel | None = None

    def start(self) -> None:
        if self.channel is None:
            self.channel, *_ = setup_channel(
                self._remote,
                auth_token=self.credentials.get("auth-token"),
                auth_token_refresh_seconds=self.credentials.get("token-refresh-seconds"),
                client_key=self.credentials.get("tls-client-key"),
                client_cert=self.credentials.get("tls-client-cert"),
                server_cert=self.credentials.get("tls-server-cert"),
                timeout=self._request_timeout,
            )

        if self._stub_cas is None:
            self._stub_cas = remote_execution_pb2_grpc.ContentAddressableStorageStub(self.channel)

    def stop(self) -> None:
        if self.channel is not None:
            self.channel.close()

    @property
    def remote_instance_name(self) -> str:
        if self._remote_instance_name is not None:
            return self._remote_instance_name
        return current_instance()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug("Checking for blob.", tags=dict(digest=digest))
        if not self.missing_blobs([digest]):
            return True
        return False

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        if self.channel is None:
            raise GrpcUninitializedError("Remote CAS backend used before gRPC initialization.")

        LOGGER.debug("Getting blob.", tags=dict(digest=digest))
        with download(
            self.channel, instance=self.remote_instance_name, retries=self.retries, max_backoff=self.max_backoff
        ) as downloader:
            if digest.size_bytes > MAX_IN_MEMORY_BLOB_SIZE_BYTES:
                # Avoid storing the large blob completely in memory.
                temp_file = NamedTemporaryFile(delete=True)
                try:
                    downloader.download_file(digest, temp_file.name, queue=False)
                except NotFoundError:
                    return None
                reader = io.BufferedReader(temp_file)
                reader.seek(0)
                return reader
            else:
                blob = downloader.get_blob(digest)
                if blob is not None:
                    return io.BytesIO(blob)
                else:
                    return None

    def delete_blob(self, digest: Digest) -> None:
        """The REAPI doesn't have a deletion method, so we can't support
        deletion for remote storage.
        """
        raise NotImplementedError("Deletion is not supported for remote storage!")

    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        """The REAPI doesn't have a deletion method, so we can't support
        bulk deletion for remote storage.
        """
        raise NotImplementedError("Bulk deletion is not supported for remote storage!")

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        if self.channel is None:
            raise GrpcUninitializedError("Remote CAS backend used before gRPC initialization.")

        write_session.seek(0)
        LOGGER.debug("Writing blob.", tags=dict(digest=digest))
        with upload(
            self.channel, instance=self.remote_instance_name, retries=self.retries, max_backoff=self.max_backoff
        ) as uploader:
            uploader.put_blob(write_session, digest=digest)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        if self._stub_cas is None:
            raise GrpcUninitializedError("Remote CAS backend used before gRPC initialization.")

        # Avoid expensive string creation.
        if LOGGER.is_enabled_for(logging.DEBUG):
            if len(digests) > 100:
                LOGGER.debug(f"Missing blobs request for: {digests[:100]} (truncated)")
            else:
                LOGGER.debug(f"Missing blobs request for: {digests}")

        request = remote_execution_pb2.FindMissingBlobsRequest(instance_name=self.remote_instance_name)

        for blob in digests:
            request_digest = request.blob_digests.add()
            request_digest.hash = blob.hash
            request_digest.size_bytes = blob.size_bytes

        response = self._stub_cas.FindMissingBlobs(request, metadata=metadata_list())

        return list(response.missing_blob_digests)

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        if self._stub_cas is None or self.channel is None:
            raise GrpcUninitializedError("Remote CAS backend used before gRPC initialization.")

        sent_digests = []
        with upload(
            self.channel, instance=self.remote_instance_name, retries=self.retries, max_backoff=self.max_backoff
        ) as uploader:
            for digest, blob in blobs:
                if len(blob) != digest.size_bytes or HASH(blob).hexdigest() != digest.hash:
                    sent_digests.append(remote_execution_pb2.Digest())
                else:
                    sent_digests.append(uploader.put_blob(io.BytesIO(blob), digest=digest, queue=True))

        assert len(sent_digests) == len(blobs)

        return [
            status_pb2.Status(code=code_pb2.OK) if d.ByteSize() > 0 else status_pb2.Status(code=code_pb2.UNKNOWN)
            for d in sent_digests
        ]

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        if self._stub_cas is None or self.channel is None:
            raise GrpcUninitializedError("Remote CAS backend used before gRPC initialization.")

        # Avoid expensive string creation.
        if LOGGER.is_enabled_for(logging.DEBUG):
            LOGGER.debug(f"Bulk read blobs request for: {digests}")

        with download(
            self.channel, instance=self.remote_instance_name, retries=self.retries, max_backoff=self.max_backoff
        ) as downloader:
            results = downloader.get_available_blobs(digests)
            # Transform List of (data, digest) pairs to expected hash-blob map
            return {digest.hash: data for data, digest in results}
