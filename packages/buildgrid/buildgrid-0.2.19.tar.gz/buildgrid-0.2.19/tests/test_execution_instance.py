# Copyright (C) 2018 Bloomberg LP
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

from unittest import mock

import pytest
from buildgrid_metering.client.client import SyncMeteringServiceClient
from buildgrid_metering.client.exceptions import MeteringServiceClientError
from buildgrid_metering.models.api import GetThrottlingResponse
from buildgrid_metering.models.dataclasses import ComputingUsage, Identity, RPCUsage, Usage
from grpc._server import _Context

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Action, Command, Digest
from buildgrid._protos.google.longrunning import operations_pb2
from buildgrid.server.enums import MeteringThrottleAction
from buildgrid.server.exceptions import CancelledError, FailedPreconditionError, ResourceExhaustedError
from buildgrid.server.execution.instance import ExecutionInstance
from buildgrid.server.scheduler import DynamicPropertySet
from buildgrid.server.sql.models import ClientIdentityEntry


class MockDataStore:
    def __init__(self, storage):
        self.storage = storage


class MockScheduler:
    def __init__(self, storage, property_set, metering_client=None, metering_throttle_action=None):
        self.storage = storage
        self.property_set = property_set
        self.metering_client = metering_client
        self.metering_throttle_action = metering_throttle_action or MeteringThrottleAction.DEPRIORITIZE

        self._kwargs = None
        self._args = None

    def queue_job_action(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
        return "queued"

    def return_queue_call_args(self):
        return self._args, self._kwargs


class DeprecatedAction:
    def __init__(self, *, command_digest, input_root_digest, do_not_cache):
        self.command_digest = command_digest
        self.input_root_digest = input_root_digest
        self.do_not_cache = do_not_cache

    def HasField(self, field):
        return False


class MockStorage:
    def __init__(self, pairs):
        command_digest = Digest(hash="command_digest", size_bytes=0)
        input_root_digest = Digest(hash="input_root_digest", size_bytes=0)
        self.action = Action(command_digest=command_digest, input_root_digest=input_root_digest, do_not_cache=True)
        self.command = Command()
        for property_pair in pairs:
            prop = self.command.platform.properties.add()
            prop.name = property_pair[0]
            prop.value = property_pair[1]

            prop = self.action.platform.properties.add()
            prop.name = property_pair[0]
            prop.value = property_pair[1]

        self.action_no_platform = DeprecatedAction(
            command_digest=command_digest, input_root_digest=input_root_digest, do_not_cache=True
        )
        self.command_fetched = False

    def get_message(self, digest, *args, **kwargs):
        if digest == "fake":
            return self.action
        elif digest == "fake-no-platform":
            return self.action_no_platform
        else:
            self.command_fetched = True
            return self.command


def test_execute_platform_matching_simple():
    """Will match on standard keys."""

    pairs = [("OSFamily", "linux"), ("ISA", "x86-64"), ("ISA", "x86-avx")]
    storage = MockStorage(pairs)
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(storage, property_set=property_set))
    assert exec_instance.execute(action_digest="fake", skip_cache_lookup=False) == "queued"


def test_execute_platform_matching_fallback():
    """Will match on standard keys."""

    pairs = [("OSFamily", "linux"), ("ISA", "x86-64"), ("ISA", "x86-avx")]
    storage = MockStorage(pairs)
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(storage, property_set=property_set))
    assert exec_instance.execute(action_digest="fake-no-platform", skip_cache_lookup=False) == "queued"
    assert storage.command_fetched


def test_execute_platform_matching_too_many_os():
    """Will not match due to too many OSFamilies being specified."""

    pairs = [("OSFamily", "linux"), ("OSFamily", "macos"), ("ISA", "x86-64"), ("ISA", "x86-avx")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    with pytest.raises(FailedPreconditionError):
        exec_instance.execute(action_digest="fake", skip_cache_lookup=False)


def test_execute_platform_matching_too_many_os_platform_key():
    """Make sure adding duplicate keys won't cause issues ."""

    pairs = [("OSFamily", "linux"), ("OSFamily", "macos"), ("ISA", "x86-64"), ("ISA", "x86-avx")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    with pytest.raises(FailedPreconditionError):
        exec_instance.execute(action_digest="fake", skip_cache_lookup=False)


def test_execute_platform_matching_failure():
    """Will not match due to platform-keys missing 'ChrootDigest'."""

    pairs = [("OSFamily", "linux"), ("ISA", "x86-64"), ("ChrootDigest", "deadbeef")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    with pytest.raises(FailedPreconditionError):
        exec_instance.execute(action_digest="fake", skip_cache_lookup=False)


def test_execute_platform_matching_success():
    """Will match due to platform keys matching."""

    pairs = [("ChrootDigest", "deadbeed")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    assert exec_instance.execute(action_digest="fake", skip_cache_lookup=False) == "queued"


def test_execute_platform_matching_config_only():
    """Will match due to platform keys matching."""

    pairs = [("OSFamily", "linux"), ("ISA", "x86-64"), ("ChrootDigest", "deadbeed")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    scheduler = MockScheduler(MockStorage(pairs), property_set=property_set)
    exec_instance = ExecutionInstance(scheduler)
    assert exec_instance.execute(action_digest="fake", skip_cache_lookup=False) == "queued"
    # The ChrootDigest key shouldn't make it into the actual requirements
    _, queue_kwargs = scheduler.return_queue_call_args()
    assert "ChrootDigest" not in queue_kwargs["platform_requirements"]
    assert all(key in queue_kwargs["platform_requirements"] for key in property_set.match_property_keys)


def test_execute_platform_matching_both_empty():
    """Edge case where nothing specified on either side."""

    pairs = []
    property_set = DynamicPropertySet(
        unique_property_keys=set(),
        match_property_keys=set(),
        wildcard_property_keys=set(),
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    assert exec_instance.execute(action_digest="fake", skip_cache_lookup=False) == "queued"


def test_execute_platform_matching_no_job_req():
    """If job doesn't specify platform key requirements, it should always pass."""

    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    exec_instance = ExecutionInstance(MockScheduler(MockStorage(pairs), property_set=property_set))
    assert exec_instance.execute(action_digest="fake", skip_cache_lookup=False) == "queued"


def test_execute_priority_set():
    """Check that the priority gets set."""
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set)
    exec_instance = ExecutionInstance(mock_scheduler)
    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=3)
    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == 3


def test_execute_priority_default():
    """Check that the priority gets sets to 0 when not specified."""
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set)
    exec_instance = ExecutionInstance(mock_scheduler)
    exec_instance.execute(action_digest="fake", skip_cache_lookup=False)
    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == 0


@pytest.fixture
def mock_exec_instance():
    return ExecutionInstance(MockScheduler(MockStorage([]), [], []))


@pytest.fixture
def mock_active_context():
    cxt = mock.MagicMock(spec=_Context)
    yield cxt


@pytest.fixture
def mock_operation():
    operation = mock.Mock(spec=operations_pb2.Operation)
    operation.done = False
    return operation


@pytest.fixture
def mock_operation_done():
    operation = mock.Mock(spec=operations_pb2.Operation)
    operation.done = True
    return operation


@pytest.fixture(params=[0, 1, 2])
def operation_updates_message_seq(mock_operation, request):
    seq = []
    for i in range(request.param):
        seq.append((None, mock_operation))

    return (request.param, seq)


@pytest.fixture(params=[0, 1, 2])
def operation_updates_completing_message_seq(mock_operation, mock_operation_done, request):
    seq = []
    for i in range(request.param):
        seq.append((None, mock_operation))

    seq.append((None, mock_operation_done))

    # Add sentinel operation update: this should never be dequeued
    # since we should stop once the operation completed (above)
    seq.append((ValueError, mock_operation))
    return (request.param, seq)


@pytest.fixture(params=[0, 1, 2])
def operation_updates_ending_with_error_seq(mock_operation, mock_operation_done, request):
    seq = []
    for i in range(request.param):
        seq.append((None, mock_operation))

    seq.append((CancelledError("Operation has been cancelled"), mock_operation))

    # Add sentinel operation update: this should never be dequeued
    # since we should stop once we encounter the first error
    seq.append((ValueError, mock_operation))
    return (request.param, seq)


@pytest.fixture(params=[0, 1, 2, 3])
def n_0_to_3_inclusive(request):
    return request.param


@pytest.fixture
def client_identity():
    return ClientIdentityEntry(instance="", workflow="build", actor="tool", subject="user")


@pytest.fixture
def mock_metering_client() -> SyncMeteringServiceClient:
    mock_metering_client = mock.Mock()
    mock_metering_client.get_throttling.return_value = GetThrottlingResponse(throttled=False)
    mock_metering_client.put_usage.return_value = None
    return mock_metering_client


def test_execute_not_throttled(client_identity: ClientIdentityEntry, mock_metering_client: SyncMeteringServiceClient):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set, metering_client=mock_metering_client)
    exec_instance = ExecutionInstance(mock_scheduler)

    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=client_identity)

    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == -1
    mock_metering_client.put_usage.assert_has_calls(
        [
            mock.call(
                Identity(
                    instance=client_identity.instance,
                    workflow=client_identity.workflow,
                    actor=client_identity.actor,
                    subject=client_identity.subject,
                ),
                "queued",
                Usage(rpc=RPCUsage(execute=1)),
            )
        ]
    )


def test_execute_not_throttled_given_exception(
    client_identity: ClientIdentityEntry, mock_metering_client: SyncMeteringServiceClient
):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_metering_client.get_throttling.side_effect = MeteringServiceClientError("connection reset")
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set, metering_client=mock_metering_client)
    exec_instance = ExecutionInstance(mock_scheduler)

    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=client_identity)

    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == -1


def test_execute_not_throttled_if_no_client_id(mock_metering_client: SyncMeteringServiceClient):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set, metering_client=mock_metering_client)
    exec_instance = ExecutionInstance(mock_scheduler)

    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=None)

    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == -1
    assert mock_metering_client.put_usage.call_count == 0


def test_execute_not_throttled_if_no_client(client_identity: ClientIdentityEntry):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set, metering_client=None)
    exec_instance = ExecutionInstance(mock_scheduler)

    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=client_identity)

    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == -1


def test_execute_throttled(client_identity: ClientIdentityEntry, mock_metering_client: SyncMeteringServiceClient):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_metering_client.get_throttling.return_value = GetThrottlingResponse(
        throttled=True, tracked_time_window_secs=100, tracked_usage=Usage(computing=ComputingUsage(utime=1))
    )
    mock_scheduler = MockScheduler(MockStorage(pairs), property_set=property_set, metering_client=mock_metering_client)
    exec_instance = ExecutionInstance(mock_scheduler)

    exec_instance.execute(action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=client_identity)

    _, kwargs = mock_scheduler.return_queue_call_args()
    assert "priority" in kwargs
    assert kwargs["priority"] == 1
    mock_metering_client.put_usage.assert_has_calls(
        [
            mock.call(
                Identity(
                    instance=client_identity.instance,
                    workflow=client_identity.workflow,
                    actor=client_identity.actor,
                    subject=client_identity.subject,
                ),
                "queued",
                Usage(rpc=RPCUsage(execute=1)),
            )
        ]
    )


def test_execute_throttled_rejected(
    client_identity: ClientIdentityEntry, mock_metering_client: SyncMeteringServiceClient
):
    pairs = [("OSFamily", "linux"), ("ISA", "x86-64")]
    property_set = DynamicPropertySet(
        unique_property_keys={"OSFamily"},
        match_property_keys={"OSFamily", "ISA"},
        wildcard_property_keys={"ChrootDigest"},
    )
    mock_metering_client.get_throttling.return_value = GetThrottlingResponse(
        throttled=True, tracked_time_window_secs=100, tracked_usage=Usage(computing=ComputingUsage(utime=1))
    )
    mock_scheduler = MockScheduler(
        MockStorage(pairs),
        property_set=property_set,
        metering_client=mock_metering_client,
        metering_throttle_action=MeteringThrottleAction.REJECT,
    )
    exec_instance = ExecutionInstance(mock_scheduler)

    with pytest.raises(ResourceExhaustedError):
        exec_instance.execute(
            action_digest="fake", skip_cache_lookup=False, priority=-1, client_identity=client_identity
        )
