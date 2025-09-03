# Copyright (C) 2023 Bloomberg LP
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


from collections import defaultdict
from contextlib import ExitStack
from typing import IO, Callable, Iterable, Iterator, TypeVar

import mmh3

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric
from buildgrid.server.threading import ContextThreadPoolExecutor

from .storage_abc import StorageABC

LOGGER = buildgrid_logger(__name__)


_T = TypeVar("_T")
_R = TypeVar("_R")


# wrapper functions for the bulk StorageABC interfaces
def _bulk_delete_for_storage(storage_digests: tuple[StorageABC, list[Digest]]) -> list[str]:
    storage, digests = storage_digests
    return storage.bulk_delete(digests)


def _fmb_for_storage(storage_digests: tuple[StorageABC, list[Digest]]) -> list[Digest]:
    storage, digests = storage_digests
    return storage.missing_blobs(digests)


def _bulk_update_for_storage(
    storage_digests: tuple[StorageABC, list[tuple[Digest, bytes]]],
) -> tuple[StorageABC, list[Status]]:
    storage, digest_tuples = storage_digests
    return storage, storage.bulk_update_blobs(digest_tuples)


def _bulk_read_for_storage(storage_digests: tuple[StorageABC, list[Digest]]) -> dict[str, bytes]:
    storage, digests = storage_digests
    return storage.bulk_read_blobs(digests)


class ShardedStorage(StorageABC):
    TYPE = "Sharded"

    def __init__(self, storages: dict[str, StorageABC], thread_pool_size: int | None = None):
        self._stack = ExitStack()
        if not storages:
            raise ValueError("ShardedStorage requires at least one shard")
        self._storages = storages
        self._threadpool = None
        if thread_pool_size:
            self._threadpool = ContextThreadPoolExecutor(thread_pool_size, "sharded-storage")

    def start(self) -> None:
        if self._threadpool:
            self._stack.enter_context(self._threadpool)
        for storage in self._storages.values():
            self._stack.enter_context(storage)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info(f"Stopped {type(self).__name__}")

    def _storage_from_digest(self, digest: Digest) -> StorageABC:
        def _score(shard_name: str, digest: Digest) -> int:
            hash = mmh3.hash(f"{shard_name}\t{digest.hash}", signed=False)
            return hash

        shard_name = min(self._storages.keys(), key=lambda name: _score(name, digest))
        return self._storages[shard_name]

    def _partition_digests(self, digests: list[Digest]) -> dict[StorageABC, list[Digest]]:
        partition: dict[StorageABC, list[Digest]] = defaultdict(list)
        for digest in digests:
            storage = self._storage_from_digest(digest)
            partition[storage].append(digest)
        return partition

    def _map(self, fn: Callable[[_T], _R], args: Iterable[_T]) -> Iterator[_R]:
        if self._threadpool:
            return self._threadpool.map(fn, args)
        else:
            return map(fn, args)

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        return self._storage_from_digest(digest).has_blob(digest)

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        return self._storage_from_digest(digest).get_blob(digest)

    @timed(METRIC.STORAGE.STREAM_READ_DURATION, type=TYPE)
    def stream_read_blob(self, digest: Digest, chunk_size: int, offset: int = 0, limit: int = 0) -> Iterator[bytes]:
        yield from self._storage_from_digest(digest).stream_read_blob(digest, chunk_size, offset, limit)

    @timed(METRIC.STORAGE.STREAM_WRITE_DURATION, type=TYPE)
    def stream_write_blob(self, digest: Digest, chunks: Iterator[bytes]) -> None:
        self._storage_from_digest(digest).stream_write_blob(digest, chunks)

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        self._storage_from_digest(digest).delete_blob(digest)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        self._storage_from_digest(digest).commit_write(digest, write_session)

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        failed_deletions: list[str] = []
        for result in self._map(_bulk_delete_for_storage, self._partition_digests(digests).items()):
            failed_deletions.extend(result)

        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(failed_deletions), type=self.TYPE)
        return failed_deletions

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        missing_blobs: list[Digest] = []

        for result in self._map(_fmb_for_storage, self._partition_digests(digests).items()):
            missing_blobs.extend(result)

        return missing_blobs

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        partitioned_digests: dict[StorageABC, list[tuple[Digest, bytes]]] = defaultdict(list)
        idx_map: dict[StorageABC, list[int]] = defaultdict(list)
        for orig_idx, digest_tuple in enumerate(blobs):
            storage = self._storage_from_digest(digest_tuple[0])
            partitioned_digests[storage].append(digest_tuple)
            idx_map[storage].append(orig_idx)

        results: list[Status] = [Status(code=code_pb2.INTERNAL, message="inconsistent batch results")] * len(blobs)
        for storage, statuses in self._map(_bulk_update_for_storage, partitioned_digests.items()):
            for status_idx, status in enumerate(statuses):
                results[idx_map[storage][status_idx]] = status
        return results

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        bulk_read_results: dict[str, bytes] = {}
        for result in self._map(_bulk_read_for_storage, self._partition_digests(digests).items()):
            bulk_read_results.update(result)

        return bulk_read_results
