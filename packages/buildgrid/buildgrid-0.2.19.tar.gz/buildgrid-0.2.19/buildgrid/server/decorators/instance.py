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
import itertools
from typing import Any, Callable, Iterator, TypeVar, cast

import grpc

from buildgrid.server.context import instance_context
from buildgrid.server.decorators.errors import error_context

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def instanced(get_instance_name: Callable[[Any], str]) -> Callable[[Func], Func]:
    def _get_instance_name(context: grpc.ServicerContext, message: Any) -> str:
        with error_context(context, "Unexpected error when determining instance name"):
            return get_instance_name(message)

    def decorator(f: Func) -> Func:
        @functools.wraps(f)
        def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
            if isinstance(message, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                first_message = next(message)
                message = itertools.chain([first_message], message)
                instance_name = _get_instance_name(context, first_message)
            else:
                instance_name = _get_instance_name(context, message)

            with instance_context(instance_name):
                yield from f(self, message, context)

        @functools.wraps(f)
        def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
            if isinstance(message, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                first_message = next(message)
                message = itertools.chain([first_message], message)
                instance_name = _get_instance_name(context, first_message)
            else:
                instance_name = _get_instance_name(context, message)

            with instance_context(instance_name):
                return f(self, message, context)

        if inspect.isgeneratorfunction(f):
            return cast(Func, server_stream_wrapper)
        return cast(Func, server_unary_wrapper)

    return decorator
