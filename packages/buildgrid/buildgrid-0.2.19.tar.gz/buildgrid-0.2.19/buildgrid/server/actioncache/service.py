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


from typing import cast

import grpc

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    ActionResult,
    GetActionResultRequest,
    UpdateActionResultRequest,
)
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2_grpc import (
    ActionCacheServicer,
    add_ActionCacheServicer_to_server,
)
from buildgrid.server.actioncache.instance import ActionCache
from buildgrid.server.decorators import rpc
from buildgrid.server.servicer import InstancedServicer


class ActionCacheService(ActionCacheServicer, InstancedServicer[ActionCache]):
    SERVICE_NAME = "ActionCache"
    REGISTER_METHOD = add_ActionCacheServicer_to_server
    FULL_NAME = RE_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def GetActionResult(self, request: GetActionResultRequest, context: grpc.ServicerContext) -> ActionResult:
        return self.current_instance.get_action_result(request.action_digest)

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def UpdateActionResult(self, request: UpdateActionResultRequest, context: grpc.ServicerContext) -> ActionResult:
        self.current_instance.update_action_result(request.action_digest, request.action_result)
        return request.action_result
