# Copyright (C) 2020 Bloomberg LP
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
from typing import Any, TypeVar

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Action, ActionResult, Digest, Tree
from buildgrid.server.cas.instance import EMPTY_BLOB_DIGEST
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.exceptions import NotFoundError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric
from buildgrid.server.utils.digests import HashableDigest

LOGGER = buildgrid_logger(__name__)


T = TypeVar("T", bound="ActionCacheABC")


class ActionCacheABC(ABC):
    def __init__(self, allow_updates: bool = False, storage: StorageABC | None = None):
        self._allow_updates = allow_updates
        self._storage = storage

    @property
    def allow_updates(self) -> bool:
        return self._allow_updates

    def __enter__(self: T) -> T:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        if self._storage is not None:
            self._storage.start()

    def stop(self) -> None:
        if self._storage is not None:
            self._storage.stop()
        LOGGER.info("Stopped ActionCache.")

    @abstractmethod
    def get_action_result(self, action_digest: Digest) -> ActionResult:
        raise NotImplementedError()

    @abstractmethod
    def update_action_result(self, action_digest: Digest, action_result: ActionResult) -> None:
        raise NotImplementedError()

    def referenced_blobs_still_exist(self, action_digest: Digest, action_result: ActionResult) -> bool:
        if self._referenced_blobs_still_exist(action_digest, action_result):
            return True

        publish_counter_metric(METRIC.ACTION_CACHE.INVALID_CACHE_COUNT, 1)
        return False

    def _referenced_blobs_still_exist(self, action_digest: Digest, action_result: ActionResult) -> bool:
        """Checks CAS for Action and ActionResult output blobs existence.

        Args:
            action_digest (Digest): Digest for the Action whose top level digests
            will be searched for.
            action_result (ActionResult): ActionResult to search referenced
            output blobs for.

        Returns:
            True if all referenced blobs are present in CAS, False otherwise.
        """
        if not self._storage:
            return True
        blobs_needed: set[HashableDigest] = set()

        for output_file in action_result.output_files:
            blobs_needed.add(HashableDigest(output_file.digest.hash, output_file.digest.size_bytes))

        for output_directory in action_result.output_directories:
            if output_directory.HasField("tree_digest"):
                blobs_needed.add(
                    HashableDigest(output_directory.tree_digest.hash, output_directory.tree_digest.size_bytes)
                )
                tree = self._storage.get_message(output_directory.tree_digest, Tree)
                if tree is None:
                    return False

                for file_node in tree.root.files:
                    blobs_needed.add(HashableDigest(file_node.digest.hash, file_node.digest.size_bytes))

                for child in tree.children:
                    for file_node in child.files:
                        blobs_needed.add(HashableDigest(file_node.digest.hash, file_node.digest.size_bytes))
            elif output_directory.HasField("root_directory_digest"):
                blobs_needed.add(
                    HashableDigest(
                        output_directory.root_directory_digest.hash, output_directory.root_directory_digest.size_bytes
                    )
                )
                try:
                    for directory in self._storage.get_tree(
                        output_directory.root_directory_digest, raise_on_missing_subdir=True
                    ):
                        blobs_needed.update(
                            [
                                HashableDigest(file_node.digest.hash, file_node.digest.size_bytes)
                                for file_node in directory.files
                            ]
                        )
                        blobs_needed.update(
                            [
                                HashableDigest(dir_node.digest.hash, dir_node.digest.size_bytes)
                                for dir_node in directory.directories
                            ]
                        )
                except NotFoundError:
                    return False

        if action_result.stdout_digest.hash and not action_result.stdout_raw:
            blobs_needed.add(HashableDigest(action_result.stdout_digest.hash, action_result.stdout_digest.size_bytes))

        if action_result.stderr_digest.hash and not action_result.stderr_raw:
            blobs_needed.add(HashableDigest(action_result.stderr_digest.hash, action_result.stderr_digest.size_bytes))

        # Additionally refresh the TTL of the ActionDigest and the top level digests
        # contained within. This will keep the Action around for use cases like bgd-browser
        # where you want to look at both the Action and it's ActionResult, but with minimal
        # overhead.
        action = self._storage.get_message(action_digest, Action)
        action_blobs: set[HashableDigest] = set()
        if action:
            action_blobs.add(HashableDigest(action_digest.hash, action_digest.size_bytes))
            action_blobs.add(HashableDigest(action.command_digest.hash, action.command_digest.size_bytes))
            action_blobs.add(HashableDigest(action.input_root_digest.hash, action.input_root_digest.size_bytes))

        blobs_to_check: set[HashableDigest] = blobs_needed | action_blobs
        # No need to check the underlying storage for the empty blob as it is a special case blob which always exists
        # It is possible that the empty blob is not actually present in the underlying storage
        blobs_to_check.discard(HashableDigest(EMPTY_BLOB_DIGEST.hash, EMPTY_BLOB_DIGEST.size_bytes))
        missing = self._storage.missing_blobs([blob.to_digest() for blob in blobs_to_check])
        required_missing = [blob for blob in missing if HashableDigest(blob.hash, blob.size_bytes) in blobs_needed]
        if len(required_missing) != 0:
            LOGGER.debug(
                "Missing blobs.", tags=dict(required_missing=len(required_missing), blobs_needed=len(blobs_needed))
            )
            return False
        return True
