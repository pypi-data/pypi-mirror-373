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
WithCacheStorage
==================

A storage provider that first checks a cache, then tries a slower
fallback provider.

To ensure clients can reliably store blobs in CAS, only `get_blob`
calls are cached -- `has_blob` and `missing_blobs` will always query
the fallback.
"""


from contextlib import ExitStack
from typing import IO

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_distribution_metric
from buildgrid.server.settings import MAX_IN_MEMORY_BLOB_SIZE_BYTES
from buildgrid.server.threading import ContextThreadPoolExecutor

from .storage_abc import StorageABC, create_write_session

LOGGER = buildgrid_logger(__name__)


class WithCacheStorage(StorageABC):
    TYPE = "WithCache"

    def __init__(
        self,
        cache: StorageABC,
        fallback: StorageABC,
        defer_fallback_writes: bool = False,
        fallback_writer_threads: int = 20,
    ) -> None:
        self._stack = ExitStack()
        self._cache = cache
        self._fallback = fallback
        self._defer_fallback_writes = defer_fallback_writes
        self._fallback_writer_threads = fallback_writer_threads
        self._executor = ContextThreadPoolExecutor(self._fallback_writer_threads, "WithCacheFallbackWriter")

    def start(self) -> None:
        if self._defer_fallback_writes:
            self._stack.enter_context(self._executor)
        self._stack.enter_context(self._cache)
        self._stack.enter_context(self._fallback)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info(f"Stopped {type(self).__name__}")

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        try:
            if self._defer_fallback_writes and self._cache.has_blob(digest):
                return True
        except Exception:
            LOGGER.warning(
                "Failed to check existence of digest in cache storage.", tags=dict(digest=digest), exc_info=True
            )

        return self._fallback.has_blob(digest)

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        try:
            cache_result = self._cache.get_blob(digest)
            if cache_result is not None:
                publish_distribution_metric(METRIC.STORAGE.WITH_CACHE.CACHE_HIT_COUNT, 1)
                return cache_result
        except Exception:
            LOGGER.warning("Failed to read digest from cache storage.", tags=dict(digest=digest), exc_info=True)

        fallback_result = self._fallback.get_blob(digest)
        if fallback_result is None:
            return None

        publish_distribution_metric(METRIC.STORAGE.WITH_CACHE.CACHE_MISS_COUNT, 1)

        try:
            self._cache.commit_write(digest, fallback_result)
        except Exception:
            LOGGER.warning(
                "Failed to write digest to cache storage after reading blob.", tags=dict(digest=digest), exc_info=True
            )

        fallback_result.seek(0)
        return fallback_result

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        self._fallback.delete_blob(digest)
        try:
            self._cache.delete_blob(digest)
        except Exception:
            LOGGER.warning("Failed to delete digest from cache storage.", tags=dict(digest=digest), exc_info=True)

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        # Only report back failures from the fallback
        try:
            cache_failures = self._cache.bulk_delete(digests)
            for failure in cache_failures:
                LOGGER.warning("Failed to delete digest from cache storage.", tags=dict(digest=failure))
            publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(cache_failures), type=self.TYPE)
        except Exception:
            LOGGER.warning("Failed to bulk delete blobs from cache storage.", exc_info=True)

        fallback_failures = self._fallback.bulk_delete(digests)
        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(fallback_failures), type=self.TYPE)
        return fallback_failures

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        written_to_cache = False
        try:
            self._cache.commit_write(digest, write_session)
            written_to_cache = True
        except Exception:
            LOGGER.warning(
                "Failed to commit write of digest to cache storage.", tags=dict(digest=digest), exc_info=True
            )

        if written_to_cache and self._defer_fallback_writes:
            write_session.seek(0)
            deferred_session = create_write_session(digest)
            while data := write_session.read(MAX_IN_MEMORY_BLOB_SIZE_BYTES):
                deferred_session.write(data)

            def deferred_submit() -> None:
                with deferred_session:
                    self._fallback.commit_write(digest, deferred_session)

            self._executor.submit(deferred_submit)
        else:
            self._fallback.commit_write(digest, write_session)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        return self._fallback.missing_blobs(digests)

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        try:
            self._cache.bulk_update_blobs(blobs)
        except Exception:
            LOGGER.warning("Failed to bulk update blobs in cache storage.", exc_info=True)

        return self._fallback.bulk_update_blobs(blobs)

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        try:
            cache_blobs = self._cache.bulk_read_blobs(digests)
        except Exception:
            LOGGER.warning("Failed to bulk read blobs from cache storage.", exc_info=True)
            cache_blobs = {}

        publish_distribution_metric(METRIC.STORAGE.WITH_CACHE.CACHE_HIT_COUNT, len(cache_blobs))

        uncached_digests = [digest for digest in digests if cache_blobs.get(digest.hash, None) is None]

        publish_distribution_metric(METRIC.STORAGE.WITH_CACHE.CACHE_MISS_COUNT, len(digests) - len(cache_blobs))

        metric_cache_percent = 0.0
        if len(digests) > 0:
            metric_cache_percent = len(cache_blobs) / len(digests) * 100
        publish_distribution_metric(METRIC.STORAGE.WITH_CACHE.CACHE_HIT_PERCENT, metric_cache_percent)

        fallback_blobs = self._fallback.bulk_read_blobs(uncached_digests)
        cache_blobs.update(fallback_blobs)

        uncached_blobs = []
        for digest in uncached_digests:
            blob = fallback_blobs.get(digest.hash)
            if blob is not None:
                uncached_blobs.append((digest, blob))

        try:
            self._cache.bulk_update_blobs(uncached_blobs)
        except Exception:
            LOGGER.warning("Failed to add blobs to cache storage after bulk read.", exc_info=True)

        return cache_blobs
