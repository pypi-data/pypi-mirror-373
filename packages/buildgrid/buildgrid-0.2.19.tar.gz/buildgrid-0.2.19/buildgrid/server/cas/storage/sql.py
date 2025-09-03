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
SQL Storage
==================

A CAS storage which stores blobs in a SQL database

"""

import itertools
from io import BytesIO
from typing import IO, Iterator, Sequence, TypedDict, cast

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import StaleDataError

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.decorators import timed
from buildgrid.server.exceptions import StorageFullError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.sql.models import BlobEntry
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.server.utils.digests import validate_digest_data

LOGGER = buildgrid_logger(__name__)


class DigestRow(TypedDict):
    digest_hash: str
    digest_size_bytes: int
    data: bytes


class SQLStorage(StorageABC):
    TYPE = "SQL"

    def __init__(self, sql_provider: SqlProvider, *, sql_ro_provider: SqlProvider | None = None) -> None:
        self._sql = sql_provider
        self._sql_ro = sql_ro_provider or sql_provider
        self._inclause_limit = self._sql.default_inlimit

        supported_dialects = ["postgresql", "sqlite"]

        if self._sql.dialect not in supported_dialects:
            raise RuntimeError(
                f"Unsupported dialect {self._sql.dialect}."
                f"SQLStorage only supports the following dialects: {supported_dialects}"
            )

        # Make a test query against the database to ensure the connection is valid
        with self._sql.session() as session:
            session.query(BlobEntry).first()

    def _sqlite_bulk_insert(self, new_rows: list[DigestRow]) -> None:
        with self._sql.session() as session:
            session.execute(sqlite_insert(BlobEntry).values(new_rows).on_conflict_do_nothing())

    def _postgresql_bulk_insert(self, new_rows: list[DigestRow]) -> None:
        with self._sql.session() as session:
            session.execute(postgresql_insert(BlobEntry).values(new_rows).on_conflict_do_nothing())

    def _bulk_insert(self, digests: list[tuple[Digest, bytes]]) -> None:
        # Sort digests by hash to ensure consistent order to minimize deadlocks
        # when BatchUpdateBlobs requests have overlapping blobs
        new_rows: list[DigestRow] = [
            {"digest_hash": digest.hash, "digest_size_bytes": digest.size_bytes, "data": blob}
            for (digest, blob) in sorted(digests, key=lambda x: x[0].hash)
        ]

        if self._sql.dialect == "sqlite":
            self._sqlite_bulk_insert(new_rows)
        elif self._sql.dialect == "postgresql":
            self._postgresql_bulk_insert(new_rows)
        else:
            raise RuntimeError(f"Unsupported dialect {self._sql.dialect} for bulk_insert")

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        statement = select(func.count(BlobEntry.digest_hash)).where(BlobEntry.digest_hash == digest.hash)
        with self._sql_ro.session() as session:
            return session.execute(statement).scalar() == 1

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        statement = select(BlobEntry.data).where(BlobEntry.digest_hash == digest.hash)
        with self._sql_ro.session() as session:
            result = session.execute(statement).scalar()
        if result is not None:
            return BytesIO(result)
        return None

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        statement = delete(BlobEntry).where(BlobEntry.digest_hash == digest.hash)
        with self._sql.session() as session:
            # Set synchronize_session to false as we don't have any local session objects
            # to keep in sync
            session.execute(statement, execution_options={"synchronize_session": False})

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        write_session.seek(0)
        blob = write_session.read()
        try:
            self._bulk_insert([(digest, blob)])
        except DBAPIError as error:
            # Error has pgcode attribute (Postgres only)
            if hasattr(error.orig, "pgcode"):
                # imported here to avoid global dependency on psycopg2
                from psycopg2.errors import DiskFull, Error, OutOfMemory

                # 53100 == DiskFull && 53200 == OutOfMemory
                original_exception = cast(Error, error.orig)
                if isinstance(original_exception, (DiskFull, OutOfMemory)):
                    raise StorageFullError(
                        f"Postgres Error: {original_exception.pgerror} ({original_exception.pgcode}"
                    ) from error
            raise

    def _partitioned_hashes(self, digests: Sequence[Digest]) -> Iterator[Iterator[str]]:
        """Given a long list of digests, split it into parts no larger than
        _inclause_limit and yield the hashes in each part.
        """
        for part_start in range(0, len(digests), self._inclause_limit):
            part_end = min(len(digests), part_start + self._inclause_limit)
            part_digests = itertools.islice(digests, part_start, part_end)
            yield (digest.hash for digest in part_digests)

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        found_hashes = set()
        with self._sql_ro.session() as session:
            for part in self._partitioned_hashes(digests):
                stmt = select(BlobEntry.digest_hash).where(BlobEntry.digest_hash.in_(part))
                for row in session.execute(stmt):
                    found_hashes.add(row.digest_hash)

        return [digest for digest in digests if digest.hash not in found_hashes]

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(  # pylint: disable=arguments-renamed
        self, digest_blob_pairs: list[tuple[Digest, bytes]]
    ) -> list[Status]:
        """Implement the StorageABC's bulk_update_blobs method.

        The StorageABC interface takes in a list of digest/blob pairs and
        returns a list of results. The list of results MUST be ordered to
        correspond with the order of the input list."""
        results = []

        pairs_to_insert = []
        for digest, blob in digest_blob_pairs:
            if validate_digest_data(digest, blob):
                results.append(Status(code=code_pb2.OK))
                pairs_to_insert.append((digest, blob))
            else:
                results.append(Status(code=code_pb2.INVALID_ARGUMENT, message="Data doesn't match hash"))

        self._bulk_insert(pairs_to_insert)
        return results

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        # Fetch all of the digests in the database
        results: dict[str, bytes] = {}
        with self._sql_ro.session() as session:
            results = {
                digest_hash: data
                for part in self._partitioned_hashes(digests)
                for digest_hash, data in session.execute(
                    select(BlobEntry.digest_hash, BlobEntry.data).where(BlobEntry.digest_hash.in_(part))
                )
            }
        return results

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        hashes = [x.hash for x in digests]

        # Make sure we don't exceed maximum size of an IN clause
        n = self._inclause_limit
        hash_chunks = [hashes[i : i + n] for i in range(0, len(hashes), n)]

        # We will not raise, rollback, or log on StaleDataErrors.
        # These errors occur when we delete fewer rows than we were expecting.
        # This is fine, since the missing rows will get deleted eventually.
        # When running bulk_deletes concurrently, StaleDataErrors
        # occur too often to log.
        num_blobs_deleted = 0
        with self._sql.session(exceptions_to_not_rollback_on=[StaleDataError]) as session:
            for chunk in hash_chunks:
                # Do not wait for locks when deleting rows. Skip locked rows to
                # avoid deadlocks.
                stmt = delete(BlobEntry).where(
                    BlobEntry.digest_hash.in_(
                        select(BlobEntry.digest_hash)
                        .where(BlobEntry.digest_hash.in_(chunk))
                        .with_for_update(skip_locked=True)
                    )
                )
                # Set synchronize_session to false as we don't have any local session objects
                # to keep in sync
                num_blobs_deleted += session.execute(stmt, execution_options={"synchronize_session": False}).rowcount
        LOGGER.info(
            "blobs deleted from storage.", tags=dict(deleted_count=num_blobs_deleted, digest_count=len(digests))
        )

        # bulk_delete is typically expected to return the digests that were not deleted,
        # but delete only returns the number of rows deleted and not what was/wasn't
        # deleted. Getting this info would require extra queries, so assume that
        # everything was either deleted or already deleted. Failures will continue to throw
        return []
