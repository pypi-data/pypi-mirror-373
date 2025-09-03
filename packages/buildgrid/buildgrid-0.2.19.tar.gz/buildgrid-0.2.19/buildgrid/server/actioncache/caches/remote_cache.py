# Copyright (C) 2019, 2020 Bloomberg LP
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
Remote Action Cache
===================

Provides an interface to a remote Action Cache. This can be used by other
services (e.g. an Execution service) to communicate with a remote cache.

It provides the same API as any other Action Cache instance backend.

"""

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ActionResult, Digest
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.client.actioncache import ActionCacheClient
from buildgrid.server.client.authentication import ClientCredentials
from buildgrid.server.client.capabilities import CapabilitiesInterface
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.context import current_instance
from buildgrid.server.exceptions import GrpcUninitializedError, NotFoundError


class RemoteActionCache(ActionCacheABC):
    def __init__(
        self,
        remote: str,
        instance_name: str | None = None,
        retries: int = 0,
        max_backoff: int = 64,
        request_timeout: float | None = None,
        channel_options: tuple[tuple[str, str], ...] | None = None,
        credentials: ClientCredentials | None = None,
    ) -> None:
        """Initialises a new RemoteActionCache instance.

        Args:
            remote (str): URL of the remote ActionCache service to open a
                channel to.
            instance_name (str | None): The instance name of the remote ActionCache
                service. If none, uses the current instance context.
            channel_options (tuple): Optional tuple of channel options to set
                when opening the gRPC channel to the remote.
            credentials (dict): Optional credentials to use when opening
                the gRPC channel. If unset then an insecure channel will be
                used.

        """
        super().__init__()
        self._remote_instance_name = instance_name
        self._remote = remote
        self._channel_options = channel_options
        if credentials is None:
            credentials = {}
        self._credentials = credentials
        self._channel: grpc.Channel | None = None
        self._allow_updates = None  # type: ignore  # TODO STOP THIS
        self._retries = retries
        self._max_backoff = max_backoff
        self._action_cache: ActionCacheClient | None = None

    def start(self) -> None:
        if self._channel is None:
            self._channel, _ = setup_channel(
                self._remote,
                auth_token=self._credentials.get("auth-token"),
                auth_token_refresh_seconds=self._credentials.get("token-refresh-seconds"),
                client_key=self._credentials.get("tls-client-key"),
                client_cert=self._credentials.get("tls-client-cert"),
                server_cert=self._credentials.get("tls-server-cert"),
            )
        if self._action_cache is None:
            self._action_cache = ActionCacheClient(self._channel, self._retries, self._max_backoff)

    def stop(self) -> None:
        if self._channel:
            self._channel.close()

    @property
    def remote_instance_name(self) -> str:
        if self._remote_instance_name is not None:
            return self._remote_instance_name
        return current_instance()

    @property
    def allow_updates(self) -> bool:
        if self._channel is None:
            raise GrpcUninitializedError("Remote cache used before gRPC initialization.")

        # Check if updates are allowed if we haven't already.
        # This is done the first time update_action_result is called rather
        # than on instantiation because the remote cache may not be running
        # when this object is instantiated.
        if self._allow_updates is None:
            interface = CapabilitiesInterface(self._channel)
            capabilities = interface.get_capabilities(self.remote_instance_name)
            self._allow_updates = capabilities.cache_capabilities.action_cache_update_capabilities.update_enabled
        return self._allow_updates

    def get_action_result(self, action_digest: Digest) -> ActionResult:
        """Retrieves the cached result for an Action.

        Queries the remote ActionCache service to retrieve the cached
        result for a given Action digest. If the remote cache doesn't
        contain a result for the Action, then ``NotFoundError`` is raised.

        Args:
            action_digest (Digest): The digest of the Action to retrieve the
                cached result of.

        """
        if self._action_cache is None:
            raise GrpcUninitializedError("Remote cache used before gRPC initialization.")

        action_result = self._action_cache.get(self.remote_instance_name, action_digest)

        if action_result is None:
            key = self._get_key(action_digest)
            raise NotFoundError(f"Key not found: {key}")
        return action_result

    def update_action_result(self, action_digest: Digest, action_result: ActionResult) -> None:
        """Stores a result for an Action in the remote cache.

        Sends an ``UpdateActionResult`` request to the remote ActionCache
        service, to store the result in the remote cache.

        If the remote cache doesn't allow updates, then this raises a
        ``NotImplementedError``.

        Args:
            action_digest (Digest): The digest of the Action whose result is
                being cached.
            action_result (ActionResult): The result to cache for the given
                Action digest.

        """
        if self._action_cache is None:
            raise GrpcUninitializedError("Remote cache used before gRPC initialization.")

        if not self.allow_updates:
            raise NotImplementedError("Updating cache not allowed")

        self._action_cache.update(self.remote_instance_name, action_digest, action_result)

    def _get_key(self, action_digest: Digest) -> tuple[str, int]:
        """Get a hashable cache key from a given Action digest.

        Args:
            action_digest (Digest): The digest to produce a cache key for.

        """
        return (action_digest.hash, action_digest.size_bytes)
