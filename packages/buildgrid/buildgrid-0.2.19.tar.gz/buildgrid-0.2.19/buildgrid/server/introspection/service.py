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

"""
IntrospectionService
====================

Definition of a IntrospectionService used for introspection and querying
of BuildGrid's internal state.

"""


from typing import cast

import grpc

from buildgrid._protos.build.buildgrid.introspection_pb2 import (
    DESCRIPTOR,
    GetOperationFiltersRequest,
    ListWorkersRequest,
    ListWorkersResponse,
    OperationFilters,
    OperationStats,
    OperationStatsRequest,
)
from buildgrid._protos.build.buildgrid.introspection_pb2_grpc import (
    IntrospectionServicer,
    add_IntrospectionServicer_to_server,
)
from buildgrid.server.decorators import rpc
from buildgrid.server.introspection.instance import IntrospectionInstance
from buildgrid.server.servicer import InstancedServicer


class IntrospectionService(IntrospectionServicer, InstancedServicer[IntrospectionInstance]):
    SERVICE_NAME = "Introspection"
    REGISTER_METHOD = add_IntrospectionServicer_to_server
    FULL_NAME = DESCRIPTOR.services_by_name["Introspection"].full_name

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def ListWorkers(self, request: ListWorkersRequest, context: grpc.ServicerContext) -> ListWorkersResponse:
        return self.current_instance.list_workers(request)

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def GetOperationFilters(
        self, request: GetOperationFiltersRequest, context: grpc.ServicerContext
    ) -> OperationFilters:
        return self.current_instance.get_operation_filters()

    @rpc(instance_getter=lambda r: cast(str, r.instance_name))
    def GetOperationStats(self, request: OperationStatsRequest, context: grpc.ServicerContext) -> OperationStats:
        return self.current_instance.get_operation_stats(request)
