import threading
from typing import Any, Iterator

import grpc
import pytest

from buildgrid.server.context import method_context, service_context
from buildgrid.server.decorators.errors import handle_errors
from buildgrid.server.decorators.limiter import limiter
from buildgrid.server.limiter import Limiter, LimiterConfig, set_limiter
from buildgrid.server.threading import ContextThreadPoolExecutor

from .utils.mocks import mock_context


def test_unary_limiter() -> None:
    set_limiter(Limiter(LimiterConfig(concurrent_request_limit=3)))
    barrier = threading.Barrier(4)
    cond = threading.Condition()

    @handle_errors()
    @limiter
    def unary_call(self: Any, message: Any, context: grpc.ServicerContext) -> None:
        barrier.wait(2)
        with cond:
            cond.wait(2)

    with service_context("foo"), method_context("bar"), ContextThreadPoolExecutor(max_workers=5) as ex:
        try:
            call0 = ex.submit(unary_call, None, None, context0 := mock_context())
            call1 = ex.submit(unary_call, None, None, context1 := mock_context())
            call2 = ex.submit(unary_call, None, None, context2 := mock_context())

            # wait for cond.wait() to be reached by all threads.
            barrier.wait(10)

            call3 = ex.submit(unary_call, None, None, context3 := mock_context())
            with pytest.raises(Exception):
                call3.result(2)

        finally:
            with cond:
                cond.notify_all()

        call0.result(2)
        call1.result(2)
        call2.result(2)

    assert context0.code() is None
    assert context1.code() is None
    assert context2.code() is None
    assert context3.code() == grpc.StatusCode.UNAVAILABLE
    assert context3.details().decode() == "Connection count is above concurrent request threshold: 3"


def test_stream_limiter() -> None:
    set_limiter(Limiter(LimiterConfig(concurrent_request_limit=3)))
    barrier = threading.Barrier(4)
    cond = threading.Condition()

    @handle_errors()
    @limiter
    def stream_call(self: Any, message: Any, context: grpc.ServicerContext) -> Iterator[None]:
        barrier.wait(2)
        with cond:
            cond.wait(2)
        yield

    def wrapped_stream_call(self: Any, message: Any, context: grpc.ServicerContext) -> None:
        for _ in stream_call(self, message, context):
            pass

    with service_context("foo"), method_context("bar"), ContextThreadPoolExecutor(max_workers=5) as ex:
        try:
            call0 = ex.submit(wrapped_stream_call, None, None, context0 := mock_context())
            call1 = ex.submit(wrapped_stream_call, None, None, context1 := mock_context())
            call2 = ex.submit(wrapped_stream_call, None, None, context2 := mock_context())

            # wait for cond.wait() to be reached by all threads.
            barrier.wait(10)

            call3 = ex.submit(wrapped_stream_call, None, None, context3 := mock_context())
            with pytest.raises(Exception):
                call3.result(2)

        finally:
            with cond:
                cond.notify_all()

        call0.result(2)
        call1.result(2)
        call2.result(2)

    assert context0.code() is None
    assert context1.code() is None
    assert context2.code() is None
    assert context3.code() == grpc.StatusCode.UNAVAILABLE
    assert context3.details().decode() == "Connection count is above concurrent request threshold: 3"
