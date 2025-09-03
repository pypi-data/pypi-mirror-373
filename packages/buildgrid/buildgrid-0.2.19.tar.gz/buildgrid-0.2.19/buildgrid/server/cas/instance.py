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
Storage Instances
=================
Instances of CAS and ByteStream
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Iterable, Iterator, Sequence

if TYPE_CHECKING:
    from hashlib import _Hash

from cachetools import TTLCache
from grpc import RpcError

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    BatchReadBlobsResponse,
    BatchUpdateBlobsRequest,
    BatchUpdateBlobsResponse,
    Digest,
    Directory,
    FindMissingBlobsResponse,
    GetTreeRequest,
    GetTreeResponse,
    Tree,
)
from buildgrid._protos.google.bytestream import bytestream_pb2 as bs_pb2
from buildgrid._protos.google.rpc import code_pb2, status_pb2
from buildgrid.server.cas.storage.storage_abc import StorageABC, create_write_session
from buildgrid.server.exceptions import (
    IncompleteReadError,
    InvalidArgumentError,
    NotFoundError,
    OutOfRangeError,
    PermissionDeniedError,
    RetriableError,
)
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_distribution_metric
from buildgrid.server.servicer import Instance
from buildgrid.server.settings import HASH, HASH_LENGTH, MAX_REQUEST_COUNT, MAX_REQUEST_SIZE, STREAM_ERROR_RETRY_PERIOD
from buildgrid.server.utils.digests import create_digest

LOGGER = buildgrid_logger(__name__)

EMPTY_BLOB = b""
EMPTY_BLOB_DIGEST: Digest = create_digest(EMPTY_BLOB)


class ContentAddressableStorageInstance(Instance):
    SERVICE_NAME = RE_DESCRIPTOR.services_by_name["ContentAddressableStorage"].full_name

    def __init__(
        self,
        storage: StorageABC,
        read_only: bool = False,
        tree_cache_size: int | None = None,
        tree_cache_ttl_minutes: float = 60,
    ) -> None:
        self._storage = storage
        self.__read_only = read_only

        self._tree_cache: TTLCache[tuple[str, int], Digest] | None = None
        if tree_cache_size:
            self._tree_cache = TTLCache(tree_cache_size, tree_cache_ttl_minutes * 60)

    def start(self) -> None:
        self._storage.start()

    def stop(self) -> None:
        self._storage.stop()
        LOGGER.info("Stopped CAS.")

    def find_missing_blobs(self, blob_digests: Sequence[Digest]) -> FindMissingBlobsResponse:
        deduplicated_digests: list[Digest] = []
        seen: set[str] = set()
        for digest in blob_digests:
            if digest.hash in seen:
                continue
            seen.add(digest.hash)
            deduplicated_digests.append(digest)
        blob_digests = deduplicated_digests

        missing_blobs = self._storage.missing_blobs(blob_digests)

        num_blobs_in_request = len(blob_digests)
        if num_blobs_in_request > 0:
            num_blobs_missing = len(missing_blobs)
            percent_missing = float((num_blobs_missing / num_blobs_in_request) * 100)

            publish_distribution_metric(METRIC.CAS.BLOBS_COUNT, num_blobs_in_request)
            publish_distribution_metric(METRIC.CAS.BLOBS_MISSING_COUNT, num_blobs_missing)
            publish_distribution_metric(METRIC.CAS.BLOBS_MISSING_PERCENT, percent_missing)

        for digest in blob_digests:
            publish_distribution_metric(METRIC.CAS.BLOB_BYTES, digest.size_bytes)

        return FindMissingBlobsResponse(missing_blob_digests=missing_blobs)

    def batch_update_blobs(self, requests: Sequence[BatchUpdateBlobsRequest.Request]) -> BatchUpdateBlobsResponse:
        if self.__read_only:
            raise PermissionDeniedError("CAS is read-only")

        if len(requests) > 0:
            publish_distribution_metric(METRIC.CAS.BLOBS_COUNT, len(requests))

        storage = self._storage
        store = []
        seen: set[str] = set()
        for request_proto in requests:
            if request_proto.digest.hash in seen:
                continue
            seen.add(request_proto.digest.hash)
            store.append((request_proto.digest, request_proto.data))
            publish_distribution_metric(METRIC.CAS.BLOB_BYTES, request_proto.digest.size_bytes)

        response = BatchUpdateBlobsResponse()
        statuses = storage.bulk_update_blobs(store)

        for (digest, _), status in zip(store, statuses):
            response_proto = response.responses.add()
            response_proto.digest.CopyFrom(digest)
            response_proto.status.CopyFrom(status)

        return response

    def batch_read_blobs(self, digests: Sequence[Digest]) -> BatchReadBlobsResponse:
        storage = self._storage

        if len(digests) > 0:
            publish_distribution_metric(METRIC.CAS.BLOBS_COUNT, len(digests))

        # Only process unique digests
        good_digests = []
        bad_digests = []
        seen: set[str] = set()
        requested_bytes = 0
        for digest in digests:
            if digest.hash in seen:
                continue
            seen.add(digest.hash)

            if len(digest.hash) != HASH_LENGTH:
                bad_digests.append(digest)
            else:
                good_digests.append(digest)
                requested_bytes += digest.size_bytes

        if requested_bytes > MAX_REQUEST_SIZE:
            raise InvalidArgumentError(
                "Combined total size of blobs exceeds "
                "server limit. "
                f"({requested_bytes} > {MAX_REQUEST_SIZE} [byte])"
            )

        if len(good_digests) > 0:
            blobs_read = storage.bulk_read_blobs(good_digests)
        else:
            blobs_read = {}

        response = BatchReadBlobsResponse()

        for digest in good_digests:
            response_proto = response.responses.add()
            response_proto.digest.CopyFrom(digest)

            if digest.hash in blobs_read and blobs_read[digest.hash] is not None:
                response_proto.data = blobs_read[digest.hash]
                status_code = code_pb2.OK

                publish_distribution_metric(METRIC.CAS.BLOB_BYTES, digest.size_bytes)
            else:
                status_code = code_pb2.NOT_FOUND
                LOGGER.info("Blob not found from BatchReadBlobs.", tags=dict(digest=digest))

            response_proto.status.CopyFrom(status_pb2.Status(code=status_code))

        for digest in bad_digests:
            response_proto = response.responses.add()
            response_proto.digest.CopyFrom(digest)
            status_code = code_pb2.INVALID_ARGUMENT
            response_proto.status.CopyFrom(status_pb2.Status(code=status_code))

        return response

    def lookup_tree_cache(self, root_digest: Digest) -> Tree | None:
        """Find full Tree from cache"""
        if self._tree_cache is None:
            return None
        tree = None
        if response_digest := self._tree_cache.get((root_digest.hash, root_digest.size_bytes)):
            tree = self._storage.get_message(response_digest, Tree)
            if tree is None:
                self._tree_cache.pop((root_digest.hash, root_digest.size_bytes))

        publish_counter_metric(METRIC.CAS.TREE_CACHE_HIT_COUNT, 1 if tree else 0)
        return tree

    def put_tree_cache(self, root_digest: Digest, root: Directory, children: Iterable[Directory]) -> None:
        """Put Tree with a full list of directories into CAS"""
        if self._tree_cache is None:
            return
        tree = Tree(root=root, children=children)
        message_blob = tree.SerializeToString()
        tree_digest = Digest(hash=HASH(message_blob).hexdigest(), size_bytes=len(message_blob))
        if self._storage.missing_blobs([tree_digest]):
            self._storage.put_message(tree)
        self._tree_cache[(root_digest.hash, root_digest.size_bytes)] = tree_digest

    def get_tree(self, request: GetTreeRequest) -> Iterator[GetTreeResponse]:
        storage = self._storage

        if not request.page_size:
            request.page_size = MAX_REQUEST_COUNT

        if tree := self.lookup_tree_cache(request.root_digest):
            # Cache hit, yield responses based on page size
            directories = [tree.root]
            directories.extend(tree.children)
            yield from (
                GetTreeResponse(directories=directories[start : start + request.page_size])
                for start in range(0, len(directories), request.page_size)
            )
            return

        results = []
        response = GetTreeResponse()

        for dir in storage.get_tree(request.root_digest):
            response.directories.append(dir)
            results.append(dir)
            if len(response.directories) >= request.page_size:
                yield response
                response.Clear()

        if response.directories:
            yield response
        if results:
            self.put_tree_cache(request.root_digest, results[0], results[1:])


@dataclass
class WriteBlobState:
    hash: "_Hash"
    bytes_count: int

    def update(self, data: bytes) -> None:
        self.hash.update(data)
        self.bytes_count += len(data)

    def validate(self, digest: Digest) -> None:
        if self.bytes_count != digest.size_bytes:
            raise NotImplementedError(
                "Cannot close stream before finishing write, "
                f"got {self.bytes_count} bytes but expected {digest.size_bytes}"
            )

        if self.hash.hexdigest() != digest.hash:
            raise InvalidArgumentError("Data does not match hash")


class ByteStreamInstance(Instance):
    SERVICE_NAME = bs_pb2.DESCRIPTOR.services_by_name["ByteStream"].full_name

    BLOCK_SIZE = 1 * 1024 * 1024  # 1 MB block size

    def __init__(
        self,
        storage: StorageABC,
        read_only: bool = False,
        disable_overwrite_early_return: bool = False,
        stream_blob: bool = True,
    ) -> None:
        self._storage = storage
        self._query_activity_timeout = 30

        self.__read_only = read_only

        # If set, prevents `ByteStream.Write()` from returning without
        # reading all the client's `WriteRequests` for a digest that is
        # already in storage (i.e. not follow the REAPI-specified
        # behavior).
        self.__disable_overwrite_early_return = disable_overwrite_early_return
        # (Should only be used to work around issues with implementations
        # that treat the server half-closing its end of the gRPC stream
        # as a HTTP/2 stream error.)

        self._stream_blob = stream_blob

    def start(self) -> None:
        self._storage.start()

    def stop(self) -> None:
        self._storage.stop()
        LOGGER.info("Stopped ByteStream.")

    def read_cas_blob(self, digest: Digest, read_offset: int, read_limit: int) -> Iterator[bs_pb2.ReadResponse]:
        digest_str = f"'{digest.hash}/{digest.size_bytes}'"
        # Check the given read offset and limit.
        if read_offset < 0 or read_offset > digest.size_bytes:
            raise OutOfRangeError(f"Read offset out of range for {digest_str}: {read_offset=}")

        if read_limit < 0:
            raise InvalidArgumentError(f"Read limit out of range for {digest_str}: {read_limit=}")

        bytes_requested = digest.size_bytes - read_offset
        if read_limit:
            bytes_requested = min(read_limit, bytes_requested)

        if bytes_requested == 0:
            yield bs_pb2.ReadResponse(data=b"")
            return

        bytes_remaining = bytes_requested

        if self._stream_blob:
            # Read the blob as a stream of chunks
            for block_data in self._storage.stream_read_blob(digest, self.BLOCK_SIZE, read_offset, bytes_requested):
                yield bs_pb2.ReadResponse(data=block_data)
                bytes_remaining -= len(block_data)
                publish_distribution_metric(METRIC.CAS.BLOB_BYTES, len(block_data))
        else:
            # Read the blob from storage and send its contents to the client.
            result = self._storage.get_blob(digest)
            if result is None:
                raise NotFoundError(f"Blob not found for {digest_str}")

            try:
                if read_offset > 0:
                    result.seek(read_offset)

                publish_distribution_metric(METRIC.CAS.BLOB_BYTES, digest.size_bytes)

                # https://docs.python.org/3/library/io.html#io.RawIOBase.read
                # If 0 bytes are returned, and size was not 0, this indicates end of file.
                while block_data := result.read(min(self.BLOCK_SIZE, bytes_remaining)):
                    bytes_remaining -= len(block_data)
                    yield bs_pb2.ReadResponse(data=block_data)
            finally:
                result.close()

        if bytes_remaining != 0:
            raise IncompleteReadError(
                f"Blob incomplete: {digest_str}, from Bytestream.Read. "
                f"Only read {bytes_requested - bytes_remaining} bytes out of "
                f"requested {bytes_requested} bytes. {read_offset=} {read_limit=}"
            )

    def write_cas_blob(
        self, digest_hash: str, digest_size: str, requests: Iterator[bs_pb2.WriteRequest]
    ) -> bs_pb2.WriteResponse:
        if self.__read_only:
            raise PermissionDeniedError("ByteStream is read-only")

        if len(digest_hash) != HASH_LENGTH or not digest_size.isdigit():
            raise InvalidArgumentError(f"Invalid digest [{digest_hash}/{digest_size}]")

        digest = Digest(hash=digest_hash, size_bytes=int(digest_size))

        publish_distribution_metric(METRIC.CAS.BLOB_BYTES, digest.size_bytes)

        if self._storage.has_blob(digest):
            # According to the REAPI specification:
            # "When attempting an upload, if another client has already
            # completed the upload (which may occur in the middle of a single
            # upload if another client uploads the same blob concurrently),
            # the request will terminate immediately [...]".
            #
            # However, half-closing the stream can be problematic with some
            # intermediaries like HAProxy.
            # (https://github.com/haproxy/haproxy/issues/1219)
            #
            # If half-closing the stream is not allowed, we read and drop
            # all the client's messages before returning, still saving
            # the cost of a write to storage.
            if self.__disable_overwrite_early_return:
                try:
                    for request in requests:
                        if request.finish_write:
                            break
                        continue
                except RpcError:
                    msg = "ByteStream client disconnected whilst streaming requests, upload cancelled."
                    LOGGER.debug(msg)
                    raise RetriableError(msg, retry_period=timedelta(seconds=STREAM_ERROR_RETRY_PERIOD))

            return bs_pb2.WriteResponse(committed_size=digest.size_bytes)

        # Start the write session and write the first request's data.
        write_state = WriteBlobState(hash=HASH(), bytes_count=0)

        if self._stream_blob:

            def gen_chunk() -> Iterator[bytes]:
                try:
                    for request in requests:
                        yield request.data
                        write_state.update(request.data)
                        if request.finish_write:
                            break
                except RpcError:
                    msg = "ByteStream client disconnected whilst streaming requests, upload cancelled."
                    LOGGER.debug(msg)
                    raise RetriableError(msg, retry_period=timedelta(seconds=STREAM_ERROR_RETRY_PERIOD))

                # Check that the data matches the provided digest.
                write_state.validate(digest)

            self._storage.stream_write_blob(digest, gen_chunk())

        else:
            with create_write_session(digest) as write_session:
                try:
                    for request in requests:
                        write_session.write(request.data)
                        write_state.update(request.data)

                        if request.finish_write:
                            break
                except RpcError:
                    write_session.close()
                    msg = "ByteStream client disconnected whilst streaming requests, upload cancelled."
                    LOGGER.debug(msg)
                    raise RetriableError(msg, retry_period=timedelta(seconds=STREAM_ERROR_RETRY_PERIOD))

                # Check that the data matches the provided digest.
                write_state.validate(digest)

                self._storage.commit_write(digest, write_session)

        return bs_pb2.WriteResponse(committed_size=write_state.bytes_count)
