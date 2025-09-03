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

from buildgrid.server.metadata import ctx_request_metadata, extract_request_metadata

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def metadatacontext(f: Func) -> Func:
    """Helper function to obtain metadata and set request metadata ContextVar,
    and then reset it on completion of method.

    Note:
        args[2] of the method must be of type grpc.ServicerContext

    This returns a decorator that extracts the invocation_metadata from the
    context argument and sets the ContextVar variable with it. Resetting the
    ContextVar variable after the method has completed.
    """

    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
        metadata = extract_request_metadata(context.invocation_metadata())
        token = ctx_request_metadata.set(metadata)
        try:
            yield from f(self, message, context)
        finally:
            ctx_request_metadata.reset(token)

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
        metadata = extract_request_metadata(context.invocation_metadata())
        token = ctx_request_metadata.set(metadata)
        try:
            return f(self, message, context)
        finally:
            ctx_request_metadata.reset(token)

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)
