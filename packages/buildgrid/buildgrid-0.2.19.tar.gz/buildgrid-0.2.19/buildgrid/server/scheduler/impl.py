# Copyright (C) 2019 Bloomberg LP
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
import threading
import uuid
from collections import defaultdict
from contextlib import ExitStack
from datetime import datetime, timedelta
from time import time
from typing import Any, Callable, Generator, Iterable, NamedTuple, Sequence, Tuple, TypedDict, TypeVar, cast

from buildgrid_metering.client import SyncMeteringServiceClient
from buildgrid_metering.models.dataclasses import ComputingUsage, Identity, Usage
from google.protobuf.any_pb2 import Any as ProtoAny
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import Channel
from sqlalchemy import ColumnExpressionArgument, and_, delete, func, insert, or_, select, text, update
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql.expression import Insert, Select

from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    Action,
    ActionResult,
    Command,
    Digest,
    ExecutedActionMetadata,
    ExecuteOperationMetadata,
    ExecuteResponse,
    RequestMetadata,
    ToolDetails,
)
from buildgrid._protos.build.buildbox.execution_stats_pb2 import ExecutionStatistics
from buildgrid._protos.build.buildgrid.identity_pb2 import ClientIdentity
from buildgrid._protos.build.buildgrid.scheduling_pb2 import SchedulingMetadata
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import Lease
from buildgrid._protos.google.longrunning import operations_pb2
from buildgrid._protos.google.longrunning.operations_pb2 import Operation
from buildgrid._protos.google.rpc import code_pb2, status_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.actioncache.caches.action_cache_abc import ActionCacheABC
from buildgrid.server.cas.storage.storage_abc import StorageABC
from buildgrid.server.client.asset import AssetClient
from buildgrid.server.client.logstream import logstream_client
from buildgrid.server.context import current_instance, instance_context, try_current_instance
from buildgrid.server.decorators import timed
from buildgrid.server.enums import BotStatus, LeaseState, MeteringThrottleAction, OperationStage
from buildgrid.server.exceptions import (
    BotSessionClosedError,
    BotSessionMismatchError,
    CancelledError,
    DatabaseError,
    InvalidArgumentError,
    NotFoundError,
    ResourceExhaustedError,
    UpdateNotAllowedError,
)
from buildgrid.server.logging import Tags, buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_timer_metric, timer
from buildgrid.server.operations.filtering import DEFAULT_SORT_KEYS, OperationFilter, SortKey
from buildgrid.server.settings import DEFAULT_MAX_EXECUTION_TIMEOUT, SQL_SCHEDULER_METRICS_PUBLISH_INTERVAL_SECONDS
from buildgrid.server.sql.models import Base as OrmBase
from buildgrid.server.sql.models import (
    BotEntry,
    BotLocalityHintEntry,
    BotPlatformEntry,
    ClientIdentityEntry,
    JobEntry,
    OperationEntry,
    PlatformEntry,
    PropertyLabelEntry,
    RequestMetadataEntry,
    digest_to_string,
    job_platform_association,
    string_to_digest,
)
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.server.sql.utils import (
    build_custom_filters,
    build_page_filter,
    build_page_token,
    build_sort_column_list,
    extract_sort_keys,
)
from buildgrid.server.threading import ContextWorker
from buildgrid.server.utils.digests import create_digest

from .assigner import AssignerConfig, SamplingConfig
from .notifier import BotNotifier, NotificationChannel, OperationsNotifier
from .properties import PropertySet, hash_from_dict

LOGGER = buildgrid_logger(__name__)


PROTOBUF_MEDIA_TYPE = "application/x-protobuf"
DIGEST_URI_TEMPLATE = "nih:sha-256;{digest_hash}"


class SchedulerMetrics(TypedDict, total=False):
    #  dict[tuple[stage_name: str, property_label: str], number_of_jobs: int]
    jobs: dict[tuple[str, str], int]


class BotMetrics(TypedDict, total=False):
    #  dict[tuple[bot_status: BotStatus], number_of_bots: int]
    bots_total: dict[BotStatus, int]

    #  dict[tuple[bot_status: BotStatus, property_label: str], number_of_bots: int]
    bots_per_property_label: dict[tuple[BotStatus, str], int]


class AgedJobHandlerOptions(NamedTuple):
    job_max_age: timedelta = timedelta(days=30)
    handling_period: timedelta = timedelta(minutes=5)
    max_handling_window: int = 10000

    @staticmethod
    def from_config(
        job_max_age_cfg: dict[str, float],
        handling_period_cfg: dict[str, float] | None = None,
        max_handling_window_cfg: int | None = None,
    ) -> "AgedJobHandlerOptions":
        """Helper method for creating ``AgedJobHandlerOptions`` objects
        If input configs are None, assign defaults"""

        def _dict_to_timedelta(config: dict[str, float]) -> timedelta:
            return timedelta(
                weeks=config.get("weeks", 0),
                days=config.get("days", 0),
                hours=config.get("hours", 0),
                minutes=config.get("minutes", 0),
                seconds=config.get("seconds", 0),
            )

        return AgedJobHandlerOptions(
            job_max_age=_dict_to_timedelta(job_max_age_cfg) if job_max_age_cfg else timedelta(days=30),
            handling_period=_dict_to_timedelta(handling_period_cfg) if handling_period_cfg else timedelta(minutes=5),
            max_handling_window=max_handling_window_cfg if max_handling_window_cfg else 10000,
        )


T = TypeVar("T", bound="Scheduler")


BotAssignmentFn = Callable[[Session, JobEntry], BotEntry | None]


class Scheduler:
    RETRYABLE_STATUS_CODES = (code_pb2.INTERNAL, code_pb2.UNAVAILABLE)

    def __init__(
        self,
        sql_provider: SqlProvider,
        storage: StorageABC,
        *,
        sql_ro_provider: SqlProvider | None = None,
        sql_notifier_provider: SqlProvider | None = None,
        property_set: PropertySet,
        action_cache: ActionCacheABC | None = None,
        action_browser_url: str | None = None,
        max_execution_timeout: int = DEFAULT_MAX_EXECUTION_TIMEOUT,
        metering_client: SyncMeteringServiceClient | None = None,
        metering_throttle_action: MeteringThrottleAction | None = None,
        bot_session_keepalive_timeout: int = 600,
        logstream_channel: Channel | None = None,
        logstream_instance: str | None = None,
        asset_client: AssetClient | None = None,
        queued_action_retention_hours: float | None = None,
        completed_action_retention_hours: float | None = None,
        action_result_retention_hours: float | None = None,
        enable_job_watcher: bool = False,
        poll_interval: float = 1,
        pruning_options: AgedJobHandlerOptions | None = None,
        queue_timeout_options: AgedJobHandlerOptions | None = None,
        max_job_attempts: int = 5,
        assigner_configs: Sequence[AssignerConfig] | None = None,
        max_queue_size: int | None = None,
        execution_timer_interval: float = 60.0,
        session_expiry_timer_interval: float = 10.0,
        instance_pools: list[list[str]] | None = None,
        bot_locality_hint_limit: int = 10,
        bot_poll_interval: float = 1.0,
    ) -> None:
        self._stack = ExitStack()

        self.storage = storage

        self.poll_interval = poll_interval
        self.bot_poll_interval = bot_poll_interval
        self.execution_timer_interval = execution_timer_interval
        self.session_expiry_interval = session_expiry_timer_interval
        self.pruning_options = pruning_options
        self.queue_timeout_options = queue_timeout_options
        self.max_job_attempts = max_job_attempts
        self.instance_pools = instance_pools or []
        self.bot_locality_hint_limit = bot_locality_hint_limit

        self._sql = sql_provider
        self._sql_ro = sql_ro_provider or sql_provider
        self._sql_notifier = sql_notifier_provider or sql_provider

        self.property_set = property_set

        self.action_cache = action_cache
        self.action_browser_url = (action_browser_url or "").rstrip("/")
        self.max_execution_timeout = max_execution_timeout
        self.enable_job_watcher = enable_job_watcher
        self.metering_client = metering_client
        self.metering_throttle_action = metering_throttle_action or MeteringThrottleAction.DEPRIORITIZE
        self.bot_session_keepalive_timeout = bot_session_keepalive_timeout
        self.logstream_channel = logstream_channel
        self.logstream_instance = logstream_instance
        self.asset_client = asset_client
        self.queued_action_retention_hours = queued_action_retention_hours
        self.completed_action_retention_hours = completed_action_retention_hours
        self.action_result_retention_hours = action_result_retention_hours
        self.max_queue_size = max_queue_size

        # Overall Scheduler Metrics (totals of jobs/leases in each state)
        # Publish those metrics a bit more sparsely since the SQL requests
        # required to gather them can become expensive
        self._last_scheduler_metrics_publish_time: dict[str, datetime] = {}
        self._scheduler_metrics_publish_interval = timedelta(seconds=SQL_SCHEDULER_METRICS_PUBLISH_INTERVAL_SECONDS)

        self.ops_notifier = OperationsNotifier(self._sql_notifier, self.poll_interval)
        self.bot_notifier = BotNotifier(self._sql_notifier, self.bot_poll_interval)
        self.prune_timer = ContextWorker(name="JobPruner", target=self.prune_timer_loop)
        self.queue_timer = ContextWorker(name="QueueTimeout", target=self.queue_timer_loop)
        self.execution_timer = ContextWorker(name="ExecutionTimeout", target=self.execution_timer_loop)
        self.session_expiry_timer = ContextWorker(self.session_expiry_timer_loop, "BotReaper")

        # The scheduling threads that will actually assign work
        self.assigners = [
            assigner for config in (assigner_configs or []) for assigner in config.generate_assigners(self)
        ]

    def __repr__(self) -> str:
        return f"Scheduler for `{repr(self._sql._engine.url)}`"

    def __enter__(self: T) -> T:
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._stack.enter_context(self.storage)
        if self.action_cache:
            self._stack.enter_context(self.action_cache)

        if self.logstream_channel:
            self._stack.enter_context(self.logstream_channel)
        if self.asset_client:
            self._stack.enter_context(self.asset_client)
        # Pruning configuration parameters
        if self.pruning_options is not None:
            LOGGER.info(f"Scheduler pruning enabled: {self.pruning_options}")
            self._stack.enter_context(self.prune_timer)
        else:
            LOGGER.info("Scheduler pruning not enabled.")

        # Queue timeout thread
        if self.queue_timeout_options is not None:
            LOGGER.info(f"Job queue timeout enabled: {self.queue_timeout_options}")
            self._stack.enter_context(self.queue_timer)
        else:
            LOGGER.info("Job queue timeout not enabled.")

        if self.execution_timer_interval > 0:
            self._stack.enter_context(self.execution_timer)
        if self.poll_interval > 0:
            self._stack.enter_context(self.ops_notifier)

        for assigner in self.assigners:
            self._stack.enter_context(assigner)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info("Stopped Scheduler.")

    def _job_in_instance_pool(self) -> ColumnExpressionArgument[bool]:
        instance_name = current_instance()
        for pool in self.instance_pools:
            if instance_name in pool:
                return JobEntry.instance_name.in_(pool)
        return JobEntry.instance_name == current_instance()

    def _bot_in_instance_pool(self) -> ColumnExpressionArgument[bool]:
        instance_name = current_instance()
        for pool in self.instance_pools:
            if instance_name in pool:
                return BotEntry.instance_name.in_(pool)
        return BotEntry.instance_name == current_instance()

    @functools.lru_cache(maxsize=100)
    def _bot_in_instance_pool_for_name(self, instance_name: str) -> ColumnExpressionArgument[bool]:
        instance_names = {instance_name}
        for pool in self.instance_pools:
            if instance_name in pool:
                instance_names.update(pool)

        if len(instance_names) > 1:
            return BotEntry.instance_name.in_(instance_names)
        return BotEntry.instance_name == instance_name

    @functools.cache
    def _instance_names_closure(self, instance_names: frozenset[str]) -> frozenset[str]:
        closure = set()
        for instance_name in instance_names:
            closure.add(instance_name)
            for pool in self.instance_pools:
                if instance_name in pool:
                    closure.update(pool)

        return frozenset(closure)

    def queue_job_action(
        self,
        *,
        action: Action,
        action_digest: Digest,
        command: Command,
        platform_requirements: dict[str, list[str]],
        property_label: str,
        priority: int,
        skip_cache_lookup: bool,
        request_metadata: RequestMetadata | None = None,
        client_identity: ClientIdentityEntry | None = None,
        scheduling_metadata: SchedulingMetadata | None = None,
    ) -> str:
        """
        De-duplicates or inserts a newly created job into the execution queue.
        Returns an operation name associated with this job.
        """
        if self.max_execution_timeout and action.timeout.seconds > self.max_execution_timeout:
            raise InvalidArgumentError("Action timeout is larger than the server's maximum execution timeout.")

        if not action.do_not_cache:
            if operation_name := self.create_operation_for_existing_job(
                action_digest=action_digest,
                priority=priority,
                request_metadata=request_metadata,
                client_identity=client_identity,
            ):
                return operation_name

        # If there was another job already in the action cache, we can check now.
        # We can use this entry to create a job and create it already completed!
        execute_response: ExecuteResponse | None = None
        if self.action_cache and not action.do_not_cache and not skip_cache_lookup:
            try:
                action_result = self.action_cache.get_action_result(action_digest)
                LOGGER.info("Job cache hit for action.", tags=dict(digest=action_digest))
                execute_response = ExecuteResponse()
                execute_response.result.CopyFrom(action_result)
                execute_response.cached_result = True
            except NotFoundError:
                pass
            except Exception:
                LOGGER.exception("Checking ActionCache for action failed.", tags=dict(digest=action_digest))

        # Extend retention for action
        self._update_action_retention(action, action_digest, self.queued_action_retention_hours)

        return self.create_operation_for_new_job(
            action=action,
            action_digest=action_digest,
            command=command,
            execute_response=execute_response,
            platform_requirements=platform_requirements,
            property_label=property_label,
            priority=priority,
            request_metadata=request_metadata,
            client_identity=client_identity,
            scheduling_metadata=scheduling_metadata,
        )

    def create_operation_for_existing_job(
        self,
        *,
        action_digest: Digest,
        priority: int,
        request_metadata: RequestMetadata | None,
        client_identity: ClientIdentityEntry | None,
    ) -> str | None:
        # Find a job with a matching action that isn't completed or cancelled and that can be cached.
        find_existing_stmt = (
            select(JobEntry)
            .where(
                JobEntry.action_digest == digest_to_string(action_digest),
                JobEntry.stage != OperationStage.COMPLETED.value,
                JobEntry.cancelled != True,  # noqa: E712
                JobEntry.do_not_cache != True,  # noqa: E712
                self._job_in_instance_pool(),
            )
            .with_for_update()
        )

        with self._sql.session(exceptions_to_not_raise_on=[Exception]) as session:
            if not (job := session.execute(find_existing_stmt).scalars().first()):
                return None

            # Reschedule if priority is now greater, and we're still waiting on it to start.
            if priority < job.priority and job.stage == OperationStage.QUEUED.value:
                LOGGER.info("Job assigned a new priority.", tags=dict(job_name=job.name, priority=priority))
                job.priority = priority
                job.assigned = False

            return self._create_operation(
                session,
                job_name=job.name,
                request_metadata=request_metadata,
                client_identity=client_identity,
            )

    def create_operation_for_new_job(
        self,
        *,
        action: Action,
        action_digest: Digest,
        command: Command,
        execute_response: ExecuteResponse | None,
        platform_requirements: dict[str, list[str]],
        property_label: str,
        priority: int,
        request_metadata: RequestMetadata | None = None,
        client_identity: ClientIdentityEntry | None = None,
        scheduling_metadata: SchedulingMetadata | None = None,
    ) -> str:
        if execute_response is None and self.max_queue_size is not None:
            # Using func.count here to avoid generating a subquery in the WHERE
            # clause of the resulting query.
            # https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.query.Query.count
            queue_count_statement = select(func.count(JobEntry.name)).where(
                JobEntry.assigned != True,  # noqa: E712
                self._job_in_instance_pool(),
                JobEntry.property_label == property_label,
                JobEntry.stage == OperationStage.QUEUED.value,
            )
        else:
            queue_count_statement = None

        with self._sql.session(exceptions_to_not_raise_on=[Exception]) as session:
            if queue_count_statement is not None:
                queue_size = session.execute(queue_count_statement).scalar_one()
                if self.max_queue_size is not None and queue_size >= self.max_queue_size:
                    raise ResourceExhaustedError(f"The platform's job queue is full: {property_label=}")

            now = datetime.utcnow()

            # Extract locality_hint from scheduling metadata
            locality_hint = None
            if scheduling_metadata and scheduling_metadata.locality_hint:
                locality_hint = scheduling_metadata.locality_hint

            job = JobEntry(
                instance_name=current_instance(),
                name=str(uuid.uuid4()),
                action=action.SerializeToString(),
                action_digest=digest_to_string(action_digest),
                do_not_cache=action.do_not_cache,
                priority=priority,
                stage=OperationStage.QUEUED.value,
                create_timestamp=now,
                queued_timestamp=now,
                schedule_after=now,
                command=" ".join(command.arguments),
                platform_requirements=hash_from_dict(platform_requirements),
                platform=self._populate_platform_requirements(session, platform_requirements),
                property_label=property_label,
                n_tries=1,
                locality_hint=locality_hint,
            )
            if execute_response:
                job.stage = OperationStage.COMPLETED.value
                job.result = digest_to_string(self.storage.put_message(execute_response))
                job.status_code = execute_response.status.code
                job.worker_completed_timestamp = datetime.utcnow()

            session.add(job)

            return self._create_operation(
                session,
                job_name=job.name,
                request_metadata=request_metadata,
                client_identity=client_identity,
            )

    def _populate_platform_requirements(
        self, session: Session, platform_requirements: dict[str, list[str]]
    ) -> list[PlatformEntry]:
        if not platform_requirements:
            return []

        required_entries = {(k, v) for k, values in platform_requirements.items() for v in values}
        conditions = [and_(PlatformEntry.key == k, PlatformEntry.value == v) for k, v in required_entries]
        statement = select(PlatformEntry.key, PlatformEntry.value).where(or_(*conditions))

        while missing := required_entries - {(k, v) for [k, v] in session.execute(statement).all()}:
            try:
                session.execute(insert(PlatformEntry), [{"key": k, "value": v} for k, v in missing])
                session.commit()
            except IntegrityError:
                session.rollback()

        return list(session.execute(select(PlatformEntry).where(or_(*conditions))).scalars())

    def create_operation(
        self,
        job_name: str,
        *,
        request_metadata: RequestMetadata | None = None,
        client_identity: ClientIdentityEntry | None = None,
    ) -> str:
        with self._sql.session(exceptions_to_not_raise_on=[Exception]) as session:
            if not (job := self._get_job(job_name, session, with_for_update=True)):
                raise NotFoundError(f"Job name does not exist: [{job_name}]")

            if job.cancelled:
                raise CancelledError(f"Job {job_name} is cancelled")

            return self._create_operation(
                session, job_name=job_name, request_metadata=request_metadata, client_identity=client_identity
            )

    def _create_operation(
        self,
        session: Session,
        *,
        job_name: str,
        request_metadata: RequestMetadata | None,
        client_identity: ClientIdentityEntry | None,
    ) -> str:

        client_identity_id: int | None = None
        if client_identity:
            client_identity_id = self.get_or_create_client_identity_in_store(session, client_identity).id

        request_metadata_id: int | None = None
        if request_metadata:
            request_metadata_id = self.get_or_create_request_metadata_in_store(session, request_metadata).id

        request_metadata = request_metadata or RequestMetadata()
        operation = OperationEntry(
            name=str(uuid.uuid4()),
            job_name=job_name,
            client_identity_id=client_identity_id,
            request_metadata_id=request_metadata_id,
        )
        session.add(operation)
        return operation.name

    def load_operation(self, operation_name: str) -> Operation:
        statement = (
            select(OperationEntry)
            .join(JobEntry)
            .where(OperationEntry.name == operation_name, self._job_in_instance_pool())
        )
        with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
            if op := session.execute(statement).scalars().first():
                return self._load_operation(op)

        raise NotFoundError(f"Operation name does not exist: [{operation_name}]")

    def _load_operation(self, op: OperationEntry) -> Operation:
        job: JobEntry = op.job

        operation = operations_pb2.Operation(
            name=op.name,
            done=job.stage == OperationStage.COMPLETED.value or op.cancelled or job.cancelled,
        )
        metadata = ExecuteOperationMetadata(
            stage=OperationStage.COMPLETED.value if operation.done else job.stage,  # type: ignore[arg-type]
            action_digest=string_to_digest(job.action_digest),
            stderr_stream_name=job.stderr_stream_name or "",
            stdout_stream_name=job.stdout_stream_name or "",
            partial_execution_metadata=self.get_execute_action_metadata(job),
        )
        operation.metadata.Pack(metadata)

        if job.cancelled or op.cancelled:
            operation.error.CopyFrom(status_pb2.Status(code=code_pb2.CANCELLED))
        elif job.status_code is not None and job.status_code != code_pb2.OK:
            operation.error.CopyFrom(status_pb2.Status(code=job.status_code))

        execute_response: ExecuteResponse | None = None
        if job.result:
            result_digest = string_to_digest(job.result)
            execute_response = self.storage.get_message(result_digest, ExecuteResponse)
            if not execute_response:
                operation.error.CopyFrom(status_pb2.Status(code=code_pb2.DATA_LOSS))
        elif job.cancelled:
            execute_response = ExecuteResponse(
                status=status_pb2.Status(code=code_pb2.CANCELLED, message="Execution cancelled")
            )

        if execute_response:
            if self.action_browser_url:
                execute_response.message = f"{self.action_browser_url}/action/{job.action_digest}/"
            operation.response.Pack(execute_response)

        return operation

    def _get_job(self, job_name: str, session: Session, with_for_update: bool = False) -> JobEntry | None:
        statement = select(JobEntry).where(JobEntry.name == job_name, self._job_in_instance_pool())
        if with_for_update:
            statement = statement.with_for_update()

        job: JobEntry | None = session.execute(statement).scalars().first()
        if job:
            LOGGER.debug(
                "Loaded job from db.",
                tags=dict(job_name=job_name, job_stage=job.stage, result=job.result, instance_name=job.instance_name),
            )

        return job

    def get_operations_for_bot(self, bot_id: str) -> Generator[Tuple[str, Digest], None, None]:
        with self._sql.session() as session:
            jobs = self._get_incomplete_jobs_for_bot(bot_id, session)
            for job in jobs:
                for operation in job.operations:
                    yield operation.name, string_to_digest(job.action_digest)

    def _get_incomplete_jobs_for_bot(
        self, bot_id: str, session: Session, with_for_update: bool = False
    ) -> Sequence[JobEntry]:
        statement = select(JobEntry).where(
            JobEntry.worker_name == bot_id,
            self._job_in_instance_pool(),
            JobEntry.stage != OperationStage.COMPLETED.value,
        )
        if with_for_update:
            statement = statement.with_for_update()

        jobs = session.execute(statement).scalars().all()
        return jobs

    def get_operation_job_name(self, operation_name: str) -> str | None:
        with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
            if operation := self._get_operation(operation_name, session):
                return operation.job_name
        return None

    def get_operation_request_metadata_by_name(self, operation_name: str) -> RequestMetadata | None:
        with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
            operation = self._get_operation(operation_name, session)
            if not operation or not operation.request_metadata:
                return None

            metadata = RequestMetadata(
                tool_details=ToolDetails(
                    tool_name=operation.request_metadata.tool_name or "",
                    tool_version=operation.request_metadata.tool_version or "",
                ),
                action_id=operation.job.action_digest,
                correlated_invocations_id=operation.request_metadata.correlated_invocations_id or "",
                tool_invocation_id=operation.request_metadata.invocation_id or "",
                action_mnemonic=operation.request_metadata.action_mnemonic or "",
                configuration_id=operation.request_metadata.configuration_id or "",
                target_id=operation.request_metadata.target_id or "",
            )

            return metadata

    def get_client_identity_by_operation(self, operation_name: str) -> ClientIdentity | None:
        with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
            operation = self._get_operation(operation_name, session)
            if not operation or not operation.client_identity:
                return None

            return ClientIdentity(
                actor=operation.client_identity.actor or "",
                subject=operation.client_identity.subject or "",
                workflow=operation.client_identity.workflow or "",
            )

    def _notify_job_updated(self, job_names: str | list[str], session: Session) -> None:
        if self._sql.dialect == "postgresql":
            if isinstance(job_names, str):
                job_names = [job_names]
            for job_name in job_names:
                session.execute(text(f"NOTIFY {NotificationChannel.JOB_UPDATED.value}, '{job_name}';"))

    def _get_operation(self, operation_name: str, session: Session) -> OperationEntry | None:
        statement = (
            select(OperationEntry)
            .join(JobEntry)
            .where(OperationEntry.name == operation_name, self._job_in_instance_pool())
        )
        return session.execute(statement).scalars().first()

    def _batch_timeout_jobs(self, job_select_stmt: Select[Any], status_code: int, message: str) -> int:
        """Timeout all jobs selected by a query"""
        with self._sql.session(sqlite_lock_immediately=True, exceptions_to_not_raise_on=[Exception]) as session:
            # Get the full list of jobs to timeout
            jobs = [job.name for job in session.execute(job_select_stmt).scalars().all()]

            if jobs:
                # Put response binary
                response = remote_execution_pb2.ExecuteResponse(
                    status=status_pb2.Status(code=status_code, message=message)
                )
                response_binary = response.SerializeToString()
                response_digest = create_digest(response_binary)
                self.storage.bulk_update_blobs([(response_digest, response_binary)])

                # Update response
                stmt_timeout_jobs = (
                    update(JobEntry)
                    .where(JobEntry.name.in_(jobs))
                    .values(
                        stage=OperationStage.COMPLETED.value,
                        status_code=status_code,
                        result=digest_to_string(response_digest),
                    )
                )
                session.execute(stmt_timeout_jobs)

                # Notify all jobs updated
                self._notify_job_updated(jobs, session)
            return len(jobs)

    def execution_timer_loop(self, shutdown_requested: threading.Event) -> None:
        """Periodically timeout aged executing jobs"""
        while not shutdown_requested.is_set():
            try:
                self.cancel_jobs_exceeding_execution_timeout(self.max_execution_timeout)
            except Exception as e:
                LOGGER.exception("Failed to timeout aged executing jobs.", exc_info=e)
            shutdown_requested.wait(timeout=self.execution_timer_interval)

    @timed(METRIC.SCHEDULER.EXECUTION_TIMEOUT_DURATION)
    def cancel_jobs_exceeding_execution_timeout(self, max_execution_timeout: int | None = None) -> None:
        if not max_execution_timeout:
            return

        # Get the full list of jobs exceeding execution timeout
        stale_jobs_statement = (
            select(JobEntry)
            .where(
                JobEntry.stage == OperationStage.EXECUTING.value,
                JobEntry.worker_start_timestamp <= datetime.utcnow() - timedelta(seconds=max_execution_timeout),
            )
            .with_for_update(skip_locked=True)
        )
        with self._sql.session(sqlite_lock_immediately=True, exceptions_to_not_raise_on=[Exception]) as session:
            jobs = session.execute(stale_jobs_statement).scalars().all()
            if not jobs:
                return

            response = remote_execution_pb2.ExecuteResponse(
                status=status_pb2.Status(
                    code=code_pb2.DEADLINE_EXCEEDED,
                    message="Execution didn't finish within timeout threshold",
                )
            )
            response_binary = response.SerializeToString()
            response_digest = create_digest(response_binary)

            # When running with a proxying client, we might need to specify instance.
            with instance_context(jobs[0].instance_name):
                self.storage.bulk_update_blobs([(response_digest, response_binary)])

            for job in jobs:
                executing_duration = datetime.utcnow() - (job.worker_start_timestamp or datetime.utcnow())
                LOGGER.warning(
                    "Job has been executing for too long. Cancelling.",
                    tags=dict(
                        job_name=job.name,
                        executing_duration=executing_duration,
                        max_execution_timeout=max_execution_timeout,
                    ),
                )
                for op in job.operations:
                    op.cancelled = True
                job.worker_completed_timestamp = datetime.utcnow()
                job.stage = OperationStage.COMPLETED.value
                job.cancelled = True
                job.result = digest_to_string(response_digest)

            for job in jobs:
                self._notify_job_updated(job.name, session)

            publish_counter_metric(METRIC.SCHEDULER.EXECUTION_TIMEOUT_COUNT, len(jobs))

    def cancel_operation(self, operation_name: str) -> None:
        statement = (
            select(JobEntry)
            .join(OperationEntry)
            .where(OperationEntry.name == operation_name, self._job_in_instance_pool())
            .with_for_update()
        )
        with self._sql.session() as session:
            if not (job := session.execute(statement).scalars().first()):
                raise NotFoundError(f"Operation name does not exist: [{operation_name}]")

            if job.stage == OperationStage.COMPLETED.value or job.cancelled:
                return

            for op in job.operations:
                if op.name == operation_name:
                    if op.cancelled:
                        return
                    op.cancelled = True

            if all(op.cancelled for op in job.operations):
                job.worker_completed_timestamp = datetime.utcnow()
                job.stage = OperationStage.COMPLETED.value
                job.cancelled = True

            self._notify_job_updated(job.name, session)

    def list_operations(
        self,
        operation_filters: list[OperationFilter] | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
    ) -> tuple[list[operations_pb2.Operation], str]:
        # Build filters and sort order
        sort_keys = DEFAULT_SORT_KEYS
        custom_filters = None
        platform_filters = []
        if operation_filters:
            # Extract custom sort order (if present)
            specified_sort_keys, non_sort_filters = extract_sort_keys(operation_filters)

            # Only override sort_keys if there were sort keys actually present in the filter string
            if specified_sort_keys:
                sort_keys = specified_sort_keys
                # Attach the operation name as a sort key for a deterministic order
                # This will ensure that the ordering of results is consistent between queries
                if not any(sort_key.name == "name" for sort_key in sort_keys):
                    sort_keys.append(SortKey(name="name", descending=False))

            # Finally, compile the non-sort filters into a filter list
            custom_filters = build_custom_filters(non_sort_filters)
            platform_filters = [f for f in non_sort_filters if f.parameter == "platform"]

        sort_columns = build_sort_column_list(sort_keys)

        with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
            statement = (
                select(OperationEntry)
                .join(JobEntry, OperationEntry.job_name == JobEntry.name)
                .outerjoin(RequestMetadataEntry)
                .outerjoin(ClientIdentityEntry)
            )
            statement = statement.filter(self._job_in_instance_pool())

            # If we're filtering by platform, filter using a subquery containing job names
            # which match the specified platform properties.
            #
            # NOTE: A platform filter using `!=` will return only jobs which set that platform
            # property to an explicitly different value; jobs which don't set the property are
            # filtered out.
            if platform_filters:
                platform_clauses = []
                for platform_filter in platform_filters:
                    key, value = platform_filter.value.split(":", 1)
                    platform_clauses.append(
                        and_(PlatformEntry.key == key, platform_filter.operator(PlatformEntry.value, value))
                    )

                job_name_subquery = (
                    select(job_platform_association.c.job_name)
                    .filter(
                        job_platform_association.c.platform_id.in_(
                            select(PlatformEntry.id).filter(or_(*platform_clauses))
                        )
                    )
                    .group_by(job_platform_association.c.job_name)
                    .having(func.count() == len(platform_filters))
                )
                statement = statement.filter(JobEntry.name.in_(job_name_subquery))

            # Apply custom filters (if present)
            if custom_filters:
                statement = statement.filter(*custom_filters)

            # Apply sort order
            statement = statement.order_by(*sort_columns)

            # Apply pagination filter
            if page_token:
                page_filter = build_page_filter(page_token, sort_keys)
                statement = statement.filter(page_filter)
            if page_size:
                # We limit the number of operations we fetch to the page_size. However, we
                # fetch an extra operation to determine whether we need to provide a
                # next_page_token.
                statement = statement.limit(page_size + 1)

            operations = list(session.execute(statement).scalars().all())

            if not page_size or not operations:
                next_page_token = ""

            # If the number of results we got is less than or equal to our page_size,
            # we're done with the operations listing and don't need to provide another
            # page token
            elif len(operations) <= page_size:
                next_page_token = ""
            else:
                # Drop the last operation since we have an extra
                operations.pop()
                # Our page token will be the last row of our set
                next_page_token = build_page_token(operations[-1], sort_keys)
            return [self._load_operation(operation) for operation in operations], next_page_token

    def list_workers(self, name_filter: str, page_number: int, page_size: int) -> tuple[list[BotEntry], int]:
        stmt = select(BotEntry, func.count().over().label("total"))
        stmt = stmt.where(
            or_(
                BotEntry.name.ilike(f"%{name_filter}%"),
                BotEntry.bot_id.ilike(f"%{name_filter}%"),
            ),
            BotEntry.instance_name == current_instance(),
        )
        stmt = stmt.order_by(BotEntry.bot_id)

        if page_size:
            stmt = stmt.limit(page_size)
        if page_number > 1:
            stmt = stmt.offset((page_number - 1) * page_size)

        with self._sql.scoped_session() as session:
            results = session.execute(stmt).all()
            count = cast(int, results[0].total) if results else 0
            session.expunge_all()

        return [r[0] for r in results], count

    def get_metrics(self, instance_name: str) -> SchedulerMetrics | None:
        # Skip publishing overall scheduler metrics if we have recently published them
        last_publish_time = self._last_scheduler_metrics_publish_time.get(instance_name)
        time_since_publish = None
        if last_publish_time:
            time_since_publish = datetime.utcnow() - last_publish_time
        if time_since_publish and time_since_publish < self._scheduler_metrics_publish_interval:
            # Published too recently, skip
            return None

        metrics: SchedulerMetrics = {}
        # metrics to gather: (category_name, function_returning_query, callback_function)

        try:
            with self._sql_ro.session(exceptions_to_not_raise_on=[Exception]) as session:
                # To utilize "ix_jobs_stage_property_label" B-tree index we query
                # `stage < COMPLETED.value` rather than `stage != COMPLETED.value`.
                results = session.execute(
                    select(
                        JobEntry.stage.label("job_stage"),
                        JobEntry.property_label.label("property_label"),
                        func.count(JobEntry.name).label("job_count"),
                    )
                    .where(JobEntry.stage < OperationStage.COMPLETED.value, JobEntry.instance_name == instance_name)
                    .group_by(JobEntry.stage, JobEntry.property_label),
                ).all()

                jobs_metrics = {}
                for stage in OperationStage:
                    if stage != OperationStage.COMPLETED:
                        jobs_metrics[stage.name, "unknown"] = 0

                for job_stage, property_label, job_count in results:
                    jobs_metrics[OperationStage(job_stage).name, property_label] = cast(int, job_count)

                metrics["jobs"] = jobs_metrics
        except DatabaseError:
            LOGGER.warning("Unable to gather metrics due to a Database Error.")
            return {}

        # This is only updated within the metrics asyncio loop; no race conditions
        self._last_scheduler_metrics_publish_time[instance_name] = datetime.utcnow()

        return metrics

    def _queued_jobs_by_capability(self, capability_hash: str) -> Select[Any]:
        return (
            select(JobEntry)
            .with_for_update(skip_locked=True)
            .where(
                JobEntry.assigned != True,  # noqa: E712
                self._job_in_instance_pool(),
                JobEntry.platform_requirements == capability_hash,
                JobEntry.stage == OperationStage.QUEUED.value,
            )
        )

    def _assign_job_to_bot(self, session: Session, job: JobEntry, bot: BotEntry) -> None:
        """Assigns a job to a bot, updating both the job and bot entries in the database.
        `job` and `bot` ORM objects must be from `session`.
        """

        job.assigned = True
        job.queued_time_duration = int((datetime.utcnow() - job.queued_timestamp).total_seconds())
        job.worker_start_timestamp = datetime.utcnow()
        job.worker_completed_timestamp = None
        job.worker_name = bot.bot_id
        job.status_code = None

        bot.lease_id = job.name
        bot.last_update_timestamp = datetime.utcnow()

        # Reduce the capacity by 1, to prevent overallocation to this specific bot
        bot.capacity -= 1

        LOGGER.debug("Assigned job to bot", tags={"bot_id": bot.bot_id, "bot_name": bot.name, "job_name": job.name})
        if self._sql.dialect == "postgresql":
            session.execute(text(f"NOTIFY {NotificationChannel.JOB_ASSIGNED.value}, '{bot.name}';"))

    def _match_bot_by_sampling(
        self, session: Session, query: Select[tuple[BotEntry]], sampling: SamplingConfig
    ) -> BotEntry | None:
        for attempt in range(sampling.max_attempts):
            # If we use `read_committed` isolation level, candidates selected can be different in each iteration.
            query = query.order_by(func.random()).limit(sampling.sample_size)
            # Future work: Use redis to cache worker candidates by instance / properties
            with self._sql_ro.session() as ro_session:
                names_query = query.with_only_columns(BotEntry.name)
                candidate_names = ro_session.execute(names_query).scalars().all()
            if candidate_names:
                # For now, we choose the bot with the highest capacity as the best candidate.
                # It would be interesting to extend this to consider other factors in future e.g. expected latencies.
                if bot := session.execute(
                    select(BotEntry)
                    .where(BotEntry.name.in_(candidate_names))
                    .where(*self._bot_healthy_clauses())
                    .order_by(BotEntry.capacity.desc())
                    .with_for_update(skip_locked=True)
                    .limit(1)
                ).scalar_one_or_none():
                    LOGGER.debug(
                        "Matched bot by sampling.",
                        tags={"bot_name": bot.name, "attempt": attempt + 1, "bot_capacity": bot.capacity},
                    )
                    return bot
        LOGGER.debug("No bot matched by sampling after all attempts.")
        return None

    def match_bot_by_capacity(
        self, session: Session, job: JobEntry, sampling: SamplingConfig | None = None
    ) -> BotEntry | None:
        """Select a bot for a job by capacity."""
        query = (
            select(BotEntry)
            .join(BotPlatformEntry, BotEntry.name == BotPlatformEntry.bot_name)
            .where(*self._bot_satisfying_job_clauses(job))
        )
        if sampling is None:
            query = query.where(*self._bot_healthy_clauses()).with_for_update(skip_locked=True).limit(1)
            bot = session.execute(query).scalar_one_or_none()
        else:
            bot = self._match_bot_by_sampling(session, query, sampling)
        if bot:
            LOGGER.debug(
                "Matched bot by capacity.",
                tags={
                    "assignment_strategy": "capacity",
                    "bot_name": bot.name,
                    "job_name": job.name,
                    "bot_capacity": bot.capacity,
                },
            )
            return bot
        return None

    def match_bot_by_locality(
        self,
        session: Session,
        job: JobEntry,
        fallback: BotAssignmentFn | None = None,
        sampling: SamplingConfig | None = None,
    ) -> BotEntry | None:
        """
        Select a bot for a job by locality.
        Run the fallback strategy if no locality match is found.
        """
        if fallback is None:
            fallback = self.match_bot_by_capacity

        query = (
            select(BotEntry)
            .join(BotPlatformEntry, BotEntry.name == BotPlatformEntry.bot_name)
            .join(BotLocalityHintEntry, BotEntry.name == BotLocalityHintEntry.bot_name)
            .where(*self._bot_satisfying_job_clauses(job))
            .where(BotLocalityHintEntry.locality_hint == job.locality_hint)
        )

        if sampling is None:
            query = query.where(*self._bot_healthy_clauses()).with_for_update(skip_locked=True).limit(1)
            bot = session.execute(query).scalar_one_or_none()
        else:
            bot = self._match_bot_by_sampling(session, query, sampling)

        if bot:
            LOGGER.debug(
                "Matched bot by locality.",
                tags={
                    "assignment_strategy": "locality",
                    "bot_name": bot.name,
                    "job_name": job.name,
                    "locality_hint": job.locality_hint,
                    "bot_capacity": bot.capacity,
                },
            )
            return bot
        else:
            LOGGER.debug("No bot matched by locality, using fallback strategy.")
            return fallback(session, job)

    @staticmethod
    def _bot_healthy_clauses() -> list[ColumnExpressionArgument[bool]]:
        """Base clauses for matching a healthy bot"""
        return [
            BotEntry.capacity > 0,
            BotEntry.bot_status == BotStatus.OK.value,
        ]

    def _bot_satisfying_job_clauses(self, job: JobEntry) -> list[ColumnExpressionArgument[bool]]:
        """Base clauses for matching a bot to a job"""
        return [
            self._bot_in_instance_pool_for_name(job.instance_name),
            BotPlatformEntry.platform == job.platform_requirements,
        ]

    def _match_job_to_bot(
        self,
        session: Session,
        job: JobEntry,
        failure_backoff: float,
        bot_assignment_fn: BotAssignmentFn,
        assigner_name: str | None = None,
    ) -> None:
        bot = bot_assignment_fn(session, job)

        # If we failed to find a suitable worker, skip to the next job and
        # add a delay before we reconsider this job for assignment
        if bot is None:
            job.schedule_after = datetime.utcnow() + timedelta(seconds=failure_backoff)
            return

        # Otherwise, continue with the assignment
        self._assign_job_to_bot(session, job, bot)
        # Mark the name of the assigner
        job.assigner_name = assigner_name

    @staticmethod
    def job_by_priority_statement(schedule_after_now: bool = False) -> Select[tuple[JobEntry]]:
        """Selects a job by priority, ordered by priority and queued timestamp"""
        statement = (
            select(JobEntry)
            .with_for_update(skip_locked=True)
            .where(
                JobEntry.assigned != True,  # noqa: E712
                JobEntry.stage == OperationStage.QUEUED.value,
            )
            .order_by(JobEntry.priority, JobEntry.queued_timestamp)
            .limit(1)
        )
        if schedule_after_now:
            statement = statement.where(JobEntry.schedule_after <= datetime.utcnow())
        return statement

    @timed(METRIC.SCHEDULER.ASSIGNMENT_DURATION)
    def assign_job_by_priority(
        self,
        failure_backoff: float = 5.0,
        instance_names: frozenset[str] | None = None,
        bot_assignment_fn: BotAssignmentFn | None = None,
        assigner_name: str | None = None,
    ) -> int:
        """Assigns a job by priority, returning the number of jobs updated"""
        bot_assignment_fn = bot_assignment_fn or self.match_bot_by_capacity
        job_statement = self.job_by_priority_statement(schedule_after_now=True)
        if instance_names:
            job_statement = job_statement.where(
                JobEntry.instance_name.in_(self._instance_names_closure(instance_names))
            )

        updated = False
        with self._sql.session() as session:
            job = session.execute(job_statement).scalar_one_or_none()
            if job is not None:
                self._match_job_to_bot(session, job, failure_backoff, bot_assignment_fn, assigner_name)
                session.flush()
                updated = True
        return 1 if updated else 0

    @timed(METRIC.SCHEDULER.ASSIGNMENT_DURATION)
    def assign_job_by_age(
        self,
        failure_backoff: float = 5.0,
        instance_names: frozenset[str] | None = None,
        bot_assignment_fn: BotAssignmentFn | None = None,
        assigner_name: str | None = None,
    ) -> int:
        """Assigns a job by age, returning the number of jobs updated"""
        bot_assignment_fn = bot_assignment_fn or self.match_bot_by_capacity
        job_statement = (
            select(JobEntry)
            .with_for_update(skip_locked=True)
            .where(
                JobEntry.assigned != True,  # noqa: E712
                JobEntry.stage == OperationStage.QUEUED.value,
                JobEntry.schedule_after <= datetime.utcnow(),
            )
            .order_by(JobEntry.queued_timestamp)
            .limit(1)
        )
        if instance_names:
            job_statement = job_statement.where(
                JobEntry.instance_name.in_(self._instance_names_closure(instance_names))
            )

        updated = False
        with self._sql.session() as session:
            job = session.execute(job_statement).scalar_one_or_none()
            if job is not None:
                self._match_job_to_bot(session, job, failure_backoff, bot_assignment_fn, assigner_name)
                session.flush()
                updated = True
        return 1 if updated else 0

    def get_queue_position(self, operation_name: str, instance_name: str, job_search_limit: int = 300) -> str:
        """Estimates a jobs position in the queue before assignment"""
        # Operation_names of an assigned jobs will return "~0"
        with self._sql.session() as session:
            find_job = select(JobEntry).join(OperationEntry).where(OperationEntry.name == operation_name)
            job = session.execute(find_job).scalar_one_or_none()
            if not job:
                raise NotFoundError(f"Operation {operation_name} not found while getting queue position")

            # Return 0 if the job is not queued
            if job.stage != OperationStage.QUEUED.value:
                return "~0"

            job_priority = job.priority
            job_queued_timestamp = job.queued_timestamp

            # Count should be inclusive of the already found job
            job_queue = (
                select(JobEntry.name)
                .where(
                    JobEntry.assigned != True,  # noqa: E712
                    JobEntry.stage == OperationStage.QUEUED.value,
                    JobEntry.instance_name.in_(self._instance_names_closure(frozenset([instance_name]))),
                    (
                        (JobEntry.priority < job_priority)
                        | ((JobEntry.priority == job_priority) & (JobEntry.queued_timestamp <= job_queued_timestamp))
                    ),
                )
                .limit(job_search_limit)
                .subquery()
            )
            job_queue_count = select(func.count()).select_from(job_queue)
            queue_position = session.execute(job_queue_count).scalar_one()

        if queue_position == job_search_limit:
            return f"{job_search_limit}+"
        return f"~{queue_position}"

    def queue_timer_loop(self, shutdown_requested: threading.Event) -> None:
        """Periodically timeout aged queued jobs"""

        if not (opts := self.queue_timeout_options):
            return

        job_max_age = opts.job_max_age
        period = opts.handling_period
        limit = opts.max_handling_window

        last_timeout_time = datetime.utcnow()
        while not shutdown_requested.is_set():
            now = datetime.utcnow()
            if now - last_timeout_time < period:
                LOGGER.info(f"Job queue timeout thread sleeping for {period} seconds")
                shutdown_requested.wait(timeout=period.total_seconds())
                continue

            timeout_jobs_scheduled_before = now - job_max_age
            try:
                with timer(METRIC.SCHEDULER.QUEUE_TIMEOUT_DURATION):
                    num_timeout = self._timeout_queued_jobs_scheduled_before(timeout_jobs_scheduled_before, limit)
                LOGGER.info(f"Timed-out {num_timeout} queued jobs scheduled before {timeout_jobs_scheduled_before}")
                if num_timeout > 0:
                    publish_counter_metric(METRIC.SCHEDULER.QUEUE_TIMEOUT_COUNT, num_timeout)

            except Exception as e:
                LOGGER.exception("Failed to timeout aged queued jobs.", exc_info=e)
            finally:
                last_timeout_time = now

    def _timeout_queued_jobs_scheduled_before(self, dt: datetime, limit: int) -> int:
        jobs_to_timeout_stmt = (
            select(JobEntry)
            .where(JobEntry.stage == OperationStage.QUEUED.value)
            .where(JobEntry.queued_timestamp < dt)
            .limit(limit)
        )
        return self._batch_timeout_jobs(
            jobs_to_timeout_stmt, code_pb2.UNAVAILABLE, "Operation has been queued for too long"
        )

    def prune_timer_loop(self, shutdown_requested: threading.Event) -> None:
        """Running in a background thread, this method wakes up periodically and deletes older records
        from the jobs tables using configurable parameters"""

        if not (opts := self.pruning_options):
            return

        job_max_age = opts.job_max_age
        pruning_period = opts.handling_period
        limit = opts.max_handling_window

        utc_last_prune_time = datetime.utcnow()
        while not shutdown_requested.is_set():
            utcnow = datetime.utcnow()
            if (utcnow - pruning_period) < utc_last_prune_time:
                LOGGER.info(f"Pruner thread sleeping for {pruning_period}(until {utcnow + pruning_period})")
                shutdown_requested.wait(timeout=pruning_period.total_seconds())
                continue

            delete_before_datetime = utcnow - job_max_age
            try:
                num_rows = self._delete_jobs_prior_to(delete_before_datetime, limit)
                LOGGER.info(f"Pruned {num_rows} row(s) from the jobs table older than {delete_before_datetime}")
            except Exception:
                LOGGER.exception("Caught exception while deleting jobs records.")
            finally:
                # Update even if error occurred to avoid potentially infinitely retrying
                utc_last_prune_time = utcnow

        LOGGER.info("Exiting pruner thread.")

    @timed(METRIC.SCHEDULER.PRUNE_DURATION)
    def _delete_jobs_prior_to(self, delete_before_datetime: datetime, limit: int) -> int:
        """Deletes older records from the jobs tables constrained by `delete_before_datetime` and `limit`"""
        delete_stmt = delete(JobEntry).where(
            JobEntry.name.in_(
                select(JobEntry.name)
                .with_for_update(skip_locked=True)
                .where(JobEntry.worker_completed_timestamp <= delete_before_datetime)
                .limit(limit)
            ),
        )

        with self._sql.session() as session:
            options = {"synchronize_session": "fetch"}
            num_rows_deleted: int = session.execute(delete_stmt, execution_options=options).rowcount

        if num_rows_deleted:
            publish_counter_metric(METRIC.SCHEDULER.PRUNE_COUNT, num_rows_deleted)

        return num_rows_deleted

    def _insert_on_conflict_do_nothing(self, model: type[OrmBase]) -> Insert:
        # `Insert.on_conflict_do_nothing` is a SQLAlchemy "generative method", it
        # returns a modified copy of the statement it is called on. For
        # some reason mypy can't understand this, so the errors are ignored here.
        if self._sql.dialect == "sqlite":
            sqlite_insert: sqlite.Insert = sqlite.insert(model)
            return sqlite_insert.on_conflict_do_nothing()

        elif self._sql.dialect == "postgresql":
            insertion: postgresql.Insert = postgresql.insert(model)
            return insertion.on_conflict_do_nothing()

        else:
            # Fall back to the non-specific insert implementation. This doesn't
            # support `ON CONFLICT DO NOTHING`, so callers need to be careful to
            # still catch IntegrityErrors if other database backends are possible.
            return insert(model)

    def get_or_create_client_identity_in_store(
        self, session: Session, client_id: ClientIdentityEntry
    ) -> ClientIdentityEntry:
        """Get the ClientIdentity in the storage or create one.
        This helper function essentially makes sure the `client_id` is created during the transaction

        Args:
            session (Session): sqlalchemy Session
            client_id (ClientIdentityEntry): identity of the client that creates an operation

        Returns:
            ClientIdentityEntry: identity of the client that creates an operation
        """
        insertion = self._insert_on_conflict_do_nothing(ClientIdentityEntry)
        insertion = insertion.values(
            {
                "instance": client_id.instance,
                "workflow": client_id.workflow,
                "actor": client_id.actor,
                "subject": client_id.subject,
            }
        )
        try:
            session.execute(insertion)

        # Handle unique constraint violation when using an unsupported database (ie. not PostgreSQL or SQLite)
        except IntegrityError:
            LOGGER.debug("Handled IntegrityError when inserting client identity.")

        stmt = (
            select(ClientIdentityEntry)
            .where(ClientIdentityEntry.instance == client_id.instance)
            .where(ClientIdentityEntry.workflow == client_id.workflow)
            .where(ClientIdentityEntry.actor == client_id.actor)
            .where(ClientIdentityEntry.subject == client_id.subject)
        )

        result: ClientIdentityEntry = session.execute(stmt).scalar_one()
        return result

    def get_or_create_request_metadata_in_store(
        self, session: Session, request_metadata: RequestMetadata
    ) -> RequestMetadataEntry:
        insertion = self._insert_on_conflict_do_nothing(RequestMetadataEntry)
        insertion = insertion.values(
            {
                "action_mnemonic": request_metadata.action_mnemonic,
                "configuration_id": request_metadata.configuration_id,
                "correlated_invocations_id": request_metadata.correlated_invocations_id,
                "invocation_id": request_metadata.tool_invocation_id,
                "target_id": request_metadata.target_id,
                "tool_name": request_metadata.tool_details.tool_name,
                "tool_version": request_metadata.tool_details.tool_version,
            }
        )
        try:
            session.execute(insertion)

        # Handle unique constraint violation when using an unsupported database (ie. not PostgreSQL or SQLite)
        except IntegrityError:
            LOGGER.debug("Handled IntegrityError when inserting request metadata.")

        stmt = (
            select(RequestMetadataEntry)
            .where(RequestMetadataEntry.action_mnemonic == request_metadata.action_mnemonic)
            .where(RequestMetadataEntry.configuration_id == request_metadata.configuration_id)
            .where(RequestMetadataEntry.correlated_invocations_id == request_metadata.correlated_invocations_id)
            .where(RequestMetadataEntry.invocation_id == request_metadata.tool_invocation_id)
            .where(RequestMetadataEntry.target_id == request_metadata.target_id)
            .where(RequestMetadataEntry.tool_name == request_metadata.tool_details.tool_name)
            .where(RequestMetadataEntry.tool_version == request_metadata.tool_details.tool_version)
        )

        result: RequestMetadataEntry = session.execute(stmt).scalar_one()
        return result

    def add_bot_entry(
        self,
        *,
        bot_name: str,
        bot_session_id: str,
        bot_session_status: int,
        bot_property_labels: list[str] | None = None,
        bot_capability_hashes: list[str] | None = None,
        bot_capacity: int = 1,
    ) -> str:
        if not bot_property_labels:
            bot_property_labels = ["unknown"]

        if not bot_capability_hashes:
            bot_capability_hashes = [hash_from_dict({})]

        with self._sql.session() as session:
            # Check if bot_id is already known. If yes, all leases associated with
            # it are requeued and the existing record deleted. A new record is then
            # created with the new bot_id/name combination, as it would in the
            # unknown case.
            locate_bot_stmt = (
                select(BotEntry)
                .where(BotEntry.bot_id == bot_session_id, self._bot_in_instance_pool())
                .with_for_update()
            )
            self._close_bot_sessions(session, session.execute(locate_bot_stmt).scalars().all())

            session.add(
                BotEntry(
                    name=bot_name,
                    bot_id=bot_session_id,
                    last_update_timestamp=datetime.utcnow(),
                    lease_id=None,
                    bot_status=bot_session_status,
                    property_labels=[],
                    instance_name=current_instance(),
                    expiry_time=datetime.utcnow() + timedelta(seconds=self.bot_session_keepalive_timeout),
                    capacity=bot_capacity,
                )
            )

            for label in bot_property_labels:
                session.add(PropertyLabelEntry(property_label=label, bot_name=bot_name))

            for capability in bot_capability_hashes:
                session.add(BotPlatformEntry(bot_name=bot_name, platform=capability))

            return bot_name

    def maybe_update_bot_platforms(self, bot_name: str, capability_hashes: list[str] | None = None) -> None:
        if not capability_hashes:
            capability_hashes = [hash_from_dict({})]

        with self._sql.session() as session:
            platforms_stmt = select(func.count(BotPlatformEntry.platform)).where(BotPlatformEntry.bot_name == bot_name)

            platforms = session.execute(platforms_stmt).scalar()
            if not platforms:
                for capability in capability_hashes:
                    session.add(BotPlatformEntry(bot_name=bot_name, platform=capability))

    def close_bot_sessions(self, bot_name: str) -> None:
        with self._sql.session() as session:
            locate_bot_stmt = (
                select(BotEntry).where(BotEntry.name == bot_name, self._bot_in_instance_pool()).with_for_update()
            )
            self._close_bot_sessions(session, session.execute(locate_bot_stmt).scalars().all())

    def _close_bot_sessions(self, session: Session, bots: Sequence[BotEntry]) -> None:
        for bot in bots:
            log_tags = {
                "instance_name": try_current_instance(),
                "request.bot_name": bot.name,
                "request.bot_id": bot.bot_id,
                "request.bot_status": bot.bot_status,
            }
            LOGGER.debug("Closing bot session.", tags=log_tags)
            for job in self._get_incomplete_jobs_for_bot(bot.bot_id, session, with_for_update=True):
                lease_tags = {**log_tags, "db.lease_id": job.name, "db.lease_state": job.lease_state()}
                LOGGER.debug("Reassigning job for bot session.", tags=lease_tags)
                self._retry_job(session, job)
                self._notify_job_updated(job.name, session)
            session.delete(bot)

    def session_expiry_timer_loop(self, shutdown_requested: threading.Event) -> None:
        LOGGER.info("Starting BotSession reaper.", tags=dict(keepalive_timeout=self.bot_session_keepalive_timeout))
        while not shutdown_requested.is_set():
            try:
                while self.reap_expired_sessions():
                    if shutdown_requested.is_set():
                        break
            except Exception as exception:
                LOGGER.exception(exception)
            shutdown_requested.wait(timeout=self.session_expiry_interval)

    def reap_expired_sessions(self) -> bool:
        """
        Find and close expired bot sessions. Returns True if sessions were closed.
        Only closes a few sessions to minimize time in transaction.
        """

        with self._sql.session() as session:
            locate_bot_stmt = (
                select(BotEntry)
                .where(BotEntry.expiry_time < datetime.utcnow())
                .order_by(BotEntry.expiry_time.desc())
                .with_for_update(skip_locked=True)
                .limit(5)
            )
            if bots := cast(list[BotEntry], session.execute(locate_bot_stmt).scalars().all()):
                bots_by_instance: dict[str, list[BotEntry]] = defaultdict(list)
                for bot in bots:
                    LOGGER.warning(
                        "BotSession has expired.",
                        tags=dict(
                            name=bot.name, bot_id=bot.bot_id, instance_name=bot.instance_name, deadline=bot.expiry_time
                        ),
                    )
                    bots_by_instance[bot.instance_name].append(bot)
                for instance_name, instance_bots in bots_by_instance.items():
                    with instance_context(instance_name):
                        self._close_bot_sessions(session, instance_bots)
                return True
            return False

    def _publish_job_duration(
        self,
        start: Timestamp | None,
        end: Timestamp | None,
        state: str,
        property_label: str,
        assigner_name: str | None,
    ) -> None:
        start_set = start is not None and (start.seconds > 0 or start.nanos > 0)
        end_set = end is not None and (end.seconds > 0 or end.nanos > 0)
        if start_set and end_set:
            # The name `Assigner` is an implementation detail, so we use the `assignerName` as the metric tag name.
            publish_timer_metric(
                METRIC.JOB.DURATION,
                end.ToDatetime() - start.ToDatetime(),  # type: ignore[union-attr]
                state=state,
                propertyLabel=property_label,
                schedulerName=assigner_name or "none",
            )

    @timed(METRIC.SCHEDULER.ASSIGNMENT_DURATION)
    def _fetch_job_for_bot(self, session: Session, bot: BotEntry, log_tags: Tags) -> Lease | None:
        # Attempt to fetch a new job for a bot to work on.
        # This can help if there are usually more jobs available than bots.

        if bot.bot_status == BotStatus.OK.value:
            job_statement = self.job_by_priority_statement(schedule_after_now=False)
            job_statement = job_statement.where(self._job_in_instance_pool()).where(
                JobEntry.platform_requirements.in_(p.platform for p in bot.platforms)
            )
            if next_job := session.execute(job_statement).scalar_one_or_none():
                log_tags["db.next_job_name"] = next_job.name
                self._assign_job_to_bot(session, next_job, bot)
                self._create_logstream_for_job(next_job, log_tags)
                self._notify_job_updated(next_job.name, session)
                LOGGER.info("Fetched next job for bot proactively.", tags=log_tags)
                return next_job.to_lease_proto()
        return None

    def _create_logstream_for_job(self, job: JobEntry, log_tags: Tags) -> None:
        if self.logstream_channel and self.logstream_instance is not None:
            try:
                action_digest = string_to_digest(job.action_digest)
                parent_base = f"{action_digest.hash}_{action_digest.size_bytes}_{int(time())}"
                with logstream_client(self.logstream_channel, self.logstream_instance) as ls_client:
                    stdout_stream = ls_client.create(f"{parent_base}_stdout")
                    stderr_stream = ls_client.create(f"{parent_base}_stderr")
                job.stdout_stream_name = stdout_stream.name
                job.stdout_stream_write_name = stdout_stream.write_resource_name
                job.stderr_stream_name = stderr_stream.name
                job.stderr_stream_write_name = stderr_stream.write_resource_name
            except Exception as e:
                LOGGER.warning("Failed to create log stream.", tags=log_tags, exc_info=e)

    @timed(METRIC.SCHEDULER.SYNCHRONIZE_DURATION)
    def synchronize_bot_leases(
        self,
        bot_name: str,
        bot_id: str,
        bot_status: int,
        bot_session_leases: Sequence[Lease],
        partial_execution_metadata: dict[str, ExecutedActionMetadata] | None = None,
        max_capacity: int = 1,
    ) -> list[Lease]:
        log_tags = {
            "instance_name": try_current_instance(),
            "request.bot_id": bot_id,
            "request.bot_status": bot_status,
            "request.bot_name": bot_name,
            "request.leases": {lease.id: lease.state for lease in bot_session_leases},
            "request.capacity": max_capacity,
        }

        with self._sql.session(exceptions_to_not_raise_on=[Exception]) as session:
            locate_bot_stmt = (
                select(BotEntry).where(BotEntry.bot_id == bot_id, self._bot_in_instance_pool()).with_for_update()
            )
            bots: Sequence[BotEntry] = session.execute(locate_bot_stmt).scalars().all()
            if not bots:
                raise InvalidArgumentError(f"Bot does not exist while validating leases. {log_tags}")

            # This is a tricky case. This case happens when a new bot session is created while an older
            # session for a bot id is waiting on leases. This can happen when a worker reboots but the
            # connection context takes a long time to close. In this case, we DO NOT want to update anything
            # in the database, because the work/lease has already been re-assigned to a new session.
            # Closing anything in the database at this point would cause the newly restarted worker
            # to get cancelled prematurely.
            if len(bots) == 1 and bots[0].name != bot_name:
                raise BotSessionMismatchError(
                    "Mismatch between client supplied bot_id/bot_name and buildgrid database record. "
                    f"db.bot_name=[{bots[0].name}] {log_tags}"
                )

            # Everything at this point is wrapped in try/catch, so we can raise BotSessionMismatchError or
            # BotSessionClosedError and have the session be closed if preconditions from here out fail.
            try:
                # There should never be time when two bot sessions exist for the same bot id. We have logic to
                # assert that old database entries for a given bot id are closed and deleted prior to making a
                # new one. If this case happens shut everything down, so we can hopefully recover.
                if len(bots) > 1:
                    raise BotSessionMismatchError(
                        "Bot id is registered to more than one bot session. "
                        f"names=[{', '.join(bot.name for bot in bots)}] {log_tags}"
                    )

                bot = bots[0]

                bot_jobs_stmt = select(JobEntry).where(
                    JobEntry.worker_name == bot_id,
                    JobEntry.stage < OperationStage.COMPLETED.value,
                    self._job_in_instance_pool(),
                )
                jobs: Sequence[JobEntry] = session.execute(bot_jobs_stmt).scalars().all()
                db_lease_ids = set(job.name for job in jobs)
                log_tags["db.leases"] = {job.name: job.lease_state() for job in jobs}

                # Update the expiry time.
                bot.expiry_time = datetime.utcnow() + timedelta(seconds=self.bot_session_keepalive_timeout)
                bot.last_update_timestamp = datetime.utcnow()
                bot.bot_status = bot_status

                # If there's no lease in the database or session, all we have to update is the bot capacity.
                if not db_lease_ids and not bot_session_leases:
                    LOGGER.debug("No lease in session or database.", tags=log_tags)

                    # Try to fill this bot's capacity with jobs
                    leases: list[Lease] = []
                    while len(leases) < max_capacity:
                        if lease := self._fetch_job_for_bot(session, bot, log_tags):
                            leases.append(lease)
                        else:
                            # Failed to immediately assign a job, give up and leave the rest of our
                            # capacity for the assigner threads.
                            break

                    bot.capacity = max_capacity - len(leases)
                    return leases

                synchronized_leases = []

                # Synchronize contents of BotSession
                #
                #   We start by synchronizing the state of the leases in our current BotSession with the database.
                #   This is where we handle state transitions for leases that have already been assigned.
                #
                for lease in bot_session_leases:
                    # Set specific tags in log lines for the lease currently being synchronized.
                    # This can help to identify a problematic lease in logs for a bot with multiple leases assigned.
                    lease_tags = {**log_tags, "request.lease_id": lease.id, "request.lease_state": lease.state}

                    # If the database has no lease, but the work is completed, we probably timed out the last call.
                    if lease.id not in db_lease_ids and lease.state == LeaseState.COMPLETED.value:
                        LOGGER.debug(
                            "No lease in database, but session lease is completed. Skipping.", tags=lease_tags
                        )
                        continue

                    # Remove this lease ID from db_lease_ids if present, now that we know we're handling it.
                    # If not present, then either the job has been cancelled or something has gone very wrong.
                    if lease.id in db_lease_ids:
                        db_lease_ids.remove(lease.id)

                    # Let's now lock the job so no more state transitions occur while we perform our updates.
                    job = self._get_job(lease.id, session, with_for_update=True)
                    if not job:
                        # Something has gone very wrong if we have a lease ID that isn't in the database.
                        raise BotSessionClosedError(f"Bot session lease id points to non-existent job. {lease_tags}")

                    lease_tags["db.lease_id"] = job.name
                    lease_tags["db.lease_state"] = job.lease_state()

                    # Update Partial Execution Metadata:
                    #
                    #   Update the job table in the database with the partial execution metadata from the worker.
                    #   This is included in the UpdateBotSession GRPC call and should contain partial execution metadata
                    #   for each lease. The job.name is the same as the lease_id.
                    #
                    if partial_execution_metadata:
                        if metadata := partial_execution_metadata.get(job.name):
                            if metadata.HasField("input_fetch_start_timestamp"):
                                job.input_fetch_start_timestamp = metadata.input_fetch_start_timestamp.ToDatetime()
                            if metadata.HasField("input_fetch_completed_timestamp"):
                                job.input_fetch_completed_timestamp = (
                                    metadata.input_fetch_completed_timestamp.ToDatetime()
                                )
                            if metadata.HasField("output_upload_start_timestamp"):
                                job.output_upload_start_timestamp = metadata.output_upload_start_timestamp.ToDatetime()
                            if metadata.HasField("output_upload_completed_timestamp"):
                                job.output_upload_completed_timestamp = (
                                    metadata.output_upload_completed_timestamp.ToDatetime()
                                )
                            if metadata.HasField("execution_start_timestamp"):
                                job.execution_start_timestamp = metadata.execution_start_timestamp.ToDatetime()
                            if metadata.HasField("execution_completed_timestamp"):
                                job.execution_completed_timestamp = metadata.execution_completed_timestamp.ToDatetime()

                    # At this point, we know that there's a lease both in the bot session and in the database.

                    # Accept:
                    #
                    #   If the lease is in the PENDING state, this means that it is a new lease for the worker,
                    #   which it must acknowledge (the next time it calls UpdateBotSession) by changing the state
                    #   to ACTIVE
                    #
                    if lease.state == LeaseState.ACTIVE.value and job.lease_state() == LeaseState.PENDING.value:
                        # A job is only considered to be "EXECUTING" when the Lease has been accepted by the worker.
                        job.stage = OperationStage.EXECUTING.value
                        self._notify_job_updated(job.name, session)
                        LOGGER.debug("Bot acked pending lease.", tags=lease_tags)

                        # Now the job has been accepted by a worker the time this job has spent in the queue can be
                        # calculated and posted to the metrics.
                        job_metadata = self.get_execute_action_metadata(job)
                        queued = job_metadata.queued_timestamp
                        worker_start = job_metadata.worker_start_timestamp
                        self._publish_job_duration(
                            queued, worker_start, "Queued", job.property_label, job.assigner_name
                        )

                        synchronized_leases.append(lease)
                        continue

                    # Complete:
                    #
                    #   Once the assignment is complete - either because it finishes or because it times out - the bot
                    #   calls Bots.UpdateBotSession again, this time updating the state of the lease from accepted to
                    #   complete, and optionally by also populating the lease’s results field, which is another Any
                    #   proto. The service can then assign it new work (removing any completed leases).
                    #
                    #   A successfully completed lease may go directly from PENDING to COMPLETED if, for example, the
                    #   lease was completed before the bot has had the opportunity to transition to ACTIVE, or if the
                    #   update transitioning the lease to the ACTIVE state was lost.
                    #
                    if lease.state == LeaseState.COMPLETED.value and job.lease_state() in (
                        LeaseState.PENDING.value,
                        LeaseState.ACTIVE.value,
                    ):
                        completion_tags = {
                            **lease_tags,
                            "request.lease_status_code": lease.status.code,
                            "request.lease_status_message": lease.status.message,
                            "db.n_tries": job.n_tries,
                        }

                        bot.lease_id = None
                        if lease.status.code in self.RETRYABLE_STATUS_CODES and job.n_tries < self.max_job_attempts:
                            LOGGER.debug("Retrying bot lease.", tags=completion_tags)
                            self._retry_job(session, job)
                        else:
                            LOGGER.debug("Bot completed lease.", tags=completion_tags)
                            self._complete_job(session, job, lease.status, bot_name=bot.name, result=lease.result)

                        self._notify_job_updated(job.name, session)
                        continue

                    # Cancel:
                    #
                    #   At any time, the service may change the state of a lease from PENDING or ACTIVE to CANCELLED;
                    #   the bot may not change to this state. The service then waits for the bot to acknowledge the
                    #   change by updating its own status to CANCELLED as well. Once both the service and the bot agree,
                    #   the service may remove it from the list of leases.
                    #
                    if lease.state == job.lease_state() == LeaseState.CANCELLED.value:
                        bot.lease_id = None
                        LOGGER.debug("Bot acked cancelled lease.", tags=lease_tags)
                        continue

                    if job.lease_state() == LeaseState.CANCELLED.value:
                        lease.state = LeaseState.CANCELLED.value
                        LOGGER.debug("Cancelled lease sent to bot for ack.", tags=lease_tags)
                        synchronized_leases.append(lease)
                        continue

                    if lease.state == LeaseState.CANCELLED.value:
                        raise BotSessionClosedError(
                            f"Illegal attempt from session to set state as cancelled. {lease_tags}"
                        )

                    # Keepalive:
                    #
                    #   The Bot periodically calls Bots.UpdateBotSession, either if there’s a genuine change (for
                    #   example, an attached phone has died) or simply to let the service know that it’s alive and
                    #   ready to receive work. If the bot doesn’t call back on time, the service considers it to have
                    #   died, and all work from the bot to be lost.
                    #
                    if lease.state == job.lease_state():
                        LOGGER.debug("Bot heartbeat acked.", tags=lease_tags)
                        synchronized_leases.append(lease)
                        continue

                    # Any other transition should really never happen... cover it anyways.
                    raise BotSessionClosedError(f"Unsupported lease state transition. {lease_tags}")

                # Add newly assigned leases
                #
                #   At this point we know that anything we've not yet handled is a newly assigned job.
                #   We can now iterate over these and generate leases for them.
                #
                for job_name in db_lease_ids:
                    job = self._get_job(job_name, session, with_for_update=True)
                    if not job:
                        # For some reason the job has disappeared between the last query and now, so skip it.
                        continue

                    log_tags["db.lease_id"] = job.name
                    log_tags["db.lease_state"] = job.lease_state()

                    # Assign:
                    #
                    #   If the lease is in the PENDING state, this means that it is a new lease for the worker, which
                    #   it must acknowledge (the next time it calls UpdateBotSession) by changing the state to ACTIVE.
                    #
                    #   Leases contain a “payload,” which is an Any proto that must be understandable to the bot.
                    #
                    #   If at any time the bot issues a call to UpdateBotSession that is inconsistent with what the
                    #   service expects, the service can take appropriate action. For example, the service may have
                    #   assigned a lease to a bot, but the call gets interrupted before the bot receives the message,
                    #   perhaps because the UpdateBotSession call times out. As a result, the next call to
                    #   UpdateBotSession from the bot will not include the lease, and the service can immediately
                    #   conclude that the lease needs to be reassigned.
                    #
                    if job.lease_state() != LeaseState.PENDING.value:
                        raise BotSessionClosedError(f"Non-pending lease is missing from the BotSession. {log_tags}")

                    self._create_logstream_for_job(job, log_tags)
                    self._notify_job_updated(job.name, session)
                    LOGGER.debug("Pending lease sent to bot for ack.", tags=log_tags)

                    synchronized_leases.append(job.to_lease_proto())

                while len(synchronized_leases) < max_capacity:
                    if lease := self._fetch_job_for_bot(session, bot, log_tags):
                        synchronized_leases.append(lease)
                    else:
                        # If there was no job to immediately fetch, give up trying
                        # and let an assigner thread handle the rest of our capacity.
                        break

                bot.capacity = max_capacity - len(synchronized_leases)
                return synchronized_leases
            # TODO allow creating a session with manual commit logic.
            # For now... Sneak the exception past the context manager.
            except (BotSessionMismatchError, BotSessionClosedError) as e:
                self._close_bot_sessions(session, bots)
                err = e
        raise err

    def _retry_job(self, session: Session, job: JobEntry) -> None:
        # If the job was mutated before we could lock it, exit fast on terminal states.
        if job.cancelled or job.stage == OperationStage.COMPLETED.value:
            return

        if job.n_tries >= self.max_job_attempts:
            status = status_pb2.Status(
                code=code_pb2.ABORTED, message=f"Job was retried {job.n_tries} unsuccessfully. Aborting."
            )
            self._complete_job(session, job, status=status)
            return

        job.stage = OperationStage.QUEUED.value
        job.assigned = False
        job.n_tries += 1
        job.worker_name = None

    def _complete_job(
        self,
        session: Session,
        job: JobEntry,
        status: Status,
        bot_name: str | None = None,
        result: ProtoAny | None = None,
    ) -> None:
        job.stage = OperationStage.COMPLETED.value
        job.status_code = status.code
        if not job.do_not_cache:
            job.do_not_cache = status.code != code_pb2.OK
        job.worker_completed_timestamp = datetime.utcnow()

        action_result = ActionResult()
        if result is not None and result.Is(action_result.DESCRIPTOR):
            result.Unpack(action_result)
        now = datetime.utcnow()
        action_result.execution_metadata.queued_timestamp.FromDatetime(job.queued_timestamp)
        action_result.execution_metadata.worker_start_timestamp.FromDatetime(job.worker_start_timestamp or now)
        action_result.execution_metadata.worker_completed_timestamp.FromDatetime(job.worker_completed_timestamp or now)
        response = ExecuteResponse(result=action_result, cached_result=False, status=status)

        job.result = digest_to_string(self.storage.put_message(response))

        if self.action_cache and result and not job.do_not_cache:
            action_digest = string_to_digest(job.action_digest)
            try:
                self.action_cache.update_action_result(action_digest, action_result)
                LOGGER.debug(
                    "Stored action result in ActionCache.",
                    tags=dict(action_result=action_result, digest=action_digest),
                )
            except UpdateNotAllowedError:
                # The configuration doesn't allow updating the old result
                LOGGER.exception(
                    "ActionCache is not configured to allow updates, ActionResult wasn't updated.",
                    tags=dict(digest=action_digest),
                )
            except Exception:
                LOGGER.exception(
                    "Unable to update ActionCache, results will not be stored in the ActionCache.",
                    tags=dict(digest=action_digest),
                )
        # Record locality hint if job completed successfully and has both locality_hint and worker_name
        if status.code == code_pb2.OK and job.locality_hint and bot_name:
            try:
                LOGGER.debug(
                    "Recording bot locality hint.",
                    tags=dict(job_name=job.name, bot_name=bot_name, locality_hint=job.locality_hint),
                )
                self._record_bot_locality_hint(session, bot_name, job.locality_hint)
            except Exception:
                # Don't fail job completion if locality hint recording fails
                LOGGER.warning(
                    "Failed to record bot locality hint.",
                    tags=dict(job_name=job.name, bot_name=bot_name, locality_hint=job.locality_hint),
                    exc_info=True,
                )

        # Update retentions
        self._update_action_retention(
            Action.FromString(job.action),
            string_to_digest(job.action_digest),
            retention_hours=self.completed_action_retention_hours,
        )
        if action_result.ByteSize() > 0:
            self._update_action_result_retention(action_result, retention_hours=self.action_result_retention_hours)

        self._publish_execution_stats(
            session, job.name, action_result.execution_metadata, job.property_label, job.assigner_name
        )

    def get_bot_status_metrics(self) -> BotMetrics:
        """Count the number of bots with a particular status and property_label"""
        with self._sql.session() as session:
            metrics: BotMetrics = {"bots_total": {}, "bots_per_property_label": {}}

            # bot count by status only
            query_total = (
                session.query(BotEntry.bot_status, func.count(BotEntry.bot_status))
                .group_by(BotEntry.bot_status)
                .filter(self._bot_in_instance_pool())
            )
            for status in BotStatus:
                metrics["bots_total"][status] = 0
            for [bot_status, count] in query_total.all():
                metrics["bots_total"][BotStatus(bot_status)] = cast(int, count)

            # bot count by status for each property label
            query_per_label = (
                session.query(BotEntry.bot_status, PropertyLabelEntry.property_label, func.count(BotEntry.bot_status))
                .join(BotEntry, BotEntry.name == PropertyLabelEntry.bot_name, isouter=True)
                .group_by(BotEntry.bot_status, PropertyLabelEntry.property_label)
                .filter(self._bot_in_instance_pool())
            )
            for status in BotStatus:
                metrics["bots_per_property_label"][status, "unknown"] = 0
            for [bot_status, property_label, count] in query_per_label.all():
                metrics["bots_per_property_label"][BotStatus(bot_status), property_label] = cast(int, count)

            return metrics

    def refresh_bot_expiry_time(self, bot_name: str, bot_id: str) -> datetime:
        """
        This update is done out-of-band from the main synchronize_bot_lease transaction, as there
        are cases where we will skip calling the synchronization, but still want the session to be
        updated such that it does not get reaped. This slightly duplicates the update happening in
        synchronize_bot_lease, however, that update is still required to not have the job reaped
        during its job assignment waiting period.

        This method should be called at the end of the update and create bot session methods.
        The returned datetime should be assigned to the deadline within the returned session proto.
        """

        locate_bot_stmt = (
            select(BotEntry)
            .where(BotEntry.name == bot_name, BotEntry.bot_id == bot_id, self._bot_in_instance_pool())
            .with_for_update()
        )
        with self._sql.session() as session:
            if bot := session.execute(locate_bot_stmt).scalar():
                now = datetime.utcnow()
                bot.last_update_timestamp = now
                bot.expiry_time = now + timedelta(seconds=self.bot_session_keepalive_timeout)
                return bot.expiry_time
        raise BotSessionClosedError("Bot not found to fetch expiry. {bot_name=} {bot_id=}")

    def get_metadata_for_leases(self, leases: Iterable[Lease]) -> list[tuple[str, bytes]]:
        """Return a list of Job metadata for a given list of leases.

        Args:
            leases (list): List of leases to get Job metadata for.

        Returns:
            List of tuples of the form
            ``('executeoperationmetadata-bin': serialized_metadata)``.

        """
        metadata = []
        with self._sql_ro.session() as session:
            for lease in leases:
                job = self._get_job(lease.id, session)
                if job is not None:
                    job_metadata = ExecuteOperationMetadata(
                        stage=job.stage,  # type: ignore[arg-type]
                        action_digest=string_to_digest(job.action_digest),
                        stderr_stream_name=job.stderr_stream_write_name or "",
                        stdout_stream_name=job.stdout_stream_write_name or "",
                        partial_execution_metadata=self.get_execute_action_metadata(job),
                    )
                    metadata.append(("executeoperationmetadata-bin", job_metadata.SerializeToString()))

        return metadata

    def get_execute_action_metadata(self, job: JobEntry) -> ExecutedActionMetadata:
        worker_name = job.worker_name or ""

        metadata = ExecutedActionMetadata(worker=worker_name)

        def assign_timestamp(field: Timestamp, timestamp: datetime | None) -> None:
            if timestamp is not None:
                field.FromDatetime(timestamp)

        assign_timestamp(metadata.queued_timestamp, job.queued_timestamp)
        assign_timestamp(metadata.worker_start_timestamp, job.worker_start_timestamp)
        assign_timestamp(metadata.worker_completed_timestamp, job.worker_completed_timestamp)
        assign_timestamp(metadata.input_fetch_start_timestamp, job.input_fetch_start_timestamp)
        assign_timestamp(metadata.input_fetch_completed_timestamp, job.input_fetch_completed_timestamp)
        assign_timestamp(metadata.output_upload_start_timestamp, job.output_upload_start_timestamp)
        assign_timestamp(metadata.output_upload_completed_timestamp, job.output_upload_completed_timestamp)
        assign_timestamp(metadata.execution_start_timestamp, job.execution_start_timestamp)
        assign_timestamp(metadata.execution_completed_timestamp, job.execution_completed_timestamp)

        return metadata

    def _fetch_execution_stats(
        self, auxiliary_metadata: RepeatedCompositeFieldContainer[ProtoAny]
    ) -> ExecutionStatistics | None:
        """Fetch ExecutionStatistics from Storage
        ProtoAny[Digest] -> ProtoAny[ExecutionStatistics]
        """
        for aux_metadata_any in auxiliary_metadata:
            # Get the wrapped digest
            if not aux_metadata_any.Is(Digest.DESCRIPTOR):
                continue
            aux_metadata_digest = Digest()
            try:
                aux_metadata_any.Unpack(aux_metadata_digest)
                # Get the blob from CAS
                execution_stats_any = self.storage.get_message(aux_metadata_digest, ProtoAny)
                # Get the wrapped ExecutionStatistics
                if execution_stats_any and execution_stats_any.Is(ExecutionStatistics.DESCRIPTOR):
                    execution_stats = ExecutionStatistics()
                    execution_stats_any.Unpack(execution_stats)
                    return execution_stats
            except Exception as exc:
                LOGGER.exception(
                    "Cannot fetch ExecutionStatistics from storage.",
                    tags=dict(auxiliary_metadata=aux_metadata_digest),
                    exc_info=exc,
                )
                return None
        return None

    def publish_execution_stats(
        self,
        job_name: str,
        execution_metadata: ExecutedActionMetadata,
        property_label: str = "unknown",
        assigner_name: str | None = None,
    ) -> None:
        with self._sql_ro.session(expire_on_commit=False) as session:
            self._publish_execution_stats(session, job_name, execution_metadata, property_label, assigner_name)

    def _publish_execution_stats(
        self,
        session: Session,
        job_name: str,
        execution_metadata: ExecutedActionMetadata,
        property_label: str,
        assigner_name: str | None,
    ) -> None:
        """Publish resource usage of the job"""
        queued = execution_metadata.queued_timestamp
        worker_start = execution_metadata.worker_start_timestamp
        worker_completed = execution_metadata.worker_completed_timestamp
        fetch_start = execution_metadata.input_fetch_start_timestamp
        fetch_completed = execution_metadata.input_fetch_completed_timestamp
        execution_start = execution_metadata.execution_start_timestamp
        execution_completed = execution_metadata.execution_completed_timestamp
        upload_start = execution_metadata.output_upload_start_timestamp
        upload_completed = execution_metadata.output_upload_completed_timestamp

        self._publish_job_duration(queued, worker_completed, "Total", property_label, assigner_name)
        # The Queued time is missing here as it's posted as soon as worker has accepted the job.
        self._publish_job_duration(worker_start, worker_completed, "Worker", property_label, assigner_name)
        self._publish_job_duration(fetch_start, fetch_completed, "Fetch", property_label, assigner_name)
        self._publish_job_duration(execution_start, execution_completed, "Execution", property_label, assigner_name)
        self._publish_job_duration(upload_start, upload_completed, "Upload", property_label, assigner_name)

        if self.metering_client is None or len(execution_metadata.auxiliary_metadata) == 0:
            return

        execution_stats = self._fetch_execution_stats(execution_metadata.auxiliary_metadata)
        if execution_stats is None:
            return
        usage = Usage(
            computing=ComputingUsage(
                utime=execution_stats.command_rusage.utime.ToMilliseconds(),
                stime=execution_stats.command_rusage.stime.ToMilliseconds(),
                maxrss=execution_stats.command_rusage.maxrss,
                inblock=execution_stats.command_rusage.inblock,
                oublock=execution_stats.command_rusage.oublock,
            )
        )

        try:
            operations = (
                session.query(OperationEntry)
                .where(OperationEntry.job_name == job_name)
                .options(joinedload(OperationEntry.client_identity))
                .all()
            )
            for op in operations:
                if op.client_identity is None:
                    continue
                client_id = Identity(
                    instance=op.client_identity.instance,
                    workflow=op.client_identity.workflow,
                    actor=op.client_identity.actor,
                    subject=op.client_identity.subject,
                )
                self.metering_client.put_usage(identity=client_id, operation_name=op.name, usage=usage)
        except Exception as exc:
            LOGGER.exception("Cannot publish resource usage.", tags=dict(job_name=job_name), exc_info=exc)

    def _update_action_retention(self, action: Action, action_digest: Digest, retention_hours: float | None) -> None:
        if not self.asset_client or not retention_hours:
            return
        uri = DIGEST_URI_TEMPLATE.format(digest_hash=action_digest.hash)
        qualifier = {"resource_type": PROTOBUF_MEDIA_TYPE}
        expire_at = datetime.now() + timedelta(hours=retention_hours)
        referenced_blobs = [action.command_digest]
        referenced_directories = [action.input_root_digest]

        try:
            self.asset_client.push_blob(
                uris=[uri],
                qualifiers=qualifier,
                blob_digest=action_digest,
                expire_at=expire_at,
                referenced_blobs=referenced_blobs,
                referenced_directories=referenced_directories,
            )
            LOGGER.debug(
                "Extended the retention of action.", tags=dict(digest=action_digest, retention_hours=retention_hours)
            )
        except Exception:
            LOGGER.exception("Failed to push action as an asset.", tags=dict(digest=action_digest))
            # Not a fatal path, don't reraise here

    def _update_action_result_retention(self, action_result: ActionResult, retention_hours: float | None) -> None:
        if not self.asset_client or not retention_hours:
            return
        digest = None
        try:
            # BuildGrid doesn't store action_result in CAS, but if we push it as an asset
            # we need it to be accessible
            digest = self.storage.put_message(action_result)

            uri = DIGEST_URI_TEMPLATE.format(digest_hash=digest.hash)
            qualifier = {"resource_type": PROTOBUF_MEDIA_TYPE}
            expire_at = datetime.now() + timedelta(hours=retention_hours)

            referenced_blobs: list[Digest] = []
            referenced_directories: list[Digest] = []

            for file in action_result.output_files:
                referenced_blobs.append(file.digest)
            for dir in action_result.output_directories:
                # Caveat: the underlying directories referenced by this `Tree` message are not referenced by this asset.
                # For clients who need to keep all referenced outputs,
                # consider setting `Action.output_directory_format` as `DIRECTORY_ONLY` or `TREE_AND_DIRECTORY`.
                if dir.tree_digest.ByteSize() != 0:
                    referenced_blobs.append(dir.tree_digest)
                if dir.root_directory_digest.ByteSize() != 0:
                    referenced_directories.append(dir.root_directory_digest)

            if action_result.stdout_digest.ByteSize() != 0:
                referenced_blobs.append(action_result.stdout_digest)
            if action_result.stderr_digest.ByteSize() != 0:
                referenced_blobs.append(action_result.stderr_digest)

            self.asset_client.push_blob(
                uris=[uri],
                qualifiers=qualifier,
                blob_digest=digest,
                expire_at=expire_at,
                referenced_blobs=referenced_blobs,
                referenced_directories=referenced_directories,
            )
            LOGGER.debug(
                "Extended the retention of action result.", tags=dict(digest=digest, retention_hours=retention_hours)
            )

        except Exception as e:
            LOGGER.exception("Failed to push action_result as an asset.", tags=dict(digest=digest), exc_info=e)
            # Not a fatal path, don't reraise here

    def _record_bot_locality_hint(self, session: Session, bot_name: str, locality_hint: str) -> None:
        """
        Record a locality hint for a bot and cleanup old hints beyond the limit.
        """
        if self.bot_locality_hint_limit == 0:
            return

        # Insert new hint with dialect-specific seq handling
        if self._sql.dialect == "postgresql":
            # For PostgreSQL, use the sequence to get the next seq number
            next_seq = None
        else:
            # For SQLite, manually find the max seq number
            max_seq = session.execute(
                select(func.coalesce(func.max(BotLocalityHintEntry.sequence_number), 0)).where(
                    BotLocalityHintEntry.bot_name == bot_name
                )
            ).scalar_one()
            next_seq = max_seq + 1

        new_hint = BotLocalityHintEntry(
            bot_name=bot_name,
            locality_hint=locality_hint,
            sequence_number=next_seq,
        )
        session.add(new_hint)
        session.flush()

        # Cleanup old hints (keep only K most recent)
        k_th_seq = (
            session.execute(
                select(BotLocalityHintEntry.sequence_number)
                .where(BotLocalityHintEntry.bot_name == bot_name)
                .order_by(BotLocalityHintEntry.sequence_number.desc())
                .offset(self.bot_locality_hint_limit - 1)  # Offset to get the K most recent
                .limit(1)
            )
            .scalars()
            .one_or_none()
        )

        if k_th_seq is not None:
            # Delete all hints older than the K-th most recent
            session.execute(
                delete(BotLocalityHintEntry).where(
                    BotLocalityHintEntry.bot_name == bot_name, BotLocalityHintEntry.sequence_number < k_th_seq
                )
            )
