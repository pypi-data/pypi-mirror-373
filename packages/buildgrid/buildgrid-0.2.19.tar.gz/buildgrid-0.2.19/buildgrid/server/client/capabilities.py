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


import grpc

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2, remote_execution_pb2_grpc
from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)


class CapabilitiesInterface:
    """Interface for calls the the Capabilities Service."""

    def __init__(self, channel: grpc.Channel) -> None:
        """Initialises an instance of the capabilities service.

        Args:
            channel (grpc.Channel): A gRPC channel to the CAS endpoint.
        """
        self.__stub = remote_execution_pb2_grpc.CapabilitiesStub(channel)

    def get_capabilities(self, instance_name: str) -> remote_execution_pb2.ServerCapabilities:
        """Returns the capabilities or the server to the user.

        Args:
            instance_name (str): The name of the instance."""

        request = remote_execution_pb2.GetCapabilitiesRequest(instance_name=instance_name)
        try:
            return self.__stub.GetCapabilities(request)

        except grpc.RpcError as e:
            LOGGER.debug(e)
            raise ConnectionError(e.details())
