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
LRUMemoryCache
==================

A storage provider that stores data in memory. When the size limit
is reached, items are deleted from the cache with the least recently
used item being deleted first.
"""

import collections
import io
import threading
from typing import IO, Any

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.settings import HASH

from .storage_abc import StorageABC

LOGGER = buildgrid_logger(__name__)


class _NullBytesIO(io.BufferedIOBase):
    """A file-like object that discards all data written to it."""

    def writable(self) -> bool:
        return True

    # TODO how to type an override here? __buffer: bytes | bytearray | memoryview | array | mmap
    def write(self, b: Any) -> int:
        return len(b)


class LRUMemoryCache(StorageABC):
    TYPE = "LRU"

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._storage: "collections.OrderedDict[tuple[str, int], bytes]" = collections.OrderedDict()
        self._bytes_stored = 0
        self._lock = threading.Lock()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug("Checking for blob.", tags=dict(digest=digest))
        with self._lock:
            return self._has_blob(digest)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        with self._lock:
            return [digest for digest in digests if not self._has_blob(digest)]

    def _has_blob(self, digest: Digest) -> bool:
        key = (digest.hash, digest.size_bytes)
        if key in self._storage:
            self._storage.move_to_end(key)
            return True
        return False

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        LOGGER.debug("Getting blob.", tags=dict(digest=digest))
        with self._lock:
            if (result := self._get_blob(digest)) is not None:
                return io.BytesIO(result)
            return None

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        with self._lock:
            return {digest.hash: result for digest in digests if (result := self._get_blob(digest)) is not None}

    def _get_blob(self, digest: Digest) -> bytes | None:
        key = (digest.hash, digest.size_bytes)
        if key in self._storage:
            self._storage.move_to_end(key)
            return self._storage[key]
        return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug("Deleting blob.", tags=dict(digest=digest))
        with self._lock:
            self._delete_blob(digest)

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        with self._lock:
            for digest in digests:
                self._delete_blob(digest)
        return []

    def _delete_blob(self, digest: Digest) -> None:
        if self._storage.pop((digest.hash, digest.size_bytes), None):
            self._bytes_stored -= digest.size_bytes

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        with self._lock:
            self._commit_write(digest, write_session)

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        with self._lock:
            result = []
            for digest, data in blobs:
                if len(data) != digest.size_bytes or HASH(data).hexdigest() != digest.hash:
                    result.append(Status(code=code_pb2.INVALID_ARGUMENT, message="Data doesn't match hash"))
                    continue
                try:
                    self._commit_write(digest, io.BytesIO(data))
                    result.append(Status(code=code_pb2.OK))
                except Exception as e:
                    result.append(Status(code=code_pb2.UNKNOWN, message=str(e)))
            return result

    def _commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug("Writing blob.", tags=dict(digest=digest))
        if digest.size_bytes > self._limit:
            # We can't cache this object, so return without doing anything.
            return

        key = (digest.hash, digest.size_bytes)
        if key in self._storage:
            # Digest already in cache, mark it as recently used
            self._storage.move_to_end(key)
            return

        size_after_write = self._bytes_stored + digest.size_bytes
        if size_after_write > self._limit:
            # Delete stuff until there's enough space to write this blob
            LOGGER.debug(
                "LRU cleanup triggered.",
                tags=dict(current_size=self._bytes_stored, limit=self._limit, additional_bytes=digest.size_bytes),
            )
            while size_after_write > self._limit:
                deleted_key = self._storage.popitem(last=False)[0]
                self._bytes_stored -= deleted_key[1]
                size_after_write -= deleted_key[1]
            LOGGER.debug("LRU cleanup finished.", tags=dict(current_size=self._bytes_stored))
        elif size_after_write < 0:
            # This should never happen
            LOGGER.error(
                "LRU overflow writing a additional bytes.",
                tags=dict(
                    digest=digest,
                    additional_bytes=digest.size_bytes,
                    current_size=self._bytes_stored,
                    size_after_write=size_after_write,
                ),
            )
            raise OverflowError()

        write_session.seek(0)
        self._storage[key] = write_session.read()
        self._bytes_stored += digest.size_bytes
