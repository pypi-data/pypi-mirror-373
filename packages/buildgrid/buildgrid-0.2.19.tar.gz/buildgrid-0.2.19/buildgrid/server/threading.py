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

import contextvars
import threading
from concurrent import futures
from concurrent.futures import Future
from typing import Any, Callable, Iterable, ParamSpec, TypeVar

from buildgrid.server.logging import buildgrid_logger

_T = TypeVar("_T")
_P = ParamSpec("_P")


LOGGER = buildgrid_logger(__name__)


class ContextThreadPoolExecutor(futures.ThreadPoolExecutor):
    def __init__(
        self,
        max_workers: int | None = None,
        thread_name_prefix: str = "",
        initializer: Callable[[], Any] | None = None,
        initargs: tuple[Any, ...] = (),
        immediate_copy: bool = False,
    ) -> None:
        """
        Create a thread pool executor which forwards context from the creating thread.

        immediate_copy if true, copies the context when this threadpool object is created.
        If false, the context will be copied as jobs are submitted to it.
        """

        self._init_ctx: contextvars.Context | None = None
        if immediate_copy:
            self._init_ctx = contextvars.copy_context()

        super().__init__(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            initargs=initargs,
        )

    def submit(self, fn: Callable[_P, _T], /, *args: _P.args, **kwargs: _P.kwargs) -> Future[_T]:
        if self._init_ctx is None:
            run = contextvars.copy_context().run
        else:
            run = self._init_ctx.copy().run

        # In newer versions of grpcio (>=1.60.0), a context is used, but is not copied from
        # the initializer thread. We can use our own instead.
        if isinstance(getattr(fn, "__self__", None), contextvars.Context):
            return super().submit(run, *args, **kwargs)  # type: ignore[arg-type]
        return super().submit(run, fn, *args, **kwargs)  # type: ignore[arg-type]


class ContextThread(threading.Thread):
    def __init__(
        self,
        target: "Callable[_P, _T]",
        name: str | None = None,
        args: Iterable[Any] = (),
        kwargs: dict[str, Any] | None = None,
        *,
        daemon: bool | None = None,
    ) -> None:
        ctx = contextvars.copy_context()
        super().__init__(
            target=ctx.copy().run,
            name=name,
            args=(target, *args),
            kwargs=kwargs,
            daemon=daemon,
        )


class ContextWorker:
    def __init__(
        self,
        target: Callable[[threading.Event], None],
        name: str | None = None,
        *,
        on_shutdown_requested: Callable[[], None] | None = None,
    ) -> None:
        """
        Run a long-lived task in a thread, where the method is provided an Event that indicates if
        shutdown is requested. We delay creating the thread until started to allow the context
        to continue to be populated.
        """

        self._shutdown_requested = threading.Event()
        self._thread: ContextThread | None = None

        self._target = target
        self._name = name
        self._on_shutdown_requested = on_shutdown_requested

    def is_alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def __enter__(self) -> "ContextWorker":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        if not self._thread:
            self._thread = ContextThread(
                target=lambda: self._target(self._shutdown_requested), name=self._name, daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        if not self._shutdown_requested.is_set():
            LOGGER.info("Stopping worker.", tags=dict(name=self._name))
            self._shutdown_requested.set()
            if self._on_shutdown_requested:
                self._on_shutdown_requested()
            if self._thread:
                self._thread.join()
            LOGGER.info("Stopped worker.", tags=dict(name=self._name))

    def wait(self, timeout: float | None = None) -> None:
        if self._thread:
            self._thread.join(timeout=timeout)
