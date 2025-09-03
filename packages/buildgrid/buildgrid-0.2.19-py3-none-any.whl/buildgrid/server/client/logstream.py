# Copyright (C) 2020 Bloomberg LP
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
from grpc import RpcError

from buildgrid._protos.build.bazel.remote.logstream.v1.remote_logstream_pb2 import CreateLogStreamRequest, LogStream
from buildgrid._protos.build.bazel.remote.logstream.v1.remote_logstream_pb2_grpc import LogStreamServiceStub
from buildgrid.server.app.commands.cmd_logstream import instanced_resource_name
from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)


class LogStreamClient:
    def __init__(self, channel: grpc.Channel, instance_name: str = "") -> None:
        self._channel = channel
        self._instance_name = instance_name
        self._logstream_stub: LogStreamServiceStub | None = LogStreamServiceStub(self._channel)

    def create(self, parent: str) -> LogStream:
        assert self._logstream_stub, "LogStreamClient used after close"

        parent = instanced_resource_name(self._instance_name, parent)
        request = CreateLogStreamRequest(parent=parent)
        try:
            return self._logstream_stub.CreateLogStream(request)
        except RpcError as e:
            LOGGER.exception(f"Error creating a LogStream: {e.details()}")
            raise ConnectionError(e.details())

    def close(self) -> None:
        self._logstream_stub = None


@contextmanager
def logstream_client(channel: grpc.Channel, instance_name: str) -> Iterator[LogStreamClient]:
    client = LogStreamClient(channel, instance_name)
    try:
        yield client
    finally:
        client.close()
