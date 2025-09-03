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
BotsService
=================

"""

from typing import cast

import grpc
from google.protobuf import empty_pb2

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ExecutedActionMetadata
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import DESCRIPTOR as BOTS_DESCRIPTOR
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import (
    BotSession,
    CreateBotSessionRequest,
    PostBotEventTempRequest,
    UpdateBotSessionRequest,
)
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2_grpc import (
    BotsServicer,
    add_BotsServicer_to_server,
)
from buildgrid.server.bots.instance import BotsInterface
from buildgrid.server.decorators import rpc
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.scheduler.impl import BotMetrics
from buildgrid.server.servicer import InstancedServicer
from buildgrid.server.utils.cancellation import CancellationContext


def _instance_name_from_bot_name(name: str) -> str:
    names = name.split("/")
    return "/".join(names[:-1])


class BotsService(BotsServicer, InstancedServicer[BotsInterface]):
    SERVICE_NAME = "Bots"
    REGISTER_METHOD = add_BotsServicer_to_server
    FULL_NAME = BOTS_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: cast(str, r.parent))
    def CreateBotSession(self, request: CreateBotSessionRequest, context: grpc.ServicerContext) -> BotSession:
        return self.current_instance.create_bot_session(
            request.bot_session, CancellationContext(context), deadline=context.time_remaining()
        )

    @rpc(instance_getter=lambda r: _instance_name_from_bot_name(r.name))
    def UpdateBotSession(self, request: UpdateBotSessionRequest, context: grpc.ServicerContext) -> BotSession:
        if request.name != request.bot_session.name:
            raise InvalidArgumentError(
                "Name in UpdateBotSessionRequest does not match BotSession. "
                f" UpdateBotSessionRequest.name=[{request.name}] BotSession.name=[{request.bot_session.name}]"
            )

        # Strip out the Partial Execution Metadata and format into a dict of [leaseID, partialExecutionMetadata]
        # The metadata header should be in the format "partial-execution-metadata-<lease_id>-bin"
        all_metadata_entries = context.invocation_metadata()
        lease_id_to_partial_execution_metadata: dict[str, ExecutedActionMetadata] = {}
        for entry in all_metadata_entries:
            if entry.key.startswith("partial-execution-metadata-"):  # type: ignore [attr-defined]
                execution_metadata = ExecutedActionMetadata()
                execution_metadata.ParseFromString(entry.value)  # type: ignore [attr-defined]
                lease_id = entry.key[len("partial-execution-metadata-") : -len("-bin")]  # type: ignore
                lease_id_to_partial_execution_metadata[lease_id] = execution_metadata

        bot_session, metadata = self.current_instance.update_bot_session(
            request.bot_session,
            CancellationContext(context),
            deadline=context.time_remaining(),
            partial_execution_metadata=lease_id_to_partial_execution_metadata,
        )

        context.set_trailing_metadata(metadata)  # type: ignore[arg-type]  # tricky covariance issue.

        return bot_session

    @rpc(instance_getter=lambda r: _instance_name_from_bot_name(r.name))
    def PostBotEventTemp(self, request: PostBotEventTempRequest, context: grpc.ServicerContext) -> empty_pb2.Empty:
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        return empty_pb2.Empty()

    def query_connected_bots_for_instance(self, instance_name: str) -> int:
        if instance := self.instances.get(instance_name):
            return instance.scheduler.bot_notifier.listener_count_for_instance(instance_name)
        return 0

    def get_bot_status_metrics(self, instance_name: str) -> BotMetrics:
        if instance := self.instances.get(instance_name):
            return instance.get_bot_status_metrics()
        return {}
