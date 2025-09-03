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

"""
A storage provider that uses redis to maintain existence and expiry metadata
for a storage.
"""


import time
from datetime import datetime, timedelta, timezone
from typing import IO, Iterator, Optional

import redis

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.cas.storage.index.index_abc import IndexABC
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.decorators import timed
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_gauge_metric
from buildgrid.server.redis.provider import RedisProvider
from buildgrid.server.utils.digests import validate_digest_data

LOGGER = buildgrid_logger(__name__)


class RedisIndex(IndexABC):
    TYPE = "RedisIndex"

    def __init__(self, redis: RedisProvider, storage: StorageABC, prefix: Optional[str] = None) -> None:
        self._redis = redis
        self._storage = storage
        self._prefix = "A"
        self._total_size_key = "total_size"
        if prefix == "A":
            LOGGER.error("Prefix 'A' is reserved as the default prefix and cannot be used")
            raise ValueError("Prefix 'A' is reserved as the default prefix and cannot be used")
        elif prefix:
            self._prefix = prefix
            self._total_size_key = self._prefix + ":" + self._total_size_key
        # TODO: make this configurable, and lower the default
        self._ttl = timedelta(days=365)

        # Keep track of the last returned scan cursor
        # to not start at the beginning for each call to `delete_n_bytes`
        self._delete_n_bytes_cursor = 0

    def start(self) -> None:
        self._storage.start()

    def stop(self) -> None:
        self._storage.stop()

    def _construct_key(self, digest: Digest) -> str:
        """Helper to get the redis key name for a particular digest"""
        # The tag prefix serves to distinguish between our keys and
        # actual blobs if the same redis is used for both index and storage
        return self._prefix + ":" + digest.hash + "_" + str(digest.size_bytes)

    def _deconstruct_key(self, keystr: str) -> Digest | None:
        """Helper to attempt to recover a Digest from a redis key"""

        try:
            tag, rest = keystr.split(":", 1)
            if tag != self._prefix:
                return None
            hash, size_bytes = rest.rsplit("_", 1)
            return Digest(hash=hash, size_bytes=int(size_bytes))
        except ValueError:
            return None

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        # Redis is authoritative for existence, no need to check storage.
        return bool(self._redis.execute_ro(lambda r: r.exists(self._construct_key(digest))))

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        if blob := self._storage.get_blob(digest):
            return blob

        deleted_index_digests = self._bulk_delete_from_index([digest])
        for digest in deleted_index_digests:
            LOGGER.warning("Blob was indexed but not in storage. Deleted from the index.", tags=dict(digest=digest))

        return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        # If the initial delete doesn't delete anything due to the key not existing
        # don't do anything else
        if self._redis.execute_rw(lambda r: r.delete(self._construct_key(digest))):
            self._storage.delete_blob(digest)

            # If we race with a blob being re-added we might have just deleted the
            # storage out from under it. We don't want the index to end up with
            # keys for things that are not present in storage since we consider
            # the index authoritative for existance. So we delete the keys again
            # after deleting from storage, this way if they do get out of sync it
            # will be in the direction of leaking objects in storage that the
            # index doesn't know about.
            def delete_from_index(r: "redis.Redis[bytes]") -> None:
                pipe = r.pipeline()
                pipe.delete(self._construct_key(digest))
                pipe.decrby(self._total_size_key, digest.size_bytes)
                pipe.execute()

            self._redis.execute_rw(delete_from_index)

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        self._storage.commit_write(digest, write_session)

        def set_ttl(r: "redis.Redis[bytes]") -> None:
            key = self._construct_key(digest)
            # Only increment total_size if this key is new
            # Use a dummy value of 1. We only care about existence and expiry
            if r.set(key, 1, ex=self._ttl, nx=True) is not None:
                r.incrby(self._total_size_key, digest.size_bytes)

        self._redis.execute_rw(set_ttl)

    def _bulk_delete_from_index(self, digests: list[Digest]) -> list[Digest]:
        def delete_from_index(r: "redis.Redis[bytes]") -> list[Digest]:
            pipe = r.pipeline()
            bytes_deleted = 0
            for digest in digests:
                pipe.delete(self._construct_key(digest))
            results = pipe.execute()
            # Go through the delete calls and only decrement total_size for the keys
            # which were actually removed
            successful_deletes = []
            for result, digest in zip(results, digests):
                if result:
                    bytes_deleted += digest.size_bytes
                    successful_deletes.append(digest)
            r.decrby(self._total_size_key, bytes_deleted)
            return successful_deletes

        successful_deletes = self._redis.execute_rw(delete_from_index)
        return successful_deletes

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        # Delete from the index and then delete from the backing storage.
        successful_deletes = self._bulk_delete_from_index(digests)
        failed_deletes = self._storage.bulk_delete(successful_deletes)
        return failed_deletes

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        # We hit the RW node for every FMB call to extend all the TTLs.
        # This could try to take advantage of RO replicas by only hitting the
        # RW node for blobs that do not have enough TTL left, if any.
        # We currently rely on the always-updated TTL to determine if a blob
        # should be protected in mark_n_bytes_as_deleted. If we allow some
        # slop before updating the RW node here we need to account for it
        # there too.
        def extend_ttls(r: "redis.Redis[bytes]") -> list[int]:
            pipe = r.pipeline(transaction=False)
            for digest in digests:
                pipe.expire(name=self._construct_key(digest), time=self._ttl)
            return pipe.execute()

        extend_results = self._redis.execute_rw(extend_ttls)

        return [digest for digest, result in zip(digests, extend_results) if result != 1]

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        result_map: dict[str, Status] = {}
        missing_blob_pairs: list[tuple[Digest, bytes]] = []
        missing_blobs = self.missing_blobs([digest for digest, _ in blobs])
        for digest, blob in blobs:
            if digest not in missing_blobs:
                if validate_digest_data(digest, blob):
                    result_map[digest.hash] = Status(code=code_pb2.OK)
                else:
                    result_map[digest.hash] = Status(code=code_pb2.INVALID_ARGUMENT, message="Data doesn't match hash")
            else:
                missing_blob_pairs.append((digest, blob))
        results = self._storage.bulk_update_blobs(missing_blob_pairs)

        def set_ttls(r: "redis.Redis[bytes]") -> None:
            pipe = r.pipeline()
            bytes_added = 0
            for digest, result in zip(missing_blobs, results):
                result_map[digest.hash] = result
                if result.code == code_pb2.OK:
                    key = self._construct_key(digest)
                    # Use a dummy value of 1. We only care about existence and expiry
                    pipe.set(key, 1, ex=self._ttl, nx=True)
            redis_results = pipe.execute()
            # only update total_size for brand new keys
            for result, digest in zip(redis_results, missing_blobs):
                if result is not None:
                    bytes_added += digest.size_bytes
            r.incrby(self._total_size_key, bytes_added)

        self._redis.execute_rw(set_ttls)
        return [result_map[digest.hash] for digest, _ in blobs]

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        fetched_digests = self._storage.bulk_read_blobs(digests)

        fetched_digest_hashes = set(digest_hash for (digest_hash, _) in fetched_digests.items())
        digests_not_in_storage: list[Digest] = []
        for expected_digest in digests:
            if expected_digest.hash not in fetched_digest_hashes:
                digests_not_in_storage.append(expected_digest)

        if digests_not_in_storage:
            deleted_index_digests = self._bulk_delete_from_index(digests_not_in_storage)
            for digest in deleted_index_digests:
                LOGGER.warning(
                    "Blob was indexed but not in storage. Deleted from the index.", tags=dict(digest=digest)
                )

        return fetched_digests

    def least_recent_digests(self) -> Iterator[Digest]:
        """Generator to iterate through the digests in LRU order"""
        # This is not a LRU index, this method is used only from tests.
        raise NotImplementedError()

    def get_total_size(self) -> int:
        """
        Return the sum of the size of all blobs within the index
        """

        # The total_size represents what we have stored in the underlying
        # storage. However, if some redis notifications for expiring keys
        # are missed we won't actually have keys to account for all the size.
        # The expectation is that a "janitor" process will locate orphaned
        # blobs in storage eventually and when it does so it will call our
        # delete_blob which will finally decrby the total_size.
        total_size = self._redis.execute_ro(lambda r: r.get(self._total_size_key))
        if total_size:
            return int(total_size)
        else:
            return 0

    def get_blob_count(self) -> int:
        key_count = int(self._redis.execute_ro(lambda r: r.dbsize()))
        # Subtract 1 to not count the `total_size` key
        # but never return a negative count
        return max(0, key_count - 1)

    def delete_n_bytes(
        self,
        n_bytes: int,
        dry_run: bool = False,
        protect_blobs_after: datetime | None = None,
        large_blob_threshold: int | None = None,
        large_blob_lifetime: datetime | None = None,
    ) -> int:
        """
        Iterate through the Redis Index using 'SCAN' and delete any entries older than
        'protect_blobs_after'. The ordering of the deletes is undefined and can't be assumed
        to be LRU. Large blobs can optionally be configured to have a separate lifetime.
        """
        now = datetime.now(timezone.utc)

        if protect_blobs_after:
            threshold_time = protect_blobs_after
        else:
            threshold_time = now

        seen: set[str] = set()
        bytes_deleted = 0

        while n_bytes > 0:
            # Used for metric publishing
            delete_start_time = time.time()

            # Maybe count should be configurable or somehow self-tuning
            # based on how many deletable keys we're actually getting
            # back per-request.
            # We could also choose random prefixes for the scan so that
            # multiple cleanup process are less likely to contend
            rawkeys: list[bytes]
            previous_cursor = self._delete_n_bytes_cursor
            self._delete_n_bytes_cursor, rawkeys = self._redis.execute_ro(
                lambda r: r.scan(match=f"{self._prefix}:*", cursor=self._delete_n_bytes_cursor, count=1000)
            )
            keys = [key.decode() for key in rawkeys if key != b""]

            def get_ttls(r: "redis.Redis[bytes]") -> list[bytes]:
                pipe = r.pipeline(transaction=False)
                for key in keys:
                    # Skip over any total_size keys
                    if key.split(":")[-1] == "total_size":
                        continue
                    pipe.ttl(key)
                return pipe.execute()

            raw_ttls = self._redis.execute_ro(get_ttls)
            ttls = [int(x) for x in raw_ttls]

            LOGGER.debug("Scan returned.", tags=dict(key_count=len(ttls)))
            digests_to_delete: list[Digest] = []
            failed_deletes: list[str] = []
            new_blob_bytes = 0
            for key, ttl in zip(keys, ttls):
                digest = self._deconstruct_key(key)
                if digest and digest.hash not in seen:
                    seen.add(digest.hash)
                    # Since FMB sets the ttl to self._ttl on every call we can
                    # use the time remaining to figure out when the last FMB
                    # call for that blob was.
                    blob_time = now - (self._ttl - timedelta(seconds=ttl))
                    if n_bytes <= 0:
                        # Reset scan cursor to previous value to not skip
                        # the digests we didn't get to
                        self._delete_n_bytes_cursor = previous_cursor
                        break

                    if (blob_time <= threshold_time) or (
                        large_blob_threshold
                        and large_blob_lifetime
                        and digest.size_bytes > large_blob_threshold
                        and blob_time <= large_blob_lifetime
                    ):
                        n_bytes -= digest.size_bytes
                        digests_to_delete.append(digest)
                    else:
                        new_blob_bytes += digest.size_bytes

            if digests_to_delete:
                if dry_run:
                    LOGGER.debug("Detected deletable digests.", tags=dict(digest_count=len(digests_to_delete)))
                    for digest in digests_to_delete:
                        if digest not in failed_deletes:
                            bytes_deleted += digest.size_bytes
                else:
                    LOGGER.debug("Deleting digests.", tags=dict(digest_count=len(digests_to_delete)))
                    failed_deletes = self.bulk_delete(digests_to_delete)
                    blobs_deleted = 0
                    for digest in digests_to_delete:
                        if digest not in failed_deletes:
                            blobs_deleted += 1
                            bytes_deleted += digest.size_bytes

                    batch_duration = time.time() - delete_start_time
                    blobs_deleted_per_second = blobs_deleted / batch_duration
                    publish_gauge_metric(METRIC.CLEANUP.BLOBS_DELETED_PER_SECOND, blobs_deleted_per_second)
            elif new_blob_bytes > 0:
                LOGGER.error(
                    "All remaining digests have been accessed within the time threshold",
                    tags=dict(new_blob_bytes=new_blob_bytes, threshold_time=protect_blobs_after),
                )

            if self._delete_n_bytes_cursor == 0:  # scan finished
                LOGGER.debug("Cursor exhausted.")
                break

        return bytes_deleted
