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
from typing import Any, Callable, Iterator, TypeVar, cast

import grpc

from buildgrid.server.context import current_instance, current_method, current_service, method_context, service_context
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metadata import extract_client_identity_dict, extract_request_metadata_dict
from buildgrid.server.metrics_names import METRIC

from .authorize import authorize
from .errors import handle_errors
from .instance import instanced
from .io import network_io
from .limiter import limiter
from .metadata import metadatacontext
from .requestid import track_request_id
from .time import timed

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]
LOGGER = buildgrid_logger(__name__)


def log_rpc(f: Func) -> Func:
    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
        tags = dict(
            service=current_service(),
            method=current_method(),
            peer=context.peer(),
            **extract_request_metadata_dict(context.invocation_metadata()),
            **extract_client_identity_dict(current_instance(), context.invocation_metadata()),
        )
        LOGGER.info("Received request.", tags=tags)
        yield from f(self, message, context)

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
        tags = dict(
            service=current_service(),
            method=current_method(),
            peer=context.peer(),
            **extract_request_metadata_dict(context.invocation_metadata()),
            **extract_client_identity_dict(current_instance(), context.invocation_metadata()),
        )
        LOGGER.info("Received request.", tags=tags)
        return f(self, message, context)

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)


def named_rpc(f: Func) -> Func:
    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
        with service_context(self.SERVICE_NAME), method_context(f.__name__):
            yield from f(self, message, context)

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
        with service_context(self.SERVICE_NAME), method_context(f.__name__):
            return f(self, message, context)

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)


def rpc(
    *,
    instance_getter: Callable[[Any], str] | None = None,
    request_formatter: Callable[[Any], Any] = lambda r: str(r),
) -> Callable[[Func], Func]:
    """
    The RPC decorator provides common functionality to all buildgrid servicer methods.
    This decorator should be attached to all endpoints in the application.

    All endpoints will produce the following metrics, with a tag "code" for grpc status values,
    a tag "service" for the service name of the RPC, and a tag "method" for the RPC method name.
    * ``rpc.duration.ms``: The time in milliseconds spent on the method.
    * ``rpc.input_bytes.count``: The number of message bytes sent from client to server.
    * ``rpc.output_bytes.count``: The number of message bytes sent from server to client.

    All other metrics produced during an RPC will have the tags "service" and "method" attached.

    Args:
        instance_getter (Callable[[Any], str]): Determines how to fetch the instance name
            from the request payload. If provided, the tag "instance" will also be applied for all
            metrics, and the RPC will be enrolled in authentication/authorization.

        request_formatter (Callable[[Any], str]): Determines how to format the request payloads in logs.
    """

    def decorator(func: Func) -> Func:
        # Note: decorators are applied in reverse order from a normal decorator pattern.
        #   All decorators that apply context vars are invoked earlier in the call chain
        #   such that the context vars remain available for logging and metrics population.
        func = limiter(func)
        func = log_rpc(func)
        if instance_getter:
            func = authorize(func)
        func = handle_errors(request_formatter)(func)
        func = network_io(func)
        func = timed(METRIC.RPC.DURATION)(func)
        func = metadatacontext(func)
        func = track_request_id(func)
        func = named_rpc(func)
        if instance_getter:
            func = instanced(instance_getter)(func)

        return func

    return decorator
