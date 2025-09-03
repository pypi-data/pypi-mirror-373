# Copyright (C) 2019 Bloomberg LP
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
IndexABC
==================

The abstract base class for storage indices. An index is a special type of
Storage that facilitates storing blob metadata. It must wrap another Storage.

Derived classes must implement all methods of both this interface and the
StorageABC interface.
"""

import abc
from datetime import datetime
from typing import Iterator

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest

from ..storage_abc import StorageABC


class IndexABC(StorageABC):
    @abc.abstractmethod
    def __init__(self, *, fallback_on_get: bool = False) -> None:
        # If fallback is enabled, the index is required to fetch blobs from
        # storage on each get_blob and bulk_read_blobs request and update
        # itself accordingly.
        self._fallback_on_get = fallback_on_get

    @abc.abstractmethod
    def least_recent_digests(self) -> Iterator[Digest]:
        """Generator to iterate through the digests in LRU order"""

    @abc.abstractmethod
    def get_total_size(self) -> int:
        """
        Return the sum of the size of all blobs within the index.
        """

    @abc.abstractmethod
    def get_blob_count(self) -> int:
        """
        Return the number of blobs within the index.
        """

    @abc.abstractmethod
    def delete_n_bytes(
        self,
        n_bytes: int,
        dry_run: bool = False,
        protect_blobs_after: datetime | None = None,
        large_blob_threshold: int | None = None,
        large_blob_lifetime: datetime | None = None,
    ) -> int:
        """Delete around n bytes of data from the index.

        The ordering in which digests are deleted is up to the specific implementations
        and may provide different semantics such as LRU or random deletion. ALL implementations
        must respect the protect_blobs_after parameter to limit the age of deleted blobs

        Implementations should generate delete around n_bytes on each call, but may delete more or less
        depending on the state of the storage, index, and value of protect_blobs_after.

        Args:
            n_bytes (int): The number of bytes to be deleted
            dry_run (bool): Don't actually delete any data, just return the number of bytes which would be deleted
            protect_blobs_after: Don't delete any digests which have been accessed after this time
            large_blob_threshold (int): Size in bytes for a blob to be considered 'large'
            large_blob_lifetime: Age after which 'large' blobs can be deleted.

        Returns:
            Number of bytes deleted
        """
