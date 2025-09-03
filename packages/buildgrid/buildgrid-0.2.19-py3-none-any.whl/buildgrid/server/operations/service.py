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
OperationsService
=================

"""

from typing import cast

import grpc
from google.protobuf.empty_pb2 import Empty

from buildgrid._protos.google.longrunning.operations_pb2 import DESCRIPTOR as OPS_DESCRIPTOR
from buildgrid._protos.google.longrunning.operations_pb2 import (
    CancelOperationRequest,
    DeleteOperationRequest,
    GetOperationRequest,
    ListOperationsRequest,
    ListOperationsResponse,
    Operation,
)
from buildgrid._protos.google.longrunning.operations_pb2_grpc import (
    OperationsServicer,
    add_OperationsServicer_to_server,
)
from buildgrid.server.decorators import rpc
from buildgrid.server.operations.instance import OperationsInstance
from buildgrid.server.servicer import InstancedServicer
from buildgrid.server.settings import CLIENT_IDENTITY_HEADER_NAME, REQUEST_METADATA_HEADER_NAME


def _parse_instance_name(operation_name: str) -> str:
    names = operation_name.split("/")
    return "/".join(names[:-1]) if len(names) > 1 else ""


def _parse_operation_name(name: str) -> str:
    names = name.split("/")
    return names[-1] if len(names) > 1 else name


class OperationsService(OperationsServicer, InstancedServicer[OperationsInstance]):
    SERVICE_NAME = "Operations"
    REGISTER_METHOD = add_OperationsServicer_to_server
    FULL_NAME = OPS_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc(instance_getter=lambda r: _parse_instance_name(r.name))
    def GetOperation(self, request: GetOperationRequest, context: grpc.ServicerContext) -> Operation:
        operation_name = _parse_operation_name(request.name)
        operation, metadata, client_identity = self.current_instance.get_operation(operation_name)
        operation.name = request.name

        trailing_metadata = []
        if metadata is not None:
            trailing_metadata.append((REQUEST_METADATA_HEADER_NAME, metadata.SerializeToString()))
        if client_identity is not None:
            trailing_metadata.append((CLIENT_IDENTITY_HEADER_NAME, client_identity.SerializeToString()))

        if trailing_metadata:
            context.set_trailing_metadata(trailing_metadata)  # type: ignore[arg-type]  # tricky covariance issue

        return operation

    @rpc(instance_getter=lambda r: cast(str, r.name))
    def ListOperations(self, request: ListOperationsRequest, context: grpc.ServicerContext) -> ListOperationsResponse:
        # The request name should be the collection name. In our case, this is just the instance name
        result = self.current_instance.list_operations(request.filter, request.page_size, request.page_token)

        for operation in result.operations:
            operation.name = f"{request.name}/{operation.name}"

        return result

    @rpc(instance_getter=lambda r: _parse_instance_name(r.name))
    def DeleteOperation(self, request: DeleteOperationRequest, context: grpc.ServicerContext) -> Empty:
        context.set_details("BuildGrid does not support DeleteOperation.")
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        return Empty()

    @rpc(instance_getter=lambda r: _parse_instance_name(r.name))
    def CancelOperation(self, request: CancelOperationRequest, context: grpc.ServicerContext) -> Empty:
        self.current_instance.cancel_operation(_parse_operation_name(request.name))
        return Empty()
