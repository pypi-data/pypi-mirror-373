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


import datetime
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator
from unittest import mock

import grpc
import pytest
from buildgrid_metering.client.exceptions import MeteringServiceHTTPError
from flaky import flaky
from google.protobuf.any_pb2 import Any as ProtoAny
from google.protobuf.duration_pb2 import Duration
from sqlalchemy import select

from buildgrid._protos.build.bazel.remote.asset.v1.remote_asset_pb2_grpc import add_PushServicer_to_server
from buildgrid._protos.build.bazel.remote.execution.v2 import remote_execution_pb2
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    Action,
    Digest,
    ExecuteOperationMetadata,
    ExecuteResponse,
)
from buildgrid._protos.build.buildbox.execution_stats_pb2 import ExecutionStatistics
from buildgrid._protos.build.buildgrid.scheduling_pb2 import SchedulingMetadata
from buildgrid._protos.google.rpc import code_pb2
from buildgrid._protos.google.rpc.status_pb2 import Status
from buildgrid.server.actioncache.caches.lru_cache import LruActionCache
from buildgrid.server.cas.storage import lru_memory_cache
from buildgrid.server.cas.storage.storage_abc import create_write_session
from buildgrid.server.client.asset import AssetClient
from buildgrid.server.context import instance_context
from buildgrid.server.controller import ExecutionController
from buildgrid.server.enums import BotStatus, LeaseState, OperationStage
from buildgrid.server.exceptions import InvalidArgumentError, NotFoundError, ResourceExhaustedError, StorageFullError
from buildgrid.server.scheduler import PropertySet, Scheduler
from buildgrid.server.scheduler.assigner import (
    AssignByCapacity,
    AssignByLocality,
    SamplingConfig,
    create_bot_assignment_fn,
)
from buildgrid.server.sql.models import (
    Base,
    BotEntry,
    BotLocalityHintEntry,
    ClientIdentityEntry,
    JobEntry,
    OperationEntry,
    digest_to_string,
    string_to_digest,
)
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.server.utils.digests import create_digest
from tests.utils.fixtures import mock_logstream_client, pg_schema_provider
from tests.utils.server import MockAssetPushServicer
from tests.utils.utils import find_free_port, generate_bot_name

server = mock.create_autospec(grpc.Server)

command = remote_execution_pb2.Command()
command_digest = create_digest(command.SerializeToString())

action = remote_execution_pb2.Action(command_digest=command_digest, do_not_cache=False)
action_digest = create_digest(action.SerializeToString())

uncacheable_action = remote_execution_pb2.Action(command_digest=command_digest, do_not_cache=True)
uncacheable_action_digest = create_digest(uncacheable_action.SerializeToString())


@pytest.fixture
def asset_service_remote() -> str:
    return f"localhost:{find_free_port()}"


@pytest.fixture
def push_service(asset_service_remote: str) -> Iterator[MockAssetPushServicer]:
    server = grpc.server(thread_pool=ThreadPoolExecutor())
    push = MockAssetPushServicer()
    add_PushServicer_to_server(push, server)
    server.add_insecure_port(asset_service_remote)
    server.start()

    try:
        yield push
    finally:
        server.stop(grace=None)


@pytest.fixture
def asset_service_channel(asset_service_remote: str) -> Iterator[grpc.Channel]:
    with grpc.insecure_channel(asset_service_remote) as channel:
        yield channel


@pytest.fixture
def asset_client(push_service, asset_service_channel: grpc.Channel) -> Iterator[AssetClient]:
    yield AssetClient(asset_service_channel, instance_name="asset")


PARAMS = ["action-cache", "no-action-cache"]


@pytest.fixture(params=PARAMS)
def controller(request, asset_client: AssetClient, common_props: PropertySet):
    use_cache = request.param
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    db = tempfile.NamedTemporaryFile().name
    sql_provider = SqlProvider(connection_string=f"sqlite:///{db}")

    # Create database tables
    Base.metadata.create_all(sql_provider._engine)

    with create_write_session(command_digest) as write_session:
        write_session.write(command.SerializeToString())
        storage.commit_write(command_digest, write_session)

    with create_write_session(action_digest) as write_session:
        write_session.write(action.SerializeToString())
        storage.commit_write(action_digest, write_session)

    if use_cache == "action-cache":
        cache = LruActionCache(storage, 50)
        scheduler = Scheduler(
            sql_provider,
            storage,
            poll_interval=0.01,
            action_cache=cache,
            property_set=common_props,
            asset_client=asset_client,
            queued_action_retention_hours=12,
            completed_action_retention_hours=1,
            action_result_retention_hours=3,
        )
    else:
        scheduler = Scheduler(
            sql_provider,
            storage,
            poll_interval=0.01,
            property_set=common_props,
            asset_client=asset_client,
            queued_action_retention_hours=12,
            completed_action_retention_hours=1,
            action_result_retention_hours=3,
        )

    with scheduler, instance_context("sql"):
        yield ExecutionController(scheduler)


PARAMS_MAX_EXECUTION = [None, 0.1, 2]


@pytest.fixture(params=PARAMS_MAX_EXECUTION)
def controller_max_execution_timeout(request, common_props):
    max_execution_timeout = request.param
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    db = tempfile.NamedTemporaryFile().name
    sql_provider = SqlProvider(connection_string=f"sqlite:///{db}")

    # Create database tables
    Base.metadata.create_all(sql_provider._engine)

    with create_write_session(command_digest) as write_session:
        write_session.write(command.SerializeToString())
        storage.commit_write(command_digest, write_session)

    with create_write_session(action_digest) as write_session:
        write_session.write(action.SerializeToString())
        storage.commit_write(action_digest, write_session)

    scheduler = Scheduler(
        sql_provider,
        storage,
        poll_interval=0.1,
        execution_timer_interval=0.1,
        property_set=common_props,
        max_execution_timeout=max_execution_timeout,
    )
    controller = ExecutionController(scheduler)
    assert controller.execution_instance is not None
    with controller.execution_instance, instance_context("sql"):
        yield controller


PARAMS_MAX_QUEUE_SIZE = [None, 1, 5]


@pytest.fixture(params=PARAMS_MAX_QUEUE_SIZE)
def controller_max_queue_size(request, common_props):
    max_queue_size = request.param
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    db = tempfile.NamedTemporaryFile().name
    sql_provider = SqlProvider(connection_string=f"sqlite:///{db}")

    # Create database tables
    Base.metadata.create_all(sql_provider._engine)

    with create_write_session(command_digest) as write_session:
        write_session.write(command.SerializeToString())
        storage.commit_write(command_digest, write_session)

    with create_write_session(action_digest) as write_session:
        write_session.write(action.SerializeToString())
        storage.commit_write(action_digest, write_session)

    scheduler = Scheduler(
        sql_provider,
        storage,
        poll_interval=0.1,
        property_set=common_props,
        max_queue_size=max_queue_size,
    )
    controller = ExecutionController(scheduler)
    assert controller.execution_instance is not None
    with controller.execution_instance, instance_context("sql"):
        yield controller


@pytest.fixture
def isolated_controllers(request, common_props):
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    db = tempfile.NamedTemporaryFile().name
    sql_provider = SqlProvider(connection_string=f"sqlite:///{db}")

    # Create database tables
    Base.metadata.create_all(sql_provider._engine)

    with create_write_session(command_digest) as write_session:
        write_session.write(command.SerializeToString())
        storage.commit_write(command_digest, write_session)

    with create_write_session(action_digest) as write_session:
        write_session.write(action.SerializeToString())
        storage.commit_write(action_digest, write_session)

    cache = LruActionCache(storage, 50)
    scheduler_a = Scheduler(sql_provider, storage, action_cache=cache, property_set=common_props)
    scheduler_b = Scheduler(sql_provider, storage, action_cache=cache, property_set=common_props)
    with scheduler_b, scheduler_a:
        yield ExecutionController(scheduler_a), ExecutionController(scheduler_b)


@pytest.fixture
def controller_postgres(
    asset_client: AssetClient, common_props: PropertySet, postgres
) -> Iterator[ExecutionController]:
    storage = lru_memory_cache.LRUMemoryCache(1024 * 1024)
    cache = LruActionCache(storage, 50)

    with pg_schema_provider(postgres) as sql_provider:
        with create_write_session(command_digest) as write_session:
            write_session.write(command.SerializeToString())
            storage.commit_write(command_digest, write_session)

        with create_write_session(action_digest) as write_session:
            write_session.write(action.SerializeToString())
            storage.commit_write(action_digest, write_session)

        scheduler = Scheduler(
            sql_provider,
            storage,
            poll_interval=0.01,
            action_cache=cache,
            property_set=common_props,
            asset_client=asset_client,
            queued_action_retention_hours=12,
            completed_action_retention_hours=1,
            action_result_retention_hours=3,
        )

        with scheduler, instance_context("sql"):
            yield ExecutionController(scheduler)


def mock_queue_job_action(
    scheduler: Scheduler,
    skip_cache_lookup=True,
    request_metadata=None,
    do_not_cache=False,
    assign=True,
    create_bot=True,
    locality_hint: str | None = None,
    job_priority=0,
    bot_capacity: int = 1,
):
    bot_id = "test-worker"
    bot_name = ""
    if create_bot:
        # Avoid re-adding the same bot entry
        with scheduler._sql.session() as session:
            bot = session.execute(select(BotEntry).where(BotEntry.bot_id == bot_id)).scalar_one_or_none()
            if bot is None:
                bot_name = scheduler.add_bot_entry(
                    bot_name=generate_bot_name(),
                    bot_session_id=bot_id,
                    bot_session_status=BotStatus.OK.value,
                    bot_capacity=bot_capacity,
                )
            else:
                bot_name = bot.name

    scheduling_metadata = SchedulingMetadata()
    if locality_hint is not None:
        scheduling_metadata.locality_hint = locality_hint

    operation_name = scheduler.queue_job_action(
        action=uncacheable_action if do_not_cache else action,
        action_digest=uncacheable_action_digest if do_not_cache else action_digest,
        command=command,
        platform_requirements={},
        property_label="unknown",
        priority=job_priority,
        skip_cache_lookup=skip_cache_lookup,
        request_metadata=request_metadata,
        scheduling_metadata=scheduling_metadata,
    )
    if assign:
        scheduler.assign_job_by_priority()
    job_name = scheduler.get_operation_job_name(operation_name)
    return bot_name, bot_id, operation_name, job_name


def test_update_lease_state(controller, push_service: MockAssetPushServicer):
    scheduler = controller.execution_instance.scheduler

    bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler)
    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        # check retention for queued action
        assert job.action_digest in push_service.blobs
        asset = push_service.blobs[job.action_digest]
        assert asset.instance_name == "asset"
        assert asset.uris == [f"nih:sha-256;{string_to_digest(job.action_digest).hash}"]
        action = Action.FromString(job.action)
        assert action.command_digest in asset.references_blobs
        assert action.input_root_digest in asset.references_directories
        assert asset.expire_at.ToDatetime() > datetime.datetime.now() + datetime.timedelta(hours=10)

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.PENDING.value

    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.ACTIVE.value

    mock_stderr_digest = Digest(hash="stderr", size_bytes=42)
    test_action_result = remote_execution_pb2.ActionResult(
        exit_code=0, stdout_raw=b"test", stderr_digest=mock_stderr_digest
    )
    lease.result.Pack(test_action_result)
    lease.state = LeaseState.COMPLETED.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 0

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        # check retention for completed action and result
        asset = push_service.blobs[job.action_digest]
        assert asset.expire_at.ToDatetime() > datetime.datetime.now() + datetime.timedelta(hours=0.5)
        action_result = scheduler.storage.get_message(string_to_digest(job.result), ExecuteResponse).result
        result_digest = create_digest(action_result.SerializeToString())
        result_asset = push_service.blobs[digest_to_string(result_digest)]
        assert result_asset.instance_name == "asset"
        assert result_asset.uris == [f"nih:sha-256;{result_digest.hash}"]
        assert mock_stderr_digest in result_asset.references_blobs
        assert result_asset.expire_at.ToDatetime() > datetime.datetime.now() + datetime.timedelta(hours=2)


def test_retry_job_lease(controller):
    scheduler: Scheduler = controller.execution_instance.scheduler
    scheduler.max_job_attempts = 2

    bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler)
    assert job_name is not None

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.n_tries == 1
        assert job.stage == OperationStage.QUEUED.value

    scheduler.close_bot_sessions(bot_name)
    bot_name = scheduler.add_bot_entry(bot_name=bot_name, bot_session_id=bot_id, bot_session_status=BotStatus.OK.value)
    scheduler.assign_job_by_priority()

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.n_tries == 2
        assert job.stage == OperationStage.QUEUED.value

    scheduler.close_bot_sessions(bot_name)

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.n_tries == 2
        assert job.stage == OperationStage.COMPLETED.value
        assert job.status_code == code_pb2.ABORTED


def test_requeue_queued_job(controller):
    scheduler: Scheduler = controller.execution_instance.scheduler
    bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler)
    assert job_name is not None

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.worker_name is not None
        assert job.stage == OperationStage.QUEUED.value

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]

    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.ACTIVE.value

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.worker_name is not None
        assert job.stage == OperationStage.EXECUTING.value

    # Make sure that retrying a job that was assigned but
    # not marked as in progress properly re-queues
    scheduler.close_bot_sessions(bot_name)
    bot_name = scheduler.add_bot_entry(bot_name=bot_name, bot_session_id=bot_id, bot_session_status=BotStatus.OK.value)

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.worker_name is None
        assert job.stage == OperationStage.QUEUED.value

    scheduler.assign_job_by_priority()

    with scheduler._sql.session() as session:
        job = scheduler._get_job(job_name, session)
        assert job is not None
        assert job.worker_name is not None
        assert job.stage == OperationStage.QUEUED.value


# Test that jobs can be created/completed with no action-cache, a working action cache,
# and an action-cache that throws exceptions when used
@pytest.mark.parametrize("cache_errors", [True, False])
def test_complete_lease_action_cache_error(controller, cache_errors):
    scheduler = controller.execution_instance.scheduler
    if scheduler.action_cache and cache_errors:
        with mock.patch.object(scheduler.action_cache, "get_action_result", autospec=True) as ac_mock:
            ac_mock.side_effect = ConnectionError("Fake Connection Error")
            bot_name, bot_id, _, _ = mock_queue_job_action(scheduler, skip_cache_lookup=False)
            assert ac_mock.call_count == 1
    else:
        bot_name, bot_id, _, _ = mock_queue_job_action(scheduler)

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.PENDING.value

    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.ACTIVE.value

    lease.state = LeaseState.COMPLETED.value
    if scheduler.action_cache and cache_errors:
        with mock.patch.object(scheduler.action_cache, "update_action_result", autospec=True) as ac_mock:
            ac_mock.side_effect = StorageFullError("TestActionCache is full")
            leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
            assert ac_mock.call_count == 1
    else:
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])

    assert len(leases) == 0


def test_uncacheable_action(controller):
    scheduler = controller.execution_instance.scheduler
    bot_name, bot_id, _, _ = mock_queue_job_action(scheduler, do_not_cache=True)

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.PENDING.value

    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]
    assert lease.state == LeaseState.ACTIVE.value

    lease.state = LeaseState.COMPLETED.value
    if scheduler.action_cache:
        # update_action_result should not be called for do_not_cache actions
        with mock.patch.object(scheduler.action_cache, "update_action_result", autospec=True) as ac_mock:
            leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
            assert ac_mock.call_count == 0
    else:
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])

    assert len(leases) == 0


def test_action_deduplication(controller):
    # Verify two identical actions are deduplicated
    scheduler = controller.execution_instance.scheduler
    _, _, operation_name, job_name = mock_queue_job_action(scheduler)
    _, _, operation_name2, job_name2 = mock_queue_job_action(scheduler)
    # Operation names should be different, but job names identical
    assert operation_name != operation_name2
    assert job_name == job_name2

    # Actions with do_not_cache=True must not be deduplicated
    _, _, uncacheable_operation_name, uncacheable_job_name = mock_queue_job_action(scheduler, do_not_cache=True)
    _, _, uncacheable_operation_name2, uncacheable_job_name2 = mock_queue_job_action(scheduler, do_not_cache=True)
    assert uncacheable_operation_name != uncacheable_operation_name2
    assert uncacheable_job_name != uncacheable_job_name2


def test_get_metadata_for_leases(controller):
    scheduler = controller.execution_instance.scheduler

    bot_name, bot_id, operation_name, _ = mock_queue_job_action(scheduler)

    scheduler.logstream_channel = mock.MagicMock()
    scheduler.logstream_instance = "testing"

    with mock.patch("buildgrid.server.scheduler.impl.logstream_client", new=mock_logstream_client()):
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
        assert len(leases) == 1
        lease = leases[0]
        lease.state = LeaseState.ACTIVE.value

        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
        assert len(leases) == 1
        lease = leases[0]

    lease_metadata = scheduler.get_metadata_for_leases([lease])
    op = scheduler.load_operation(operation_name)
    op_metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(op_metadata)

    assert op_metadata.partial_execution_metadata.worker == bot_id
    assert op_metadata.partial_execution_metadata.queued_timestamp.ToDatetime() != datetime.datetime(1970, 1, 1, 0, 0)
    assert op_metadata.partial_execution_metadata.worker_start_timestamp.ToDatetime() != datetime.datetime(
        1970, 1, 1, 0, 0
    )
    assert op_metadata.partial_execution_metadata.worker_completed_timestamp.ToDatetime() == datetime.datetime(
        1970, 1, 1, 0, 0
    )

    assert op_metadata.stdout_stream_name
    assert op_metadata.stdout_stream_name.endswith("stdout/mock-logstream")
    assert op_metadata.stderr_stream_name
    assert op_metadata.stderr_stream_name.endswith("stderr/mock-logstream")

    # Lease metadata should be the same, just with the write streams instead
    op_metadata.stdout_stream_name = op_metadata.stdout_stream_name + "/write"
    op_metadata.stderr_stream_name = op_metadata.stderr_stream_name + "/write"
    assert lease_metadata[0][0] == "executeoperationmetadata-bin"
    assert lease_metadata[0][1] == op_metadata.SerializeToString()


def test_list_operations(controller):
    """Test that the scheduler reports the correct
    number of operations when calling list_operations()"""
    scheduler = controller.execution_instance.scheduler
    operations, _ = scheduler.list_operations()
    assert len(operations) == 0

    mock_queue_job_action(scheduler)

    operations, _ = scheduler.list_operations()
    assert len(operations) == 1

    mock_queue_job_action(scheduler)
    mock_queue_job_action(scheduler)

    operations, _ = scheduler.list_operations()
    assert len(operations) == 3


def test_query_operation_metadata(controller):
    """Test that the scheduler returns the expected `RequestMetadata`
    information for an operation.
    """
    scheduler = controller.execution_instance.scheduler

    request_metadata = remote_execution_pb2.RequestMetadata()
    request_metadata.tool_details.tool_name = "my-tool"
    request_metadata.tool_details.tool_version = "1.0"
    request_metadata.tool_invocation_id = "invId123"
    request_metadata.correlated_invocations_id = "corId456"

    _, _, operation_name, _ = mock_queue_job_action(scheduler, request_metadata=request_metadata)
    metadata = scheduler.get_operation_request_metadata_by_name(operation_name)

    assert metadata is not None
    assert metadata.tool_details.tool_name == request_metadata.tool_details.tool_name
    assert metadata.tool_details.tool_version == request_metadata.tool_details.tool_version
    assert metadata.tool_invocation_id == request_metadata.tool_invocation_id
    assert metadata.correlated_invocations_id == request_metadata.correlated_invocations_id


# Validate that an ongoing job has an operation which is not marked done
def test_get_job_operation_ongoing(controller):
    scheduler = controller.execution_instance.scheduler
    _, _, operation_name, _ = mock_queue_job_action(scheduler)

    operation = scheduler.load_operation(operation_name)
    assert operation.name == operation_name
    assert not operation.done


# Validate that a finished job has an operation with an ExecuteResponse
# containing an OK status code
def test_get_job_operation_finished(controller):
    scheduler = controller.execution_instance.scheduler
    bot_name, bot_id, operation_name, _ = mock_queue_job_action(scheduler)

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]
    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]

    lease.state = LeaseState.COMPLETED.value
    test_action_result = remote_execution_pb2.ActionResult(exit_code=1, stdout_raw=b"test")
    lease.result.Pack(test_action_result)
    scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])

    operation = scheduler.load_operation(operation_name)
    assert operation.name == operation_name
    assert operation.done
    assert operation.WhichOneof("result") == "response"

    execute_response = remote_execution_pb2.ExecuteResponse()
    assert operation.response.Unpack(execute_response)

    assert execute_response.status.code == code_pb2.OK
    assert execute_response.result.stdout_raw == b"test"
    assert execute_response.result.exit_code == 1


# Validate that a failed job has an operation with an ExecuteResponse
# containing a non-OK status code
def test_get_job_operation_failed(controller):
    scheduler = controller.execution_instance.scheduler
    scheduler.max_job_attempts = 0
    bot_name, bot_id, operation_name, _ = mock_queue_job_action(scheduler)

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]
    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]

    lease.state = LeaseState.COMPLETED.value
    failed_status = Status(code=code_pb2.ABORTED, message="Failed Status")
    lease.status.CopyFrom(failed_status)
    scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])

    operation = scheduler.load_operation(operation_name)
    assert operation.name == operation_name
    assert operation.done
    assert operation.WhichOneof("result") == "response"

    execute_response = remote_execution_pb2.ExecuteResponse()
    assert operation.response.Unpack(execute_response)
    assert execute_response.status == failed_status


@flaky(max_runs=3)
@pytest.mark.parametrize("n_operations", [1, 2])
@pytest.mark.parametrize("sleep_time", [0.2])
def test_max_execution_timeout(controller_max_execution_timeout, sleep_time, n_operations):
    scheduler = controller_max_execution_timeout.execution_instance.scheduler

    max_execution_timeout = scheduler.max_execution_timeout

    # Queue Job
    bot_name, bot_id, operation_name, job_name = mock_queue_job_action(scheduler)

    # Create n operations
    operation_names = [operation_name]
    for i in range(n_operations - 1):
        operation_names.append(scheduler.create_operation(job_name=job_name))

    for i in range(n_operations):
        operation_initially = scheduler.load_operation(operation_names[i])
        assert operation_initially.done is False

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 1
    lease = leases[0]

    lease.state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
    assert len(leases) == 1
    lease = leases[0]

    # Make sure it was marked as "Executing"
    op_after_assignment = scheduler.load_operation(operation_name)
    assert not op_after_assignment.done

    # Wait and see it marked as cancelled when exceeding execution timeout...
    time.sleep(sleep_time)

    if max_execution_timeout and sleep_time >= max_execution_timeout:
        for operation_name in operation_names:
            operation = scheduler.load_operation(operation_name)
            assert operation.done is True
            # Verify the response in the operation has the correct
            # status code
            assert operation.WhichOneof("result") == "response"
            execute_response = remote_execution_pb2.ExecuteResponse()
            assert operation.response.Unpack(execute_response)
            assert execute_response.status.code == code_pb2.DEADLINE_EXCEEDED

        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
        assert len(leases) == 1
        lease = leases[0]
        assert lease.state == LeaseState.CANCELLED.value
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
        assert len(leases) == 0
    else:
        for operation_name in operation_names:
            operation = scheduler.load_operation(operation_name)
            assert operation.done is False
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [lease])
        assert len(leases) == 1
        lease = leases[0]
        assert lease.state == LeaseState.ACTIVE.value


def test_max_execution_timeout_rejection(controller):
    scheduler = controller.execution_instance.scheduler
    scheduler.max_execution_timeout = 1

    action = remote_execution_pb2.Action(
        command_digest=command_digest, do_not_cache=False, timeout=Duration(seconds=2)
    )
    action_digest = create_digest(action.SerializeToString())

    with create_write_session(action_digest) as write_session:
        write_session.write(action.SerializeToString())
        scheduler.storage.commit_write(action_digest, write_session)

    with pytest.raises(InvalidArgumentError):
        scheduler.queue_job_action(
            action=action,
            action_digest=action_digest,
            command=command,
            platform_requirements={},
            property_label="unknown",
            priority=0,
            skip_cache_lookup=False,
            request_metadata=None,
        )


@pytest.fixture
def mock_metering_client():
    usage_sink = []

    def mock_put_usage(identity, operation_name, usage):
        usage_sink.append((identity, operation_name, usage))

    mocked = mock.Mock()
    mocked.put_usage.side_effect = mock_put_usage
    mocked.sink = usage_sink
    yield mocked


def store_message(scheduler, message):
    binary = message.SerializeToString()
    digest = create_digest(binary)
    scheduler.storage.bulk_update_blobs([(digest, binary)])
    return digest


@pytest.fixture
def mock_execution_metadata(controller):
    scheduler = controller.execution_instance.scheduler

    action_digest = store_message(scheduler, Action())

    execution_stats = ExecutionStatistics()
    execution_stats.command_rusage.maxrss = 100
    execution_stats_any = ProtoAny()
    execution_stats_any.Pack(execution_stats)
    execution_stats_digest = store_message(scheduler, execution_stats_any)

    digest_any = ProtoAny()
    digest_any.Pack(execution_stats_digest)
    execution_metadata = remote_execution_pb2.ExecutedActionMetadata()
    execution_metadata.auxiliary_metadata.append(digest_any)

    now = datetime.datetime.now()
    with scheduler._sql.session(exceptions_to_not_raise_on=[Exception]) as session:
        session.add(
            JobEntry(
                name="job",
                instance_name="sql",
                action_digest=digest_to_string(action_digest),
                action=b"",
                create_timestamp=now,
                queued_timestamp=now,
                schedule_after=now,
                assigned=False,
                n_tries=1,
                platform_requirements="",
                property_label="unknown",
                command="foo",
            )
        )
        session.add(ClientIdentityEntry(id=1, instance="sql", workflow="build", actor="tool", subject="user1"))
        session.add(ClientIdentityEntry(id=2, instance="sql", workflow="build", actor="tool", subject="user2"))
        session.add(OperationEntry(name="op1", job_name="job", client_identity_id=1))
        session.add(OperationEntry(name="op2", job_name="job", client_identity_id=2))

    return execution_metadata


def test_publish_execution_stats(controller, mock_metering_client, mock_execution_metadata):
    scheduler = controller.execution_instance.scheduler
    scheduler.metering_client = mock_metering_client

    with instance_context("sql"):
        scheduler.publish_execution_stats("job", mock_execution_metadata, "linux")
    assert len(mock_metering_client.sink) == 2


def test_publish_execution_stats_fetch_fails_no_throw(controller, mock_metering_client, mock_execution_metadata):
    scheduler = controller.execution_instance.scheduler
    scheduler.metering_client = mock_metering_client
    mock_metering_client.put_usage.side_effect = MeteringServiceHTTPError(503, "big bang")

    with instance_context("sql"):
        scheduler.publish_execution_stats("job", mock_execution_metadata)
    assert len(mock_metering_client.sink) == 0


def test_publish_execution_stats_invalid_execution_stats(controller, mock_metering_client, mock_execution_metadata):
    scheduler = controller.execution_instance.scheduler
    scheduler.metering_client = mock_metering_client

    some_digest = Digest()
    some_digest_any = ProtoAny()
    some_digest_any.Pack(some_digest)
    mock_execution_metadata.auxiliary_metadata.pop()
    mock_execution_metadata.auxiliary_metadata.append(some_digest_any)

    with instance_context("sql"):
        scheduler.publish_execution_stats("job", mock_execution_metadata, "linux")
    assert len(mock_metering_client.sink) == 0


def test_publish_execution_stats_no_client(controller, mock_metering_client, mock_execution_metadata):
    scheduler = controller.execution_instance.scheduler
    # Just dont assign a client?? Weird test

    with instance_context("sql"):
        scheduler.publish_execution_stats("job", mock_execution_metadata, "linux")
    assert len(mock_metering_client.sink) == 0


def test_instance_isolation_create_operation(isolated_controllers):
    controller_a, controller_b = isolated_controllers
    scheduler_a = controller_a.execution_instance.scheduler
    scheduler_b = controller_b.execution_instance.scheduler

    with instance_context("instance-a"):
        _, _, _, job_name = mock_queue_job_action(scheduler_a)
        # Check that we can only create an Operation for the job on the same instance
        scheduler_a.create_operation(job_name=job_name)

    with instance_context("instance-b"):
        with pytest.raises(NotFoundError):
            scheduler_b.create_operation(job_name=job_name)


def test_instance_isolation_load_operation(isolated_controllers):
    controller_a, controller_b = isolated_controllers
    scheduler_a = controller_a.execution_instance.scheduler
    scheduler_b = controller_b.execution_instance.scheduler

    with instance_context("instance-a"):
        _, _, operation_name, _ = mock_queue_job_action(scheduler_a)
        # Check that fetching the operation respects instances
        scheduler_a.load_operation(operation_name)

    with instance_context("instance-b"):
        with pytest.raises(NotFoundError):
            scheduler_b.load_operation(operation_name)


def test_instance_isolation_lease_assignment(isolated_controllers):
    controller_a, controller_b = isolated_controllers
    scheduler_a: Scheduler = controller_a.execution_instance.scheduler
    scheduler_b: Scheduler = controller_b.execution_instance.scheduler
    bot_id = "test-worker"

    # Queue a job into instance-a
    with instance_context("instance-a"):
        mock_queue_job_action(scheduler_a, create_bot=False, assign=False)

    # Connect a bot to instance-b
    with instance_context("instance-b"):
        bot_name = scheduler_b.add_bot_entry(
            bot_name=generate_bot_name(), bot_session_id=bot_id, bot_session_status=BotStatus.OK.value
        )

    # Attempt to assign work in the scheduler that got the job
    scheduler_a.assign_job_by_priority(failure_backoff=0)

    # The bot should have no lease created
    with instance_context("instance-b"):
        leases = scheduler_b.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
        assert len(leases) == 0

    # Attempt to assign work in the scheduler that has the bot
    scheduler_b.assign_job_by_priority(failure_backoff=0)

    # There should still be no lease for the job, since it's instance name doesn't match the bot
    with instance_context("instance-b"):
        leases = scheduler_b.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
        assert len(leases) == 0

    # Synchronize the bot with the wrong instance
    with instance_context("instance-a"):
        with pytest.raises(InvalidArgumentError):
            scheduler_a.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])

    with instance_context("instance-b"):
        scheduler_b.close_bot_sessions(bot_name)

    # Add the bot to the instance which has a job queued
    with instance_context("instance-a"):
        bot_name = scheduler_a.add_bot_entry(
            bot_name=generate_bot_name(), bot_session_id=bot_id, bot_session_status=BotStatus.OK.value
        )

    # Attempt to assign work again
    scheduler_a.assign_job_by_priority(failure_backoff=0)

    # This time the job should have a lease
    with instance_context("instance-a"):
        leases = scheduler_a.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
        assert len(leases) == 1
        lease = leases[0]
        assert lease.state == LeaseState.PENDING.value


def test_isolated_instances_list_operations(isolated_controllers):
    controller_a, controller_b = isolated_controllers
    scheduler_a = controller_a.execution_instance.scheduler
    scheduler_b = controller_b.execution_instance.scheduler

    with instance_context("instance-a"):
        mock_queue_job_action(scheduler_a)

    # Check that ListOperations respects instances
    with instance_context("instance-a"):
        operations_a, _ = scheduler_a.list_operations()
    with instance_context("instance-b"):
        operations_b, _ = scheduler_b.list_operations()

    assert len(operations_a) == 1
    assert len(operations_b) == 0


def test_max_queue_size(controller_max_queue_size):
    scheduler = controller_max_queue_size.execution_instance.scheduler

    max_queue_size = scheduler.max_queue_size

    # Queue jobs up to the maximum queue size
    for _ in range(max_queue_size or 10):
        mock_queue_job_action(scheduler, do_not_cache=True, assign=False)

    if max_queue_size is not None:
        # Attempt to queue an additional job, expecting an error
        with pytest.raises(ResourceExhaustedError):
            mock_queue_job_action(scheduler, do_not_cache=True, assign=False)


def test_queue_job_action_with_scheduling_metadata_locality_hint(controller):
    """Test that jobs are created with locality_hint when scheduling metadata is provided."""
    scheduler = controller.execution_instance.scheduler

    # Create scheduling metadata with locality hint
    _, _, _, job_name = mock_queue_job_action(scheduler, locality_hint="a")

    # Check that the job has the correct locality_hint stored
    with scheduler._sql.session() as session:
        job = session.execute(select(JobEntry).where(JobEntry.name == job_name)).scalar_one()
        assert job.locality_hint == "a"


def test_queue_job_action_with_scheduling_metadata_empty_locality_hint(controller):
    """Test that jobs are created with NULL locality_hint when scheduling metadata has empty string."""
    scheduler = controller.execution_instance.scheduler

    # Queue job with scheduling metadata but empty locality hint
    _, _, _, job_name = mock_queue_job_action(scheduler, locality_hint="")

    # Check that the job has NULL locality_hint (empty string converts to None)
    with scheduler._sql.session() as session:
        job = session.execute(select(JobEntry).where(JobEntry.name == job_name)).scalar_one()
        assert job.locality_hint is None


def test_queue_job_action_without_scheduling_metadata(controller):
    """Test that jobs are created with NULL locality_hint when no scheduling metadata is provided."""
    scheduler = controller.execution_instance.scheduler

    # Queue job without scheduling metadata (backward compatibility)
    _, _, _, job_name = mock_queue_job_action(scheduler, locality_hint=None)

    # Check that the job has NULL locality_hint
    with scheduler._sql.session() as session:
        job = session.execute(select(JobEntry).where(JobEntry.name == job_name)).scalar_one()
        assert job.locality_hint is None


@pytest.mark.parametrize("controller", ["action-cache"], indirect=True)
def test_complete_job_with_locality_hint(controller, controller_postgres):
    """Test that jobs with locality hint can be competed."""

    for c in [controller, controller_postgres]:
        scheduler: Scheduler = c.execution_instance.scheduler

        # Create scheduling metadata with locality hint
        scheduling_metadata = SchedulingMetadata()
        locality_hint = "a"
        scheduling_metadata.locality_hint = locality_hint

        # Queue job with scheduling metadata
        bot_name = scheduler.add_bot_entry(
            bot_name=generate_bot_name(), bot_session_id="test-worker", bot_session_status=BotStatus.OK.value
        )
        bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler, locality_hint=locality_hint)
        assert job_name is not None

        # Complete the job
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
        assert len(leases) == 1
        leases[0].state = LeaseState.ACTIVE.value
        leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
        assert len(leases) == 1
        leases[0].state = LeaseState.COMPLETED.value
        scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
        with scheduler._sql.session() as session:
            job = scheduler._get_job(job_name, session)
            assert job is not None
            assert job.locality_hint == locality_hint

            # bot is associated with the locality hint
            locality_hints = (
                session.execute(select(BotLocalityHintEntry).where(BotLocalityHintEntry.bot_name == bot_name))
                .scalars()
                .all()
            )
            assert len(locality_hints) == 1
            assert locality_hints[0].locality_hint == locality_hint


@pytest.mark.parametrize("controller", ["action-cache"], indirect=True)
def test_complete_job_with_locality_hints_limit_size(controller, controller_postgres):
    """Test that jobs with locality hint can be competed."""

    for c in [controller, controller_postgres]:
        scheduler: Scheduler = c.execution_instance.scheduler

        # Create scheduling metadata with locality hint
        scheduling_metadata = SchedulingMetadata()
        locality_hint = "a"
        scheduling_metadata.locality_hint = locality_hint

        # Queue and complete jobs with scheduling metadata
        bot_name = ""  # placeholder, all jobs will use the same bot name
        for i in range(20):
            bot_name, bot_id, _, _ = mock_queue_job_action(scheduler, locality_hint=locality_hint)
            leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
            assert len(leases) == 1
            leases[0].state = LeaseState.ACTIVE.value
            leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
            assert len(leases) == 1
            leases[0].state = LeaseState.COMPLETED.value
            scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)

        with scheduler._sql.session() as session:
            locality_hints = (
                session.execute(select(BotLocalityHintEntry).where(BotLocalityHintEntry.bot_name == bot_name))
                .scalars()
                .all()
            )
            # size is limited
            assert len(locality_hints) == scheduler.bot_locality_hint_limit


def test_bot_proactively_fetch(controller_postgres):
    """Test that bots can proactively fetch jobs when bot_proactively_fetch is enabled."""
    scheduler: Scheduler = controller_postgres.execution_instance.scheduler

    # Enqueue 2 jobs
    bot_name, bot_id, _, _ = mock_queue_job_action(scheduler, do_not_cache=True, skip_cache_lookup=True, assign=False)
    _ = mock_queue_job_action(scheduler, do_not_cache=True, skip_cache_lookup=True, assign=False)

    # Even though assign is False, the bot should be able to fetch jobs
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases)
    # Complete the first job
    leases[0].state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
    assert len(leases)
    leases[0].state = LeaseState.COMPLETED.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
    assert len(leases)

    with scheduler._sql.session() as session:
        jobs = session.execute(select(JobEntry)).scalars().all()
        assert len(jobs) == 2
        assert jobs[0].stage == OperationStage.COMPLETED.value
        # Assert that the second job is scheduled
        assert jobs[1].assigned
        assert jobs[1].worker_name == bot_id


def test_schedule_by_instances(controller_postgres):

    scheduler: Scheduler = controller_postgres.execution_instance.scheduler

    # Enqueue a job without assigning
    bot_name, bot_id, _, _ = mock_queue_job_action(scheduler, do_not_cache=True, skip_cache_lookup=True, assign=False)

    # Assign by instance names
    num_updated = scheduler.assign_job_by_priority(failure_backoff=0.1, instance_names=frozenset(["sql", "foo"]))
    assert num_updated == 1

    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) != 0
    # Complete the  job
    leases[0].state = LeaseState.ACTIVE.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
    assert len(leases) != 0
    leases[0].state = LeaseState.COMPLETED.value
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, leases)
    assert len(leases) == 0


def test_schedule_by_instances_isolation(controller_postgres):

    scheduler: Scheduler = controller_postgres.execution_instance.scheduler

    # Enqueue a job without assigning
    _, _, _, job_name = mock_queue_job_action(scheduler, do_not_cache=True, skip_cache_lookup=True, assign=False)
    assert job_name is not None

    # Assign by unrelated instance names
    num_updated = scheduler.assign_job_by_priority(failure_backoff=0.1, instance_names=frozenset(["foo", "bar"]))
    assert num_updated == 0


def test_scheduling_match_by_locality(controller_postgres):
    """Test that a job is scheduled based on locality hints."""

    scheduler: Scheduler = controller_postgres.execution_instance.scheduler
    locality_hint = "a"
    bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler, locality_hint=locality_hint, assign=False)
    assert job_name is not None
    # Add another bot with locality hint
    bot_id2 = "test-worker2"
    bot_name2 = scheduler.add_bot_entry(
        bot_name=generate_bot_name(), bot_session_id=bot_id2, bot_session_status=BotStatus.OK.value
    )
    with scheduler._sql.session() as session:
        bot_locality_hint = BotLocalityHintEntry(bot_name=bot_name2, locality_hint=locality_hint)
        session.add(bot_locality_hint)

    # Run assignment
    strategy = AssignByLocality(sampling=SamplingConfig(sample_size=2))
    bot_fn = create_bot_assignment_fn(strategy, scheduler, "locality")
    scheduler.assign_job_by_priority(bot_assignment_fn=bot_fn)

    # Job is assigned to the bot with matching locality hint
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) == 0
    leases = scheduler.synchronize_bot_leases(bot_name2, bot_id2, BotStatus.OK.value, [])
    assert len(leases) > 0


def test_scheduling_match_by_locality_fallback(controller_postgres):
    """Test that a job is scheduled by the fallback mechanism."""

    scheduler: Scheduler = controller_postgres.execution_instance.scheduler
    locality_hint = "a"
    bot_name, bot_id, _, job_name = mock_queue_job_action(scheduler, locality_hint=locality_hint, assign=False)
    assert job_name is not None

    # Run assignment
    scheduler.assign_job_by_priority(bot_assignment_fn=scheduler.match_bot_by_locality)

    # Even though the bot has no locality hint, it should still be able to fetch the job
    leases = scheduler.synchronize_bot_leases(bot_name, bot_id, BotStatus.OK.value, [])
    assert len(leases) > 0


def test_queue_position(controller_postgres) -> None:
    scheduler: Scheduler = controller_postgres.execution_instance.scheduler

    # Helper function to add a mock job to queue
    def add_mock_job(priority: int) -> str:
        scheduling_metadata = SchedulingMetadata()
        operation_name = scheduler.queue_job_action(
            action=uncacheable_action,
            action_digest=uncacheable_action_digest,
            command=command,
            platform_requirements={},
            property_label="unknown",
            priority=priority,
            skip_cache_lookup=True,
            request_metadata=None,
            scheduling_metadata=scheduling_metadata,
        )
        return operation_name

    # Add 5 jobs of varying priority and timestamp to queue
    first = add_mock_job(0)
    low = add_mock_job(1)
    second = add_mock_job(0)
    high = add_mock_job(-1)
    third = add_mock_job(0)

    assert first != second

    # Check queue positions
    instance_name = "sql"

    assert "~1" == scheduler.get_queue_position(high, instance_name)
    assert "~2" == scheduler.get_queue_position(first, instance_name)
    assert "~3" == scheduler.get_queue_position(second, instance_name)
    assert "~4" == scheduler.get_queue_position(third, instance_name)
    assert "~5" == scheduler.get_queue_position(low, instance_name)

    assert "3+" == scheduler.get_queue_position(third, instance_name, job_search_limit=3)
    assert "3+" == scheduler.get_queue_position(low, instance_name, job_search_limit=3)

    # Create a bot
    scheduler.add_bot_entry(
        bot_name=generate_bot_name(),
        bot_session_id="test-worker",
        bot_session_status=BotStatus.OK.value,
    )

    # Assign the next job
    scheduler.assign_job_by_priority()

    # Check queue positions have moved up
    assert "~0" == scheduler.get_queue_position(high, instance_name)
    assert "~1" == scheduler.get_queue_position(first, instance_name)
    assert "~2" == scheduler.get_queue_position(second, instance_name)
    assert "~3" == scheduler.get_queue_position(third, instance_name)
    assert "~4" == scheduler.get_queue_position(low, instance_name)


def test_scheduling_match_by_sampled_capacity(controller_postgres):
    """Test that a job is scheduled based on load-balancing via sampling."""

    scheduler: Scheduler = controller_postgres.execution_instance.scheduler
    # Add a bot and assign a job to it
    # The remaining capacity of the bot is 1
    mock_queue_job_action(scheduler, bot_capacity=2)

    # Add another bot (capacity == 2) & job pair
    bot_id2 = "test-worker2"
    _ = scheduler.add_bot_entry(
        bot_name=generate_bot_name(), bot_session_id=bot_id2, bot_session_status=BotStatus.OK.value, bot_capacity=2
    )
    _, _, _, job_name = mock_queue_job_action(
        scheduler, create_bot=False, assign=False, bot_capacity=2, skip_cache_lookup=True, do_not_cache=True
    )
    assert job_name is not None

    # Run assignment
    strategy = AssignByCapacity(sampling=SamplingConfig(sample_size=2))
    bot_fn = create_bot_assignment_fn(strategy, scheduler, "sampled")
    scheduler.assign_job_by_priority(bot_assignment_fn=bot_fn)

    # Job is assigned to the idle bot that has the higher capacity
    with scheduler._sql.session() as session:
        job = session.execute(select(JobEntry).where(JobEntry.name == job_name)).scalar_one()
        assert job.assigned is True
        assert job.worker_name == bot_id2
