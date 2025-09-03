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


from typing import Iterable, Iterator, cast

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ExecuteRequest, WaitExecutionRequest
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2_grpc import (
    ExecutionServicer,
    add_ExecutionServicer_to_server,
)
from buildgrid._protos.google.longrunning import operations_pb2
from buildgrid.server.context import current_instance
from buildgrid.server.decorators import rpc
from buildgrid.server.exceptions import CancelledError
from buildgrid.server.execution.instance import ExecutionInstance
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metadata import extract_client_identity, extract_request_metadata, extract_scheduling_metadata
from buildgrid.server.servicer import InstancedServicer
from buildgrid.server.utils.cancellation import CancellationContext

LOGGER = buildgrid_logger(__name__)


def _parse_instance_name(operation_name: str) -> str:
    names = operation_name.split("/")
    return "/".join(names[:-1])


class ExecutionService(ExecutionServicer, InstancedServicer[ExecutionInstance]):
    SERVICE_NAME = "Execution"
    REGISTER_METHOD = add_ExecutionServicer_to_server
    FULL_NAME = RE_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def Execute(self, request: ExecuteRequest, context: grpc.ServicerContext) -> Iterator[operations_pb2.Operation]:
        yield from self._handle_request(request, context)

    @rpc(instance_getter=lambda r: _parse_instance_name(r.name))
    def WaitExecution(
        self, request: WaitExecutionRequest, context: grpc.ServicerContext
    ) -> Iterator[operations_pb2.Operation]:
        yield from self._handle_request(request, context)

    def query_connected_clients_for_instance(self, instance_name: str) -> int:
        if instance := self.instances.get(instance_name):
            return instance.scheduler.ops_notifier.listener_count()
        return 0

    def _handle_request(
        self,
        request: ExecuteRequest | WaitExecutionRequest,
        context: grpc.ServicerContext,
    ) -> Iterable[operations_pb2.Operation]:
        peer_uid = context.peer()

        try:
            if isinstance(request, ExecuteRequest):
                request_metadata = extract_request_metadata(context.invocation_metadata())
                client_identity = extract_client_identity(current_instance(), context.invocation_metadata())
                scheduling_metadata = extract_scheduling_metadata(context.invocation_metadata())
                operation_name = self.current_instance.execute(
                    action_digest=request.action_digest,
                    skip_cache_lookup=request.skip_cache_lookup,
                    priority=request.execution_policy.priority,
                    request_metadata=request_metadata,
                    client_identity=client_identity,
                    scheduling_metadata=scheduling_metadata,
                )
            else:  # isinstance(request, WaitExecutionRequest)"
                names = request.name.split("/")
                operation_name = names[-1]

            operation_full_name = f"{current_instance()}/{operation_name}"

            for operation in self.current_instance.stream_operation_updates(
                operation_name, context=CancellationContext(context)
            ):
                operation.name = operation_full_name
                yield operation

            if not context.is_active():
                LOGGER.info(
                    "Peer was holding thread for operation updates but the rpc context is inactive; releasing thread.",
                    tags=dict(peer_uid=peer_uid, instance_name=current_instance(), operation_name=operation_name),
                )

        except CancelledError as e:
            LOGGER.info(e)
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.CANCELLED)
            yield e.last_response  # type: ignore[misc]  # need a better signature
