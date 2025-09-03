import threading
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Iterator

from buildgrid.server.context import current_method, current_service


@dataclass
class LimiterConfig:
    concurrent_request_limit: int = 0


@dataclass
class ConnectionCounts:
    counts: dict[str, dict[str, int]] = field(default_factory=dict)

    def increment(self, service: str, method: str) -> None:
        if service not in self.counts:
            self.counts[service] = {}

        if method not in self.counts[service]:
            self.counts[service][method] = 0

        self.counts[service][method] += 1

    def decrement(self, service: str, method: str) -> None:
        if service in self.counts:
            if method in self.counts[service]:
                self.counts[service][method] -= 1
                if self.counts[service][method] <= 0:
                    del self.counts[service][method]

            if len(self.counts[service]) == 0:
                del self.counts[service]

    def total(self) -> int:
        return sum(sum(method_counts.values()) for method_counts in self.counts.values())

    def copy(self) -> "ConnectionCounts":
        return ConnectionCounts(
            counts={
                service: {method: count for method, count in methods.items()}
                for service, methods in self.counts.items()
            },
        )


class Limiter:
    def __init__(self, config: LimiterConfig) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._counts = ConnectionCounts()

    @contextmanager
    def with_limiter(self) -> Iterator[None]:
        service = current_service()
        method = current_method()
        try:
            with self._lock:
                self._counts.increment(service, method)
                if self._config.concurrent_request_limit > 0:
                    if self._counts.total() > self._config.concurrent_request_limit:
                        # results in response code UNAVAILABLE
                        raise ConnectionError(
                            "Connection count is above concurrent request threshold: "
                            f"{self._config.concurrent_request_limit}"
                        )
            yield
        finally:
            with self._lock:
                self._counts.decrement(service, method)

    @property
    def connection_counts(self) -> ConnectionCounts:
        with self._lock:
            return self._counts.copy()


# By default, the limiter is not configured with a limit.
LimiterContext: "ContextVar[Limiter]" = ContextVar("Limiter", default=Limiter(LimiterConfig()))


def set_limiter(limiter: Limiter) -> None:
    LimiterContext.set(limiter)


def get_limiter() -> Limiter:
    return LimiterContext.get()
