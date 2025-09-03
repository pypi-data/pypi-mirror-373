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

import contextlib
import inspect
import itertools
from functools import wraps
from typing import Any, Callable, Iterator, TypeVar, cast

import grpc

from buildgrid.server.exceptions import (
    BotSessionCancelledError,
    BotSessionClosedError,
    BotSessionMismatchError,
    DuplicateBotSessionError,
    FailedPreconditionError,
    IncompleteReadError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
    ResourceExhaustedError,
    RetriableError,
    UnknownBotSessionError,
)
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.sentry import send_exception_to_sentry

Func = TypeVar("Func", bound=Callable)  # type: ignore[type-arg]


LOGGER = buildgrid_logger(__name__)


@contextlib.contextmanager
def error_context(context: grpc.ServicerContext, unhandled_message: str) -> Iterator[None]:
    try:
        yield

    except BotSessionCancelledError as e:
        LOGGER.info(e)
        context.abort(grpc.StatusCode.CANCELLED, str(e))

    except BotSessionClosedError as e:
        LOGGER.debug(e)
        context.abort(grpc.StatusCode.DATA_LOSS, str(e))

    except IncompleteReadError as e:
        LOGGER.exception(e)
        context.abort(grpc.StatusCode.DATA_LOSS, str(e))

    except ConnectionError as e:
        LOGGER.exception(e)
        context.abort(grpc.StatusCode.UNAVAILABLE, str(e))

    except DuplicateBotSessionError as e:
        LOGGER.info(e)
        context.abort(grpc.StatusCode.ABORTED, str(e))

    except FailedPreconditionError as e:
        LOGGER.error(e)
        context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(e))

    except (InvalidArgumentError, BotSessionMismatchError, UnknownBotSessionError) as e:
        LOGGER.info(e)
        context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

    except NotFoundError as e:
        LOGGER.debug(e)
        context.abort(grpc.StatusCode.NOT_FOUND, str(e))

    except NotImplementedError as e:
        LOGGER.info(e)
        context.abort(grpc.StatusCode.UNIMPLEMENTED, str(e))

    except PermissionDeniedError as e:
        LOGGER.exception(e)
        context.abort(grpc.StatusCode.PERMISSION_DENIED, str(e))

    except RetriableError as e:
        LOGGER.info("Retriable error.", tags=dict(client_retry_delay=e.retry_info.retry_delay))
        context.abort_with_status(e.error_status)

    except ResourceExhaustedError as e:
        LOGGER.exception(e)
        context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, str(e))

    except Exception as e:
        if context.code() is None:  # type: ignore[attr-defined]
            send_exception_to_sentry(e)
            LOGGER.exception(unhandled_message)
            context.abort(grpc.StatusCode.INTERNAL, str(e))
        raise


def handle_errors(get_printable_request: Callable[[Any], Any] = lambda r: str(r)) -> Callable[[Func], Func]:
    def decorator(f: Func) -> Func:
        @wraps(f)
        def return_wrapper(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
            if isinstance(request, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                initial_request = next(request)
                printed_request = get_printable_request(initial_request)
                request = itertools.chain([initial_request], request)
            else:
                printed_request = get_printable_request(request)

            with error_context(context, f"Unexpected error in {f.__name__}; request=[{printed_request}]"):
                return f(self, request, context)

        @wraps(f)
        def yield_wrapper(self: Any, request: Any, context: grpc.ServicerContext) -> Any:
            if isinstance(request, Iterator):
                # Pop the message out to get the instance from it, then and recreate the iterator.
                initial_request = next(request)
                printed_request = get_printable_request(initial_request)
                request = itertools.chain([initial_request], request)
            else:
                printed_request = get_printable_request(request)

            with error_context(context, f"Unexpected error in {f.__name__}; request=[{printed_request}]"):
                yield from f(self, request, context)

        if inspect.isgeneratorfunction(f):
            return cast(Func, yield_wrapper)
        return cast(Func, return_wrapper)

    return decorator
