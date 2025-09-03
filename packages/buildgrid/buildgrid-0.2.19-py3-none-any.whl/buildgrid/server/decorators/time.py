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
import time
from datetime import timedelta
from typing import Any, Callable, Iterator, TypeVar, cast

import grpc

from buildgrid.server.metrics_utils import publish_timer_metric

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def _service_metadata(*args: Any, _error: str | None = None) -> dict[str, str]:
    # If the decorator is being used for service methods, then we assume errors are already being handled.
    # If an error does get through somehow, assume this leads to an internal error.
    if len(args) == 3:
        if isinstance(context := args[2], grpc.ServicerContext):
            code = context.code()  # type: ignore[attr-defined]
            if code is None:
                code = grpc.StatusCode.OK if _error is None else grpc.StatusCode.INTERNAL
            return {"status": code.name}

    # In this case, the error handling is being used for a normal method. Report the error.
    if _error is not None:
        return {"exceptionType": _error}

    return {}


def timed(metric_name: str, **tags: str) -> Callable[[Func], Func]:
    def decorator(func: Func) -> Func:
        @functools.wraps(func)
        def return_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            error: str | None = None
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = e.__class__.__name__
                raise
            finally:
                run_time = timedelta(seconds=time.perf_counter() - start_time)
                publish_timer_metric(metric_name, run_time, **_service_metadata(*args, _error=error), **tags)

        @functools.wraps(func)
        def yield_wrapper(*args: Any, **kwargs: Any) -> Iterator[Any]:
            start_time = time.perf_counter()
            error: str | None = None
            try:
                yield from func(*args, **kwargs)
            except Exception as e:
                error = e.__class__.__name__
                raise
            finally:
                run_time = timedelta(seconds=time.perf_counter() - start_time)
                publish_timer_metric(metric_name, run_time, **_service_metadata(*args, _error=error), **tags)

        if inspect.isgeneratorfunction(func):
            return cast(Func, yield_wrapper)
        return cast(Func, return_wrapper)

    return decorator
