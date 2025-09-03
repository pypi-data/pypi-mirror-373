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

import random
from functools import lru_cache
from threading import Event
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm.exc import StaleDataError

from buildgrid.server.cleanup.janitor.config import SQLStorageConfig
from buildgrid.server.cleanup.janitor.index import IndexLookup
from buildgrid.server.exceptions import FailedPreconditionError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.settings import HASH
from buildgrid.server.sql.models import BlobEntry
from buildgrid.server.threading import ContextWorker

LOGGER = buildgrid_logger(__name__)


@lru_cache(maxsize=1)
def get_sha256_buckets() -> list[tuple[str, str]]:
    # This function creates bucket boundaries for 256 buckets based on sha256 hash values.
    # Each bucket represents a range of hash values. For example, the first bucket will include
    # all hashes starting with "00" and ending before "01". This is because in string comparison:
    # "00" < "0000..." < "00ffffff" < "01".
    # The last bucket will include hashes starting with "ff" and ending before "fg":
    # "ff" < "ff000000..." < "ffffff..." < "fg".

    if HASH().name != "sha256":
        LOGGER.error("SQL Janitor only supports sha256 hashing.")
        raise FailedPreconditionError("SQL Janitor only supports sha256 hashing.")

    # This creates the first 255 buckets. For example, the first bucket is ("00", "01"),
    # the second bucket is ("01", "02"), and so on up to ("fe", "ff").
    buckets = [(f"{i:02x}", f"{i + 1:02x}") for i in range(255)]

    # The last bucket is a special case because the last value is "ff" and the next value is "fg".
    buckets.append(("ff", "fg"))
    return buckets


class SQLJanitor:

    def __init__(self, sqlStorageConfig: SQLStorageConfig, index: IndexLookup):
        self._index = index
        self._sql = sqlStorageConfig.sql
        self._sql_ro = sqlStorageConfig.sql_ro
        self._sleep_interval = sqlStorageConfig.sleep_interval
        self._batch_size = sqlStorageConfig.batch_size
        self._batch_sleep_interval = sqlStorageConfig.batch_sleep_interval

        self._stop_requested = Event()
        self._worker = ContextWorker(target=self.run, name="Janitor", on_shutdown_requested=self._stop_requested.set)

    def delete_digests(self, digests: set[str]) -> int:
        # We will not raise, rollback, or log on StaleDataErrors.
        # These errors occur when we delete fewer rows than we were expecting.
        with self._sql.session(exceptions_to_not_rollback_on=[StaleDataError]) as session:
            stmt = delete(BlobEntry).where(
                BlobEntry.digest_hash.in_(
                    select(BlobEntry.digest_hash)
                    .where(BlobEntry.digest_hash.in_(digests))
                    .with_for_update(skip_locked=True)
                )
            )
            # Set synchronize_session to false as we don't have any local session objects
            # to keep in sync
            return session.execute(stmt, execution_options={"synchronize_session": False}).rowcount

    def cleanup_bucket(self, bucket: tuple[str, str]) -> None:
        current_end = bucket[0]
        num_deleted = 0
        while True:
            if self._stop_requested.is_set():
                break
            statement = (
                select(BlobEntry.digest_hash, BlobEntry.digest_size_bytes)
                .where(BlobEntry.digest_hash > current_end, BlobEntry.digest_hash < bucket[1])
                .order_by(BlobEntry.digest_hash)
                .limit(self._batch_size)
            )
            with self._sql_ro.session() as session:
                results = session.execute(statement).fetchall()

            if not results:
                break

            # get the digest of the last blob
            current_end = results[-1][0]

            # Create a map from digets to a string "digests/size"
            digest_map = {f"{digest}_{size}": digest for digest, size in results}
            missing_digests = self._index.get_missing_digests(set(digest_map.keys()))
            missing_hashes = set([digest_map[key] for key in missing_digests])
            num_deleted += self.delete_digests(missing_hashes)

            if self._batch_sleep_interval:
                self._stop_requested.wait(timeout=self._batch_sleep_interval)

            if len(results) < self._batch_size:
                break

        LOGGER.info(f"Deleted {num_deleted} blobs from sql storage between {bucket[0]}-{bucket[1]}")

    def __enter__(self) -> "SQLJanitor":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._worker.start()

    def stop(self, *args: Any, **kwargs: Any) -> None:
        self._worker.stop()

    def run(self, stop_requested: Event) -> None:
        random.seed()
        while not stop_requested.is_set():
            try:
                bucket_boundaries = get_sha256_buckets()

                # Shuffle the bucket names to reduce the likelihood of two janitors
                # concurrently cleaning the same bucket.
                random.shuffle(bucket_boundaries)

                for bucket in bucket_boundaries:
                    self.cleanup_bucket(bucket)
            except Exception:
                LOGGER.exception("Exception while cleaning up SQL storage with janitor")
                continue

            stop_requested.wait(timeout=self._sleep_interval)
