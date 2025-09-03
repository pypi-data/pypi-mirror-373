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

from buildgrid.server.auth.manager import authorize_request
from buildgrid.server.context import current_instance
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import timer

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def authorize(f: Func) -> Func:
    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
        try:
            with timer(METRIC.RPC.AUTH_DURATION):
                authorize_request(context, current_instance(), f.__name__)
            yield from f(self, message, context)
        except InvalidArgumentError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
        try:
            with timer(METRIC.RPC.AUTH_DURATION):
                authorize_request(context, current_instance(), f.__name__)
            return f(self, message, context)
        except InvalidArgumentError as e:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)
