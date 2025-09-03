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

import inspect
import uuid
from functools import wraps
from typing import Any, Callable, Iterator, TypeVar, cast

from buildgrid.server.metadata import ctx_grpc_request_id

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def track_request_id(f: Func) -> Func:
    """Decorator to set the request ID ContextVar.

    This decorator sets the ``ctx_grpc_request_id`` ContextVar to a UUID
    for the duration of the decorated function. This ContextVar is used
    in logging output to allow log lines for the same request to be
    identified.

    """

    @wraps(f)
    def return_wrapper(*args: Any, **kwargs: Any) -> Any:
        ctx_grpc_request_id.set(str(uuid.uuid4()))
        try:
            return f(*args, **kwargs)
        finally:
            ctx_grpc_request_id.set(None)

    @wraps(f)
    def yield_wrapper(*args: Any, **kwargs: Any) -> Iterator[Any]:
        ctx_grpc_request_id.set(str(uuid.uuid4()))
        try:
            yield from f(*args, **kwargs)
        finally:
            ctx_grpc_request_id.set(None)

    if inspect.isgeneratorfunction(f):
        return cast(Func, yield_wrapper)
    return cast(Func, return_wrapper)
