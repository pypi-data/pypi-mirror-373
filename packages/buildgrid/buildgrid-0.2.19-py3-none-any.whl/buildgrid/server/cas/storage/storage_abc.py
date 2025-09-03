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
StorageABC
==================

The abstract base class for storage providers.
"""

import abc
import io
from tempfile import TemporaryFile
from typing import IO, Any, Iterator, TypeVar

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest, Directory
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.exceptions import NotFoundError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import timer
from buildgrid.server.settings import HASH, MAX_IN_MEMORY_BLOB_SIZE_BYTES
from buildgrid.server.types import MessageType

LOGGER = buildgrid_logger(__name__)

M = TypeVar("M", bound=MessageType)


def create_write_session(digest: Digest) -> IO[bytes]:
    """
    Return a file-like object to which a blob's contents could be written.

    For large files, to avoid excess memory usage, upload to temporary file.
    For small files we can work in memory for performance.
    """

    if digest.size_bytes > MAX_IN_MEMORY_BLOB_SIZE_BYTES:
        return TemporaryFile()
    return io.BytesIO()


T = TypeVar("T", bound="StorageABC")


class StorageABC(abc.ABC):
    TYPE: str

    def __enter__(self: T) -> T:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        pass

    def stop(self) -> None:
        LOGGER.info(f"Stopped {type(self).__name__}")

    @abc.abstractmethod
    def has_blob(self, digest: Digest) -> bool:
        """Return True if the blob with the given instance/digest exists."""

    @abc.abstractmethod
    def get_blob(self, digest: Digest) -> IO[bytes] | None:
        """Return a file-like object containing the blob. Most implementations
        will read the entire file into memory and return a `BytesIO` object.
        Eventually this should be corrected to handle files which cannot fit
        into memory.

        The file-like object must be readable and seekable.

        If the blob isn't present in storage, return None.
        """

    def stream_read_blob(self, digest: Digest, chunk_size: int, offset: int = 0, limit: int = 0) -> Iterator[bytes]:
        """Return a generator that yields the blob in chunks.

        If the blob isn't present in storage, it throws NotFound.
        """
        blob = self.get_blob(digest)
        if blob is None:
            raise NotFoundError(f"Blob not found: {digest.hash}/{digest.size_bytes}")

        if limit > 0:
            limit = min(limit, digest.size_bytes - offset)
        else:
            limit = digest.size_bytes - offset
        blob.seek(offset)
        for start in range(0, limit, chunk_size):
            end = min(start + chunk_size, digest.size_bytes)
            yield blob.read(end - start)

    def stream_write_blob(self, digest: Digest, chunks: Iterator[bytes]) -> None:
        """Given a stream of chunks, write it to the storage."""

        with create_write_session(digest) as session:
            for chunk in chunks:
                session.write(chunk)
            self.commit_write(digest, session)

    @abc.abstractmethod
    def delete_blob(self, digest: Digest) -> None:
        """Delete the blob from storage if it's present."""

    @abc.abstractmethod
    def commit_write(self, digest: Digest, write_session: IO[bytes]) -> None:
        """Store the contents for a digest.

        The storage object is not responsible for verifying that the data
        written to the write_session actually matches the digest. The caller
        must do that.
        """

    @abc.abstractmethod
    def bulk_delete(self, digests: list[Digest]) -> list[str]:
        """Delete a list of blobs from storage."""

    @abc.abstractmethod
    def missing_blobs(self, digests: list[Digest]) -> list[Digest]:
        """Return a container containing the blobs not present in CAS."""

    @abc.abstractmethod
    def bulk_update_blobs(self, blobs: list[tuple[Digest, bytes]]) -> list[Status]:
        """Given a container of (digest, value) tuples, add all the blobs
        to CAS. Return a list of Status objects corresponding to the
        result of uploading each of the blobs.

        Unlike in `commit_write`, the storage object will verify that each of
        the digests matches the provided data.
        """

    @abc.abstractmethod
    def bulk_read_blobs(self, digests: list[Digest]) -> dict[str, bytes]:
        """Given an iterable container of digests, return a
        {hash: file-like object} dictionary corresponding to the blobs
        represented by the input digests.

        Each file-like object must be readable and seekable.
        """

    def put_message(self, message: MessageType) -> Digest:
        """Store the given Protobuf message in CAS, returning its digest."""
        message_blob = message.SerializeToString()
        digest = Digest(hash=HASH(message_blob).hexdigest(), size_bytes=len(message_blob))
        with create_write_session(digest) as session:
            session.write(message_blob)
            self.commit_write(digest, session)
        return digest

    def get_message(self, digest: Digest, message_type: type[M]) -> M | None:
        """Retrieve the Protobuf message with the given digest and type from
        CAS. If the blob is not present, returns None.
        """
        message_blob = self.get_blob(digest)
        if message_blob is None:
            return None
        try:
            return message_type.FromString(message_blob.read())
        finally:
            message_blob.close()

    def get_tree(self, root_digest: Digest, raise_on_missing_subdir: bool = False) -> Iterator[Directory]:
        # From the spec, a NotFound response only occurs if the root directory is missing.
        with timer(METRIC.STORAGE.GET_TREE_DURATION, type=self.TYPE):
            root_directory = self.get_message(root_digest, Directory)
            if root_directory is None:
                raise NotFoundError(f"Root digest not found: {root_digest.hash}/{root_digest.size_bytes}")
            yield root_directory

            queue = [subdir.digest for subdir in root_directory.directories]
            while queue:
                blobs = self.bulk_read_blobs(queue)

                # GetTree allows for missing subtrees, but knowing some digests
                # are missing without scanning the result on the caller side
                # makes certain usages more efficient
                if raise_on_missing_subdir and len(blobs) < len(queue):
                    raise NotFoundError(
                        f"Missing entries under root directory: {root_digest.hash}/{root_digest.size_bytes}"
                    )

                directories = [Directory.FromString(b) for b in blobs.values()]
                queue = [subdir.digest for d in directories for subdir in d.directories]

                if len(directories) > 0:
                    yield from directories
