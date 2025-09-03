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

import functools
import inspect
from typing import Any, Callable, Iterator, TypeVar, Union, cast

import grpc
from google.protobuf.message import Message

from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric

from .time import _service_metadata

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]
_Message = Union[Iterator[Message], Message]


def network_io(f: Func) -> Func:
    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: _Message, context: grpc.ServicerContext) -> Iterator[Any]:
        input_bytes = 0
        if isinstance(message, Iterator):

            def stream(messages: Iterator[Message]) -> Iterator[Message]:
                nonlocal input_bytes
                for input_message in messages:
                    input_bytes += input_message.ByteSize()
                    yield input_message

            message = stream(message)
        else:
            input_bytes = message.ByteSize()

        output_bytes = 0
        try:
            for output_message in f(self, message, context):
                output_bytes += output_message.ByteSize()
                yield output_message
        finally:
            metadata = _service_metadata(self, message, context)
            publish_counter_metric(METRIC.RPC.INPUT_BYTES, input_bytes, **metadata)
            publish_counter_metric(METRIC.RPC.OUTPUT_BYTES, output_bytes, **metadata)

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: _Message, context: grpc.ServicerContext) -> Any:
        input_bytes = 0
        if isinstance(message, Iterator):

            def stream(messages: Iterator[Message]) -> Iterator[Message]:
                nonlocal input_bytes
                for input_message in messages:
                    input_bytes += input_message.ByteSize()
                    yield input_message

            message = stream(message)
        else:
            input_bytes = message.ByteSize()

        output_bytes = 0
        try:
            output_message = f(self, message, context)
            output_bytes += output_message.ByteSize()
            return output_message
        finally:
            metadata = _service_metadata(self, message, context)
            publish_counter_metric(METRIC.RPC.INPUT_BYTES, input_bytes, **metadata)
            publish_counter_metric(METRIC.RPC.OUTPUT_BYTES, output_bytes, **metadata)

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)
