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


"""
ExecutionInstance
=================
An instance of the Remote Execution Service.
"""


from contextlib import ExitStack
from typing import Iterable

from buildgrid_metering.models.dataclasses import Identity, RPCUsage, Usage

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import DESCRIPTOR as RE_DESCRIPTOR
from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import (
    Action,
    Command,
    Digest,
    Platform,
    RequestMetadata,
)
from buildgrid._protos.build.buildgrid.scheduling_pb2 import SchedulingMetadata
from buildgrid._protos.google.longrunning.operations_pb2 import Operation
from buildgrid.server.auth.manager import get_context_client_identity
from buildgrid.server.enums import MeteringThrottleAction
from buildgrid.server.exceptions import FailedPreconditionError, NotFoundError, ResourceExhaustedError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.scheduler import Scheduler
from buildgrid.server.servicer import Instance
from buildgrid.server.sql.models import ClientIdentityEntry
from buildgrid.server.utils.cancellation import CancellationContext

# All priorities >= this value will not be throttled / deprioritized
EXECUTION_DEPRIORITIZATION_LIMIT = 1

LOGGER = buildgrid_logger(__name__)


class ExecutionInstance(Instance):
    SERVICE_NAME = RE_DESCRIPTOR.services_by_name["Execution"].full_name

    def __init__(
        self,
        scheduler: Scheduler,
        operation_stream_keepalive_timeout: int | None = None,
    ) -> None:
        self._stack = ExitStack()
        self.scheduler = scheduler

        self._operation_stream_keepalive_timeout = operation_stream_keepalive_timeout

    def start(self) -> None:
        self.scheduler.start()
        self._stack.callback(self.scheduler.stop)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info("Stopped Execution.")

    def execute(
        self,
        *,
        action_digest: Digest,
        skip_cache_lookup: bool,
        priority: int = 0,
        request_metadata: RequestMetadata | None = None,
        client_identity: ClientIdentityEntry | None = None,
        scheduling_metadata: SchedulingMetadata | None = None,
    ) -> str:
        """
        Sends a job for execution. Queues an action and creates an Operation to be associated with this action.
        """

        action = self.scheduler.storage.get_message(action_digest, Action)
        if not action:
            raise FailedPreconditionError("Could not get action from storage.")

        command = self.scheduler.storage.get_message(action.command_digest, Command)
        if not command:
            raise FailedPreconditionError("Could not get command from storage.")

        if action.HasField("platform"):
            platform = action.platform
        elif command.HasField("platform"):
            platform = command.platform
        else:
            platform = Platform()

        property_label, platform_requirements = self.scheduler.property_set.execution_properties(platform)

        should_throttle = self._should_throttle_execution(priority, client_identity)
        if should_throttle:
            if self.scheduler.metering_throttle_action == MeteringThrottleAction.REJECT:
                raise ResourceExhaustedError("User quota exceeded")

            # TODO test_execution_instance is a total mess. It mocks way too much making tests
            # brittle. when possible merge it into execution_service tests and use proper logging here.
            # Should be able to write `action_digest=[{action_digest.hash}/{action_digest.size_bytes}]`, but cant
            # AttributeError: 'str' object has no attribute 'hash'
            LOGGER.info(
                "Job priority throttled.",
                tags=dict(digest=action_digest, old_priority=priority, new_priority=EXECUTION_DEPRIORITIZATION_LIMIT),
            )
            priority = EXECUTION_DEPRIORITIZATION_LIMIT

        operation_name = self.scheduler.queue_job_action(
            action=action,
            action_digest=action_digest,
            command=command,
            platform_requirements=platform_requirements,
            property_label=property_label,
            skip_cache_lookup=skip_cache_lookup,
            priority=priority,
            request_metadata=request_metadata,
            client_identity=client_identity,
            scheduling_metadata=scheduling_metadata,
        )
        self._meter_execution(client_identity, operation_name)
        return operation_name

    def stream_operation_updates(self, operation_name: str, context: CancellationContext) -> Iterable[Operation]:
        job_name = self.scheduler.get_operation_job_name(operation_name)
        if not job_name:
            raise NotFoundError(f"Operation name does not exist: [{operation_name}]")
        # Start the listener as soon as we get the job name and re-query. This avoids potentially missing
        # the completed update if it triggers in between sending back the first result and the yield resuming.
        with self.scheduler.ops_notifier.subscription(job_name) as update_requested:
            yield (operation := self.scheduler.load_operation(operation_name))
            if operation.done:
                return

            # When the context is deactivated, we can quickly stop waiting.
            context.on_cancel(update_requested.set)
            while not context.is_cancelled():
                update_requested.wait(timeout=self._operation_stream_keepalive_timeout)
                update_requested.clear()

                if context.is_cancelled():
                    return

                yield (operation := self.scheduler.load_operation(operation_name))
                if operation.done:
                    return

    def _meter_execution(self, client_identity: ClientIdentityEntry | None, operation_name: str) -> None:
        """Meter the number of executions of client"""
        if self.scheduler.metering_client is None or client_identity is None:
            return
        try:
            identity = Identity(
                instance=client_identity.instance,
                workflow=client_identity.workflow,
                actor=client_identity.actor,
                subject=client_identity.subject,
            )
            usage = Usage(rpc=RPCUsage(execute=1))
            self.scheduler.metering_client.put_usage(identity, operation_name, usage)
        except Exception as exc:
            LOGGER.exception(
                f"Failed to publish execution usage for identity: {get_context_client_identity()}", exc_info=exc
            )

    def _should_throttle_execution(self, priority: int, client_identity: ClientIdentityEntry | None) -> bool:
        if (
            priority >= EXECUTION_DEPRIORITIZATION_LIMIT
            or self.scheduler.metering_client is None
            or client_identity is None
        ):
            return False
        try:
            identity = Identity(
                instance=client_identity.instance,
                workflow=client_identity.workflow,
                actor=client_identity.actor,
                subject=client_identity.subject,
            )
            response = self.scheduler.metering_client.get_throttling(identity)
            if response.throttled:
                LOGGER.info(
                    "Execution request is throttled.",
                    tags=dict(client_id=client_identity, usage=response.tracked_usage),
                )
            return response.throttled
        except Exception as exc:
            LOGGER.exception("Failed to get throttling information.", exc_info=exc)
            return False
