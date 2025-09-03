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

from contextvars import ContextVar
from dataclasses import dataclass

import sentry_sdk


@dataclass
class Sentry:
    dsn: str
    sample_rate: float
    proxy: str


SentryContext: "ContextVar[Sentry | None]" = ContextVar("Sentry", default=None)


def set_sentry_client(sentry: Sentry) -> None:
    if sentry:
        sentry_sdk.init(
            dsn=sentry.dsn,
            sample_rate=sentry.sample_rate,
            http_proxy=sentry.proxy,
            # Our default configuration should only handle exceptions that are
            # explicitly caught using sentry_sdk.capture_exception()
            default_integrations=False,
        )
    SentryContext.set(sentry)


def get_sentry_client() -> Sentry | None:
    return SentryContext.get()


def send_exception_to_sentry(e: Exception) -> None:
    sentry = get_sentry_client()
    if sentry:
        sentry_sdk.capture_exception(e)
