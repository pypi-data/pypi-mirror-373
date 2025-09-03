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


from contextlib import contextmanager
from typing import Iterator

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    ActionResult,
    Digest,
    GetActionResultRequest,
    UpdateActionResultRequest,
)
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2_grpc import ActionCacheStub
from buildgrid.server.client.retrier import GrpcRetrier
from buildgrid.server.exceptions import NotFoundError
from buildgrid.server.metadata import metadata_list


class ActionCacheClient:
    """Remote ActionCache service client helper.

    The :class:`ActionCacheClient` class comes with a generator factory function
    that can be used together with the `with` statement for context management::

        from buildgrid.server.client.actioncache import query

        with query(channel, instance='build') as action_cache:
            digest, action_result = action_cache.get(action_digest)
    """

    def __init__(
        self,
        channel: grpc.Channel,
        retries: int = 0,
        max_backoff: int = 64,
        should_backoff: bool = True,
    ) -> None:
        """Initializes a new :class:`ActionCacheClient` instance.

        Args:
            channel (grpc.Channel): a gRPC channel to the ActionCache endpoint.
        """
        self._grpc_retrier = GrpcRetrier(retries=retries, max_backoff=max_backoff, should_backoff=should_backoff)
        self.channel = channel
        self._stub = ActionCacheStub(self.channel)

    def get(self, instance_name: str | None, action_digest: Digest) -> ActionResult | None:
        """Attempt to retrieve cached :obj:`ActionResult` for : given obj:`Action`."""
        try:
            return self._grpc_retrier.retry(self._get, instance_name, action_digest)
        except NotFoundError:
            return None

    def update(
        self, instance_name: str | None, action_digest: Digest, action_result: ActionResult
    ) -> ActionResult | None:
        """Attempt to map in cache an :obj:`Action` to an :obj:`ActionResult`."""
        try:
            return self._grpc_retrier.retry(self._update, instance_name, action_digest, action_result)
        except NotFoundError:
            return None

    def _get(self, instance_name: str | None, action_digest: Digest) -> ActionResult:
        """Retrieves the cached :obj:`ActionResult` for a given :obj:`Action`.

        Args:
            instance_name (str): the instance name of the action cache.
            action_digest (:obj:`Digest`): the action's digest to query.

        Returns:
            :obj:`ActionResult`: the cached result or None if not found.

        Raises:
            grpc.RpcError: on any network or remote service error.
        """

        request = GetActionResultRequest()
        request.instance_name = instance_name or ""
        request.action_digest.CopyFrom(action_digest)

        res = self._stub.GetActionResult(request, metadata=metadata_list())
        return res

    def _update(self, instance_name: str | None, action_digest: Digest, action_result: ActionResult) -> ActionResult:
        """Maps in cache an :obj:`Action` to an :obj:`ActionResult`.

        Args:
            instance_name (str): the instance name of the action cache.
            action_digest (:obj:`Digest`): the action's digest to update.
            action_result (:obj:`ActionResult`): the action's result.

        Returns:
            :obj:`ActionResult`: the cached result or None on failure.

        Raises:
            grpc.RpcError: on any network or remote service error.
        """

        request = UpdateActionResultRequest()
        request.instance_name = instance_name or ""
        request.action_digest.CopyFrom(action_digest)
        request.action_result.CopyFrom(action_result)

        res = self._stub.UpdateActionResult(request, metadata=metadata_list())
        return res

    def close(self) -> None:
        """Closes the underlying connection stubs."""
        self.channel.close()


@contextmanager
def query(
    channel: grpc.Channel,
    retries: int = 0,
    max_backoff: int = 64,
    should_backoff: bool = True,
) -> Iterator[ActionCacheClient]:
    """Context manager generator for the :class:`ActionCacheClient` class."""
    client = ActionCacheClient(channel, retries=retries, max_backoff=max_backoff, should_backoff=should_backoff)
    try:
        yield client
    finally:
        client.close()
