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


from abc import ABC, abstractmethod

from redis import Redis
from sqlalchemy import select

from buildgrid.server.cleanup.janitor.config import RedisConfig
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.redis.provider import RedisProvider
from buildgrid.server.sql.models import IndexEntry
from buildgrid.server.sql.provider import SqlProvider

LOGGER = buildgrid_logger(__name__)


class IndexLookup(ABC):

    @abstractmethod
    def get_missing_digests(self, digests: set[str]) -> set[str]:
        """Return the subset of ``digests`` which is not in the index."""


class RedisIndexLookup(IndexLookup):

    def __init__(self, config: RedisConfig):
        LOGGER.info("Creating a Redis CAS Janitor.")

        self._batch_size = config.key_batch_size
        self._index_prefix = config.index_prefix
        self._redis = RedisProvider(
            host=config.host,
            port=config.port,
            password=config.password,
            db=config.db,
            dns_srv_record=config.dns_srv_record,
            sentinel_master_name=config.sentinel_master_name,
        )

    def get_missing_digests(self, digests: set[str]) -> set[str]:
        def _get_missing_digests(redis: "Redis[bytes]") -> set[str]:
            # NOTE: Use a sorted list of digests here since we need to pipeline them in
            # the same order as we zip them with the pipeline results.
            sorted_digests = sorted(digests)
            found_digests: set[str] = set()
            offset = 0
            while offset < len(sorted_digests):
                batch = sorted_digests[offset : offset + self._batch_size]
                pipe = redis.pipeline()
                for digest in batch:
                    pipe.exists(f"{self._index_prefix}{digest}")
                results = pipe.execute()
                found_digests |= {digest for result, digest in zip(results, batch) if result > 0}
                offset += self._batch_size

            return digests - found_digests

        return self._redis.execute_ro(_get_missing_digests)


class SqlIndexLookup(IndexLookup):

    def __init__(self, connection_string: str):
        LOGGER.info("Creating an SQL CAS Janitor.")
        self._sql = SqlProvider(connection_string=connection_string)

    def get_missing_digests(self, digests: set[str]) -> set[str]:
        hashes = set(digest.split("_", 1)[0] for digest in digests)
        with self._sql.scoped_session() as session:
            stmt = select(IndexEntry.digest_hash, IndexEntry.digest_size_bytes).filter(
                IndexEntry.digest_hash.in_(hashes)
            )
            found_digests = {f"{row[0]}_{row[1]}" for row in session.execute(stmt)}
            return digests - found_digests
