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
DiskStorage
==================

A CAS storage provider that stores files as blobs on disk.
"""

import errno
import io
import os
import tempfile
from typing import IO

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.decorators import timed
from buildgrid.server.exceptions import StorageFullError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.settings import HASH, MAX_IN_MEMORY_BLOB_SIZE_BYTES

from .storage_abc import StorageABC

LOGGER = buildgrid_logger(__name__)


class DiskStorage(StorageABC):
    TYPE = "Disk"

    def __init__(self, path: str) -> None:
        if not os.path.isabs(path):
            self.__root_path = os.path.abspath(path)
        else:
            self.__root_path = path
        self.__cas_path = os.path.join(self.__root_path, "cas")

        self.objects_path = os.path.join(self.__cas_path, "objects")
        self.temp_path = os.path.join(self.__root_path, "tmp")

        os.makedirs(self.objects_path, exist_ok=True)
        os.makedirs(self.temp_path, exist_ok=True)

    @timed(METRIC.STORAGE.STAT_DURATION, type=TYPE)
    def has_blob(self, digest: Digest) -> bool:
        LOGGER.debug("Checking for blob.", tags=dict(digest=digest))
        return os.path.exists(self._get_object_path(digest))

    @timed(METRIC.STORAGE.BULK_STAT_DURATION, type=TYPE)
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        return [digest for digest in digests if not os.path.exists(self._get_object_path(digest))]

    @timed(METRIC.STORAGE.READ_DURATION, type=TYPE)
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        LOGGER.debug("Getting blob.", tags=dict(digest=digest))
        try:
            f = open(self._get_object_path(digest), "rb")
            # TODO probably need to make StorageABC generic...?
            return io.BufferedReader(f)
        except FileNotFoundError:
            return None

    @timed(METRIC.STORAGE.BULK_READ_DURATION, type=TYPE)
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        result = {}
        for digest in digests:
            try:
                with open(self._get_object_path(digest), "rb") as f:
                    result[digest.hash] = f.read()
            except FileNotFoundError:
                # Ignore files not found, will be reported as NOT_FOUND higher up.
                pass
        return result

    @timed(METRIC.STORAGE.DELETE_DURATION, type=TYPE)
    def delete_blob(self, digest: Digest) -> None:
        LOGGER.debug("Deleting blob.", tags=dict(digest=digest))
        try:
            os.remove(self._get_object_path(digest))
        except OSError:
            pass

    @timed(METRIC.STORAGE.BULK_DELETE_DURATION, type=TYPE)
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        failed_deletions = []
        for digest in digests:
            try:
                os.remove(self._get_object_path(digest))
            except FileNotFoundError:
                # Ignore files not found. Already deleted.
                pass
            except OSError:
                # If deletion threw an exception, assume deletion failed. More specific implementations
                # with more information can return if a blob was missing instead
                LOGGER.warning("Unable to clean up digest.", tags=dict(digest=digest), exc_info=True)
                failed_deletions.append(digest.hash)

        return failed_deletions

    @timed(METRIC.STORAGE.WRITE_DURATION, type=TYPE)
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        LOGGER.debug("Writing blob.", tags=dict(digest=digest))
        object_path = self._get_object_path(digest)

        write_session.seek(0)
        try:
            with tempfile.NamedTemporaryFile("wb", dir=self.temp_path) as f:
                while data := write_session.read(MAX_IN_MEMORY_BLOB_SIZE_BYTES):
                    f.write(data)
                os.makedirs(os.path.dirname(object_path), exist_ok=True)
                os.link(f.name, object_path)
        except FileExistsError:
            # Object is already there!
            pass
        except OSError as e:
            # Not enough space error or file too large
            if e.errno in [errno.ENOSPC, errno.EFBIG]:
                raise StorageFullError(f"Disk Error: {e.errno}") from e
            raise e

    @timed(METRIC.STORAGE.BULK_WRITE_DURATION, type=TYPE)
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        result = []
        for digest, data in blobs:
            object_path = self._get_object_path(digest)
            if len(data) != digest.size_bytes or HASH(data).hexdigest() != digest.hash:
                result.append(Status(code=code_pb2.INVALID_ARGUMENT, message="Data doesn't match hash"))
                continue
            try:
                with tempfile.NamedTemporaryFile("wb", dir=self.temp_path) as f:
                    f.write(data)
                    os.makedirs(os.path.dirname(object_path), exist_ok=True)
                    os.link(f.name, object_path)
                result.append(Status(code=code_pb2.OK))
            except FileExistsError:
                # Object is already there!
                result.append(Status(code=code_pb2.OK))
            except OSError as e:
                code = code_pb2.INTERNAL
                if e.errno in [errno.ENOSPC, errno.EFBIG]:
                    code = code_pb2.RESOURCE_EXHAUSTED
                result.append(Status(code=code, message=f"Disk Error: {e}"))
        return result

    def _get_object_path(self, digest: Digest) -> str:
        return os.path.join(self.objects_path, digest.hash[:2], digest.hash[2:])
