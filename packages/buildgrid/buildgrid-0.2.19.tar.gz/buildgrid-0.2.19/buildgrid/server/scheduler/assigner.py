import random
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generator, Literal, Protocol, Union

from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.threading import ContextWorker

if TYPE_CHECKING:
    # Avoid circular import
    from .impl import BotAssignmentFn, Scheduler

LOGGER = buildgrid_logger(__name__)


@dataclass(frozen=True)
class SamplingConfig:
    """
    Configuration for sampling bots, used by `BotAssignmentStrategy`.
    If enabled, the assigner will sample a list of bots without locking them and choose the best one.
    """

    sample_size: int
    max_attempts: int = 1


@dataclass(frozen=True)
class AssignByCapacity:
    kind: Literal["capacity"] = "capacity"
    sampling: SamplingConfig | None = None


@dataclass(frozen=True)
class AssignByLocality:
    kind: Literal["locality"] = "locality"
    sampling: SamplingConfig | None = None
    fallback: "BotAssignmentStrategy" = AssignByCapacity()


# Use dataclasses for these types, so it's easier to extend them in the future
BotAssignmentStrategy = Union[AssignByCapacity, AssignByLocality]


def create_bot_assignment_fn(
    strategy: BotAssignmentStrategy, scheduler: "Scheduler", assigner_name: str
) -> "BotAssignmentFn":
    match strategy:
        case AssignByCapacity():
            LOGGER.info(f"{assigner_name} will match bots by capacity.")
            return lambda session, job: scheduler.match_bot_by_capacity(session, job, strategy.sampling)
        case AssignByLocality():
            LOGGER.info(f"{assigner_name} will match bots by locality.")
            return lambda session, job: scheduler.match_bot_by_locality(
                session,
                job,
                create_bot_assignment_fn(strategy.fallback, scheduler, f"{assigner_name}-fallback"),
                strategy.sampling,
            )


class JobAssigner(Protocol):

    def __enter__(self) -> "JobAssigner": ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

    def start(self) -> None: ...

    def stop(self) -> None: ...

    def begin(self, shutdown_requested: threading.Event) -> None: ...


class PriorityAgeJobAssigner:

    def __init__(
        self,
        scheduler: "Scheduler",
        name: str,
        interval: float,
        priority_percentage: int = 100,
        jitter_factor: float = 1,
        failure_backoff: float = 5.0,
        busy_sleep_factor: float = 0.01,
        instance_names: frozenset[str] | None = None,
        bot_assignment_strategy: BotAssignmentStrategy = AssignByCapacity(),
    ):
        self._assigner = ContextWorker(target=self.begin, name=name)
        self._failure_backoff = failure_backoff
        self._interval = interval
        self._jitter_factor = jitter_factor
        self._name = name
        self._priority_percentage = priority_percentage
        self._scheduler = scheduler
        self._busy_sleep_factor = busy_sleep_factor
        self._instance_names = instance_names

        self._bot_assignment_strategy = bot_assignment_strategy
        self._bot_assignment_fn = create_bot_assignment_fn(bot_assignment_strategy, scheduler, name)

    def __enter__(self) -> "JobAssigner":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._assigner.start()

    def stop(self) -> None:
        self._assigner.stop()

    def begin(self, shutdown_requested: threading.Event) -> None:
        while not shutdown_requested.is_set():
            try:
                prob = random.randint(1, 100)
                assign_func = (
                    self._scheduler.assign_job_by_priority
                    if prob <= self._priority_percentage
                    else self._scheduler.assign_job_by_age
                )
                num_updated = assign_func(
                    self._failure_backoff,
                    self._instance_names,
                    self._bot_assignment_fn,
                    self._name,
                )
                interval = self._interval + (random.random() * self._jitter_factor)
                if num_updated > 0:
                    interval *= self._busy_sleep_factor

                shutdown_requested.wait(timeout=interval)
            except Exception as e:
                LOGGER.exception(
                    f"{self._name} encountered exception: {e}.",
                    tags=dict(retry_delay_seconds=self._interval),
                    exc_info=e,
                )
                # Sleep for a bit so that we give enough time for the
                # database to potentially recover
                shutdown_requested.wait(timeout=self._interval)


class AssignerConfig(Protocol):
    count: int
    interval: float

    def generate_assigners(self, scheduler: "Scheduler") -> Generator[JobAssigner, None, None]:
        """Generate the actual JobAssigner objects defined by this configuration."""
        ...


@dataclass
class PriorityAgeAssignerConfig:
    name: str
    count: int
    interval: float
    priority_assignment_percentage: int = 100
    failure_backoff: float = 5.0
    jitter_factor: float = 1.0
    busy_sleep_factor: float = 0.01
    instance_names: frozenset[str] | None = None
    bot_assignment_strategy: BotAssignmentStrategy = AssignByCapacity()

    def generate_assigners(self, scheduler: "Scheduler") -> Generator[PriorityAgeJobAssigner, None, None]:
        LOGGER.info("Generating assigners.", tags={"count": self.count, "name": self.name})
        for i in range(0, self.count):
            yield PriorityAgeJobAssigner(
                scheduler=scheduler,
                name=self.name,
                interval=self.interval,
                priority_percentage=self.priority_assignment_percentage,
                failure_backoff=self.failure_backoff,
                jitter_factor=self.jitter_factor,
                busy_sleep_factor=self.busy_sleep_factor,
                instance_names=self.instance_names,
                bot_assignment_strategy=self.bot_assignment_strategy,
            )
