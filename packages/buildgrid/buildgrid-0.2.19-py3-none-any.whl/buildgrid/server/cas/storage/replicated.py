# Copyright (C) 2024 Bloomberg LP
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
ReplicatedStorage
=========================

A storage provider which stores data in multiple storages, replicating
any data missing in some but present in others.

"""
import queue
import threading
from contextlib import ExitStack
from typing import IO, Any, List

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric
from buildgrid.server.settings import MAX_REQUEST_COUNT, MAX_REQUEST_SIZE
from buildgrid.server.threading import ContextWorker
from buildgrid.server.utils.digests import HashableDigest

from .storage_abc import StorageABC

LOGGER = buildgrid_logger(__name__)


class ReplicatedStorage(StorageABC):
    TYPE = "Replicated"

    def __init__(
        self,
        storages: list[StorageABC],
        replication_queue_size: int = 0,
        replication_threadpool_size: int = 1,
        read_replication: bool = True,
    ) -> None:
        self._stack = ExitStack()
        self._storages = dict(enumerate(storages))
        self._enable_replication_threads = False
        self._read_replication = read_replication

        self._replica_queue: queue.Queue[Any] = queue.Queue(maxsize=replication_queue_size)
        self.replication_workers: list[ContextWorker] = [
            ContextWorker(name=f"Replicator-{i}", target=self.replication_loop)
            for i in range(replication_threadpool_size)
        ]

        if replication_queue_size > 0:
            self._enable_replication_threads = True

    def start(self) -> None:
        for storage in self._storages.values():
            self._stack.enter_context(storage)
        if self._enable_replication_threads:
            for replication_worker in self.replication_workers:
                self._stack.enter_context(replication_worker)

    def stop(self) -> None:
        self._stack.close()

    def replication_loop(self, shutdown_requested: threading.Event) -> None:
        # Go through all items in the replication queue and call either
        # get_blob or bulk_read_blobs on them to kick off replication
        # to all necessary storages
        while not shutdown_requested.is_set():
            try:
                digests_to_replicate: List[Digest] = self._replica_queue.get(timeout=1)
            except queue.Empty:
                continue
            try:
                # Go through the digests to replicate and batch them where possible
                batch: List[Digest] = []
                batch_size = 0
                for digest in digests_to_replicate:
                    if digest.size_bytes > MAX_REQUEST_SIZE:
                        _ = self._get_blob(digest, replicate_on_read=True)
                        continue

                    if len(batch) + 1 > MAX_REQUEST_COUNT or batch_size + digest.size_bytes > MAX_REQUEST_SIZE:

                        _ = self._bulk_read_blobs(batch, replicate_on_read=True)
                        batch = []
                        batch_size = 0

                    batch.append(digest)
                    batch_size += digest.size_bytes

                if len(batch) > 0:
                    _ = self._bulk_read_blobs(batch, replicate_on_read=True)
            except Exception:
                LOGGER.exception(f"Caught exception while replicating {digests_to_replicate}")
                shutdown_requested.wait(timeout=1)
            self._replica_queue.task_done()

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        has_blob: set[int] = set(i for i in self._storages if self._storages[i].has_blob(digest))
        missing_blob = set(self._storages.keys()) - has_blob
        if len(missing_blob) < len(self._storages):
            publish_counter_metric(METRIC.STORAGE.REPLICATED.REQUIRED_REPLICATION_COUNT, len(missing_blob))
        return len(has_blob) > 0

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        return self._get_blob(digest, replicate_on_read=self._read_replication)

    def _get_blob(self, digest: Digest, replicate_on_read: bool) -> IO[bytes] | None:
        has_blob: set[int] = set(i for i in self._storages if self._storages[i].has_blob(digest))
        missing_blob = set(self._storages.keys()) - has_blob
        blob = None
        failed_writes = 0
        for idx in has_blob:
            if blob := self._storages[idx].get_blob(digest):
                break
            LOGGER.error(
                "Storage shard reported digest exists but downloading failed.",
                tags=dict(shard_index=idx, digest=digest),
            )
            missing_blob.add(idx)
        if len(missing_blob) < len(self._storages):
            if replicate_on_read:
                assert blob is not None
                for idx in missing_blob:
                    try:
                        self._storages[idx].commit_write(digest, blob)
                        LOGGER.debug("Replicated digest to storage shard.", tags=dict(shard_index=idx, digest=digest))
                    except Exception as e:
                        LOGGER.warning(
                            f"Failed to replicate digest to storage shard: {e}.",
                            tags=dict(shard_index=idx, digest=digest),
                        )
                        failed_writes += 1
                    blob.seek(0)

                publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, failed_writes)
                publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_COUNT, len(missing_blob) - failed_writes)
            else:
                for idx in missing_blob:
                    LOGGER.debug(
                        "Blob pending replication for storage shard.", tags=dict(shard_index=idx, digest=digest)
                    )
        return blob

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        for storage in self._storages.values():
            storage.delete_blob(digest)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        failed_writes = 0
        error_msgs: list[str] = []
        for idx, storage in self._storages.items():
            try:
                storage.commit_write(digest, write_session)
            except Exception as error:
                LOGGER.warning(
                    f"Failed to write digest to storage shard: {error}", tags=dict(shard_index=idx, digest=digest)
                )
                error_msgs.append(str(error))
                failed_writes += 1
            write_session.seek(0)

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, failed_writes)
        if failed_writes == len(self._storages):
            error_string = "Writes to all storages failed with the following errors:\n"
            error_string += "\n".join(error_msgs)
            LOGGER.error(error_string)
            raise RuntimeError(error_string)

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        failed_deletions_set: set[str] = set()
        for storage in self._storages.values():
            failed_deletions_set.union(storage.bulk_delete(digests))
        publish_counter_metric(METRIC.STORAGE.DELETE_ERRORS_COUNT, len(failed_deletions_set), type=self.TYPE)
        return list(failed_deletions_set)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        """Call missing_blobs on each storage and only report a blob is missing if it's in none of the
        storages. The number of blobs missing from a storage but present in others is logged and published
        as a metric
        """
        missing_for_storage: dict[int, set[HashableDigest]] = {}
        for idx, storage in self._storages.items():
            response = storage.missing_blobs(digests)
            missing_for_storage[idx] = {HashableDigest(digest.hash, digest.size_bytes) for digest in response}

        # Find the set of inconsistent digests, defined as digests which are missing in some, but not all, storages.
        missing_from_all_storages = set.intersection(*missing_for_storage.values())
        inconsistent_digests: set[HashableDigest] = (
            set.union(*missing_for_storage.values()) - missing_from_all_storages
        )
        for idx, missing_digests in missing_for_storage.items():
            inconsistent_digests_for_storage = missing_digests & inconsistent_digests
            if inconsistent_digests_for_storage:
                LOGGER.info(
                    "Storage shard has blobs which need to be replicated.",
                    tags=dict(shard_index=idx, digest_count=len(inconsistent_digests_for_storage)),
                )

        if self._enable_replication_threads and len(inconsistent_digests) > 0:
            try:
                self._replica_queue.put_nowait([x.to_digest() for x in inconsistent_digests])
            except queue.Full:
                LOGGER.warning(
                    "Digests to be replicated were skipped due to full replication queue.",
                    tags=dict(skipped_digests=len(inconsistent_digests)),
                )
                publish_counter_metric(
                    METRIC.STORAGE.REPLICATED.REPLICATION_QUEUE_FULL_COUNT, len(inconsistent_digests)
                )
        publish_counter_metric(METRIC.STORAGE.REPLICATED.REQUIRED_REPLICATION_COUNT, len(inconsistent_digests))
        missing_blobs_list = [hdigest.to_digest() for hdigest in missing_from_all_storages]
        return missing_blobs_list

    # Bulk write to all storages. Errors are not fatal as long as one storage is
    # successfully written to
    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        digest_result: dict[HashableDigest, Status] = {}
        errored_blobs_total = 0
        for idx, storage in self._storages.items():
            errored_blobs_for_storage = 0
            results = storage.bulk_update_blobs(blobs)
            for digest_blob_tuple, result in zip(blobs, results):
                digest, _ = digest_blob_tuple
                hdigest = HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes)

                if result.code != code_pb2.OK:
                    errored_blobs_for_storage += 1

                # Keep track of the status code for this digest, preferring OK over errors
                if hdigest not in digest_result or digest_result[hdigest].code != code_pb2.OK:
                    digest_result[hdigest] = result

            if errored_blobs_for_storage > 0:
                LOGGER.warning(
                    "Failed to write all digests to storage shard.",
                    tags=dict(shard_index=idx, digest_count=len(results), error_count=errored_blobs_for_storage),
                )
                errored_blobs_total += errored_blobs_for_storage

        publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, errored_blobs_total)
        return [digest_result[hdigest] for hdigest in digest_result]

    # Read blobs from all storages, writing any missing blobs into storages missing
    # them from storages that have them
    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        return self._bulk_read_blobs(digests, replicate_on_read=self._read_replication)

    def _bulk_read_blobs(self, digests: list[Digest], replicate_on_read: bool) -> dict[str, bytes]:
        digest_set = set(HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes) for digest in digests)
        missing_blobs: dict[int, set[HashableDigest]] = {}
        bulk_read_results: dict[str, bytes] = {}
        # Find what blobs are missing for this storage and read what's available
        for idx, storage in self._storages.items():
            missing_blobs[idx] = set(
                [
                    HashableDigest(hash=digest.hash, size_bytes=digest.size_bytes)
                    for digest in storage.missing_blobs(digests)
                ]
            )
            present_blobs = digest_set - missing_blobs[idx]
            blobs_to_read = [x.to_digest() for x in present_blobs if x.hash not in bulk_read_results]
            bulk_read_results.update(self._storages[idx].bulk_read_blobs(blobs_to_read))

        replicated_blobs_count = 0
        errored_blobs_count = 0
        for idx, missing in missing_blobs.items():
            if replicate_on_read:
                # Write any blobs that exist in other storages which are missing from this storage
                write_batch: list[tuple[Digest, bytes]] = []
                for digest in missing:
                    if digest.hash in bulk_read_results:
                        write_batch.append((digest.to_digest(), bulk_read_results[digest.hash]))
                if write_batch:
                    update_results = self._storages[idx].bulk_update_blobs(write_batch)
                    for result in update_results:
                        if result.code != code_pb2.OK:
                            errored_blobs_count += 1
                        else:
                            replicated_blobs_count += 1
                    LOGGER.debug(
                        "Replicated blobs to storage shard.", tags=dict(shard_index=idx, digest_count=len(write_batch))
                    )
                publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_COUNT, replicated_blobs_count)
                publish_counter_metric(METRIC.STORAGE.REPLICATED.REPLICATION_ERROR_COUNT, errored_blobs_count)
            else:
                LOGGER.debug(
                    "Blobs pending replication for storage shard.",
                    tags=dict(shard_index=idx, digest_count=len(missing)),
                )
        return bulk_read_results
