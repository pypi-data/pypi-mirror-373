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


from threading import Event
from typing import Callable

from grpc import ServicerContext

from buildgrid.server.logging import buildgrid_logger

LOGGER = buildgrid_logger(__name__)


class CancellationContext:
    def __init__(self, context: ServicerContext) -> None:
        """
        Creates a wrapper for a grpc.ServicerContext which allows determining if a gRPC request has been
        cancelled by the client. Callbacks may be added to this context which will be invoked if the
        underlying grpc.ServicerContext is triggered.
        """

        self._event = Event()
        self._context = context
        self._callbacks: list[Callable[[], None]] = []
        context.add_callback(self._on_callback)

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def _on_callback(self) -> None:
        LOGGER.debug("Request cancelled.")
        self._event.set()
        for callback in self._callbacks:
            callback()

    def on_cancel(self, callback: Callable[[], None]) -> None:
        self._callbacks.append(callback)
        if self.is_cancelled():
            callback()
