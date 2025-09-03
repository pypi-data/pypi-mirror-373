# Copyright (C) 2025 Bloomberg LP
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


from contextlib import ExitStack

import mmh3

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ActionResult, Digest
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)


class ShardedActionCache(ActionCacheABC):
    """

    This is a wrapper intended to be used to compose an Action Cache of
    multiple other Action Caches, e.g. for sharding a Redis Action Cache.

    Requests are forwarded on to a specific shard based on the shard name,
    instance name, and Action Digest.

    """

    def __init__(
        self,
        shards: dict[str, ActionCacheABC],
        allow_updates: bool = True,
        cache_failed_actions: bool = True,
        cache_key_salt: str | None = None,
    ) -> None:
        """Initialise a new sharded Action Cache.

        Args:
            shards (dict[str, ActionCacheABC]): Mapping of shard name to cache shard.

            allow_updates (bool): Allow updates to be pushed to the Action Cache.
                Individual shards may specify this separately, which will effectively
                override the value defined here for that shard. Defaults to ``True``.

            cache_failed_actions (bool): Whether to store failed (non-zero exit
                code) actions. Individual shards may specify this separately, which will
                effectively override the value defined here for that shard. Default to
                ``True``.

            cache_key_salt (str): If provided, included in the Redis key for cache entries. Use
                to isolate or share specific chunks of a shared Redis cache.

        """
        super().__init__(allow_updates=allow_updates)
        self._stack = ExitStack()
        self._cache_failed_actions = cache_failed_actions
        self._cache_key_salt = cache_key_salt
        self._shards = shards

    def start(self) -> None:
        for shard in self._shards.values():
            self._stack.enter_context(shard)

    def stop(self) -> None:
        self._stack.close()

    def _cache_from_digest(self, digest: Digest) -> ActionCacheABC:
        def _score(shard_name: str, digest: Digest) -> int:
            key = self._get_key(digest)
            hash = mmh3.hash(f"{shard_name}\t{key}", signed=False)
            return hash

        shard_name = min(self._shards.keys(), key=lambda name: _score(name, digest))
        return self._shards[shard_name]

    def get_action_result(self, action_digest: Digest) -> ActionResult:
        """Retrieves the cached result for an Action.

        Determines the expected shard, and attempts to retrieve the ActionResult from
        that shard. If the result is not found, a NotFoundError is raised.

        Args:
            action_digest (Digest): The digest of the Action to retrieve the
                cached result of.

        """
        return self._cache_from_digest(action_digest).get_action_result(action_digest)

    def update_action_result(self, action_digest: Digest, action_result: ActionResult) -> None:
        """Stores a result for an Action in the cache.

        Determines which shard a result should be stored in, and attempts to store
        it. If the result has a non-zero exit code and `cache_failed_actions` is False
        for either this shard or the whole cache, the result is not cached.

        Args:
            action_digest (Digest): The digest of the Action whose result is
                being cached.

            action_result (ActionResult): The result to cache for the given
                Action digest.

        """
        if not self._allow_updates:
            raise NotImplementedError("Updating cache not allowed")

        if self._cache_failed_actions or action_result.exit_code == 0:
            self._cache_from_digest(action_digest).update_action_result(action_digest, action_result)

    def _get_key(self, action_digest: Digest) -> str:
        if self._cache_key_salt is None:
            return action_digest.hash
        return f"{self._cache_key_salt}\t{action_digest.hash}"
