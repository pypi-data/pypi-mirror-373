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

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ActionResult, Digest
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.exceptions import NotFoundError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric

LOGGER = buildgrid_logger(__name__)


class MirroredCache(ActionCacheABC):
    """Synchronize two mirrored action-caches to the same state"""

    def __init__(
        self,
        first: ActionCacheABC,
        second: ActionCacheABC,
    ):
        # Don't pass a storage object to super class
        # as blob existence check will be performed by each object.
        # On the other hand, the storages of these two caches should point to the same one
        # or also mirrored with each other.
        super().__init__(allow_updates=True, storage=None)
        self._first = first
        self._second = second

    def start(self) -> None:
        self._first.start()
        self._second.start()

    def stop(self) -> None:
        self._second.stop()
        self._first.stop()

    def update_action_result(self, action_digest: Digest, action_result: ActionResult) -> None:
        self._first.update_action_result(action_digest, action_result)
        self._second.update_action_result(action_digest, action_result)
        LOGGER.info("Finished dual write to both action-caches.", tags=dict(digest=action_digest))

    def get_action_result(self, action_digest: Digest) -> ActionResult:
        first_result = _try_get_action_result(self._first, action_digest)
        second_result = _try_get_action_result(self._second, action_digest)

        if first_result is None and second_result is None:
            raise NotFoundError(f"Action result not found: {action_digest.hash}/{action_digest.size_bytes}")

        if first_result is None:
            publish_counter_metric(METRIC.ACTION_CACHE.MIRRORED_MISMATCH_COUNT, 1)
            self._first.update_action_result(action_digest, second_result)  # type: ignore[arg-type]
            return second_result  # type: ignore[return-value]

        if second_result is None:
            publish_counter_metric(METRIC.ACTION_CACHE.MIRRORED_MISMATCH_COUNT, 1)
            self._second.update_action_result(action_digest, first_result)
            return first_result

        if first_result != second_result:
            publish_counter_metric(METRIC.ACTION_CACHE.MIRRORED_MISMATCH_COUNT, 1)
            LOGGER.warning(
                "Different action results in mirrored caches.",
                tags=dict(first_result=first_result, second_result=second_result),
            )
            return first_result

        publish_counter_metric(METRIC.ACTION_CACHE.MIRRORED_MATCH_COUNT, 1)
        return first_result


def _try_get_action_result(cache: ActionCacheABC, digest: Digest) -> ActionResult | None:
    try:
        return cache.get_action_result(digest)
    except NotFoundError:
        return None
