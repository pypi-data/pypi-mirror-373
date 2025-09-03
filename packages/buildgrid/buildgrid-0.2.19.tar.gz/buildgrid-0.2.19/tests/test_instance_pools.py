from typing import Iterator

import pytest
from grpc import Channel

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    Action,
    BatchUpdateBlobsRequest,
    Command,
    ExecuteOperationMetadata,
    ExecuteRequest,
)
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2_grpc import (
    ContentAddressableStorageStub,
    ExecutionStub,
)
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import (
    BotSession,
    CreateBotSessionRequest,
    UpdateBotSessionRequest,
)
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2_grpc import BotsStub
from buildgrid.server.client.channel import setup_channel
from buildgrid.server.enums import BotStatus, LeaseState, OperationStage
from buildgrid.server.sql.models import Base
from buildgrid.server.sql.provider import SqlProvider
from buildgrid.server.utils.digests import create_digest
from tests.utils.fixtures import new_postgres
from tests.utils.server import serve

CONFIG = """
server:
  - !channel
    address: "[::]:50051"
    insecure-mode: true

authorization:
  method: none

monitoring:
  enabled: false

connections:
  - !sql-connection &sql
    connection-string: CONNECTION_STRING
    pool-size: 5
    pool-timeout: 30
    max-overflow: 10

storages:
  - !lru-storage &storage
    size: 256mb

caches:
  - !lru-action-cache &cache
    storage: *storage
    max-cached-refs: 256
    cache-failed-actions: true
    allow-updates: true

schedulers:
  - !sql-scheduler &scheduler
    storage: *storage
    sql: *sql
    queue-timeout-job-max-age: { minutes: 1 }
    queue-timeout-period: { minutes: 1 }
    queue-timeout-max-window: 100
    action-cache: *cache
    instance-pools: [['instance1', 'instance2']]
    assigners:
      - !priority-age-assigner
        count: 3
        interval: 0.1
        priority-assignment-percentage: 100
        failure-backoff: 0

instances:
  - name: ['instance1', 'instance2', 'instance3']

    services:
      - !cas
        storage: *storage
        tree-cache-size: 100
        tree-cache-ttl-minutes: 30

      - !bytestream
        storage: *storage

      - !action-cache
        cache: *cache

      - !execution
        scheduler: *scheduler

      - !bots
        scheduler: *scheduler

thread-pool-size: 100
"""


@pytest.fixture
def channel() -> Iterator[str]:
    with new_postgres() as postgres:
        sql_provider = SqlProvider(connection_string=postgres.url())
        with sql_provider._engine.begin() as conn:
            Base.metadata.create_all(conn)

        try:
            with serve(CONFIG.replace("CONNECTION_STRING", postgres.url())) as (server, _):
                channel, _ = setup_channel("http://" + server.remote)
                yield channel
        finally:
            sql_provider._engine.dispose()
        pass


def upload_action(channel: Channel, instance: str):
    cas = ContentAddressableStorageStub(channel)

    command = Command()
    command_data = command.SerializeToString()
    command_digest = create_digest(command_data)

    action = Action(command_digest=command_digest, do_not_cache=True)
    action_data = action.SerializeToString()
    action_digest = create_digest(action_data)

    res = cas.BatchUpdateBlobs(
        BatchUpdateBlobsRequest(
            instance_name=instance,
            requests=[
                BatchUpdateBlobsRequest.Request(digest=command_digest, data=command_data),
                BatchUpdateBlobsRequest.Request(digest=action_digest, data=action_data),
            ],
        )
    )
    for response in res.responses:
        assert response.status.code == 0

    return action_digest


def test_bots_on_same_instance_as_request(channel: Channel):
    """
    Create an action on the same instance that the worker is connected to.
    """

    action_digest = upload_action(channel, "instance1")
    execution = ExecutionStub(channel)
    bots = BotsStub(channel)

    exec_stream = execution.Execute(ExecuteRequest(instance_name="instance1", action_digest=action_digest))
    op = next(exec_stream)
    metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(metadata)
    assert metadata.stage == OperationStage.QUEUED.value

    bot_session = BotSession()
    bot_session.bot_id = "test-worker"
    bot_session.status = BotStatus.OK.value

    bot_session = bots.CreateBotSession(
        CreateBotSessionRequest(parent="instance1", bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 1
    assert bot_session.leases[0].state == LeaseState.PENDING.value

    bot_session.leases[0].state = LeaseState.ACTIVE.value
    bot_session = bots.UpdateBotSession(
        UpdateBotSessionRequest(name=bot_session.name, bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 1
    assert bot_session.leases[0].state == LeaseState.ACTIVE.value

    bot_session.leases[0].state = LeaseState.COMPLETED.value
    bot_session = bots.UpdateBotSession(
        UpdateBotSessionRequest(name=bot_session.name, bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 0

    op = list(exec_stream)[-1]
    metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(metadata)
    assert metadata.stage == OperationStage.COMPLETED.value


def test_bots_on_same_instance_as_pool(channel: Channel):
    """
    Create an action on a different instance than what the worker is connected to.
    Because instance1 is in the same pool as instance2, they should be scheduled on the same worker.
    """

    action_digest = upload_action(channel, "instance1")
    execution = ExecutionStub(channel)
    bots = BotsStub(channel)

    exec_stream = execution.Execute(ExecuteRequest(instance_name="instance1", action_digest=action_digest))
    op = next(exec_stream)
    metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(metadata)
    assert metadata.stage == OperationStage.QUEUED.value

    bot_session = BotSession()
    bot_session.bot_id = "test-worker"
    bot_session.status = BotStatus.OK.value

    bot_session = bots.CreateBotSession(
        CreateBotSessionRequest(parent="instance2", bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 1
    assert bot_session.leases[0].state == LeaseState.PENDING.value

    bot_session.leases[0].state = LeaseState.ACTIVE.value
    bot_session = bots.UpdateBotSession(
        UpdateBotSessionRequest(name=bot_session.name, bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 1
    assert bot_session.leases[0].state == LeaseState.ACTIVE.value

    bot_session.leases[0].state = LeaseState.COMPLETED.value
    bot_session = bots.UpdateBotSession(
        UpdateBotSessionRequest(name=bot_session.name, bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 0

    op = list(exec_stream)[-1]
    metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(metadata)
    assert metadata.stage == OperationStage.COMPLETED.value


def test_bots_on_different_instance_than_pool(channel: Channel):
    """
    Create an action on a different instance than what the worker is connected to.
    Because instance3 is not in the same pool as instance2, they should be isolated.
    """

    action_digest = upload_action(channel, "instance3")
    execution = ExecutionStub(channel)
    bots = BotsStub(channel)

    exec_stream = execution.Execute(ExecuteRequest(instance_name="instance3", action_digest=action_digest))
    op = next(exec_stream)
    metadata = ExecuteOperationMetadata()
    op.metadata.Unpack(metadata)
    assert metadata.stage == OperationStage.QUEUED.value

    bot_session = BotSession()
    bot_session.bot_id = "test-worker"
    bot_session.status = BotStatus.OK.value

    bot_session = bots.CreateBotSession(
        CreateBotSessionRequest(parent="instance1", bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 0

    # Verify a worker connected to the instance3 still gets the work.
    bot_session = bots.CreateBotSession(
        CreateBotSessionRequest(parent="instance3", bot_session=bot_session),
        timeout=5,
    )
    assert len(bot_session.leases) == 1
    assert bot_session.leases[0].state == LeaseState.PENDING.value
