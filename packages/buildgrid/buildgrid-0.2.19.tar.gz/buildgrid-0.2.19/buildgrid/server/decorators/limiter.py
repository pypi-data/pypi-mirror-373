import functools
import inspect
from typing import Any, Callable, Iterator, TypeVar, cast

import grpc

from buildgrid.server.limiter import get_limiter

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


def limiter(f: Func) -> Func:
    @functools.wraps(f)
    def server_stream_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[Any]:
        with get_limiter().with_limiter():
            yield from f(self, message, context)

    @functools.wraps(f)
    def server_unary_wrapper(self: Any, message: Any, context: grpc.ServicerContext) -> Any:
        with get_limiter().with_limiter():
            return f(self, message, context)

    if inspect.isgeneratorfunction(f):
        return cast(Func, server_stream_wrapper)
    return cast(Func, server_unary_wrapper)
