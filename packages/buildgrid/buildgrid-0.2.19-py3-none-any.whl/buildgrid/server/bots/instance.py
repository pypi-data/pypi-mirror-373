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

import uuid
from contextlib import ExitStack
from threading import Event

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import ExecutedActionMetadata
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import DESCRIPTOR as BOTS_DESCRIPTOR
from buildgrid._protos.google.devtools.remoteworkers.v1test2.bots_pb2 import BotSession
from buildgrid.server.context import current_instance
from buildgrid.server.enums import BotStatus
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.scheduler import Scheduler
from buildgrid.server.scheduler.impl import BotMetrics
from buildgrid.server.scheduler.properties import hash_from_dict
from buildgrid.server.servicer import Instance
from buildgrid.server.settings import MAX_WORKER_TTL, NETWORK_TIMEOUT
from buildgrid.server.utils.bots import bot_log_tags, get_bot_capacity
from buildgrid.server.utils.cancellation import CancellationContext

LOGGER = buildgrid_logger(__name__)


class BotsInterface(Instance):
    SERVICE_NAME = BOTS_DESCRIPTOR.services_by_name["Bots"].full_name

    def __init__(self, scheduler: Scheduler) -> None:
        self._stack = ExitStack()
        self.scheduler = scheduler

    def start(self) -> None:
        self._stack.enter_context(self.scheduler)
        self._stack.enter_context(self.scheduler.bot_notifier)
        if self.scheduler.session_expiry_interval > 0:
            self._stack.enter_context(self.scheduler.session_expiry_timer)

    def stop(self) -> None:
        self._stack.close()
        LOGGER.info("Stopped Bots.")

    def create_bot_session(
        self, bot_session: BotSession, context: CancellationContext, deadline: float | None = None
    ) -> BotSession:
        """Creates a new bot session. Server should assign a unique
        name to the session. If the bot_id already exists in the database
        then any leases already assigned to that id are requeued
        (via close_bot_session) and then the name previously associated with
        the bot_id is replaced with the new name in the database. If the bot_id
        is not in the database, a new record is created.
        """
        if not bot_session.bot_id:
            raise InvalidArgumentError("Bot's id must be set by client.")

        capacity = get_bot_capacity(bot_session)
        labels = self.scheduler.property_set.bot_property_labels(bot_session)
        capabilities = list(map(hash_from_dict, self.scheduler.property_set.worker_properties(bot_session)))

        # Create new record
        bot_session.name = f"{current_instance()}/{uuid.uuid4()}"
        with self.scheduler.bot_notifier.subscription(bot_session.name) as event:
            self.scheduler.add_bot_entry(
                bot_name=bot_session.name,
                bot_session_id=bot_session.bot_id,
                bot_session_status=bot_session.status,
                bot_property_labels=labels,
                bot_capability_hashes=capabilities,
                bot_capacity=capacity,
            )

            LOGGER.info("Created new BotSession. Requesting leases.", tags=bot_log_tags(bot_session))
            self._request_leases(bot_session, context, event, deadline=deadline, capacity=capacity)
        self._assign_deadline_for_botsession(bot_session)

        LOGGER.debug("Completed CreateBotSession.", tags=bot_log_tags(bot_session))
        return bot_session

    def update_bot_session(
        self,
        bot_session: BotSession,
        context: CancellationContext,
        deadline: float | None = None,
        partial_execution_metadata: dict[str, ExecutedActionMetadata] | None = None,
    ) -> tuple[BotSession, list[tuple[str, bytes]]]:
        """Client updates the server. Any changes in state to the Lease should be
        registered server side. Assigns available leases with work.
        """
        LOGGER.debug("Beginning initial lease synchronization.", tags=bot_log_tags(bot_session))

        orig_leases_count = len(bot_session.leases)
        with self.scheduler.bot_notifier.subscription(bot_session.name) as event:
            capacity = get_bot_capacity(bot_session)
            leases = self.scheduler.synchronize_bot_leases(
                bot_session.name,
                bot_session.bot_id,
                bot_session.status,
                bot_session.leases,
                partial_execution_metadata,
                max_capacity=capacity,
            )
            del bot_session.leases[:]
            bot_session.leases.extend(leases)

            LOGGER.debug("Completed initial lease synchronization.", tags=bot_log_tags(bot_session))

            capabilities = list(map(hash_from_dict, self.scheduler.property_set.worker_properties(bot_session)))
            self.scheduler.maybe_update_bot_platforms(bot_session.name, capabilities)

            # Only block on lease assignment if we aren't currently working on anything, to avoid
            # the client needing to deal with interrupting this wait when a current job is
            # completed. Any extra assignments can be picked up when we next synchronize.
            #
            # This should also be skipped if we've removed a lease from the session, to mitigate
            # situations where the scheduler is updated with the new state of a lease, but a fault
            # thereafter causes the worker to retry the old UpdateBotSession call.
            if not leases and not orig_leases_count:
                self._request_leases(bot_session, context, event, deadline=deadline, capacity=capacity)

        metadata = self.scheduler.get_metadata_for_leases(bot_session.leases)
        self._assign_deadline_for_botsession(bot_session)

        LOGGER.debug("Completed UpdateBotSession.", tags=bot_log_tags(bot_session))
        return bot_session, metadata

    def get_bot_status_metrics(self) -> BotMetrics:
        return self.scheduler.get_bot_status_metrics()

    def _assign_deadline_for_botsession(self, bot_session: BotSession) -> None:
        bot_session.expire_time.FromDatetime(
            self.scheduler.refresh_bot_expiry_time(bot_session.name, bot_session.bot_id)
        )

    def _request_leases(
        self,
        bot_session: BotSession,
        context: CancellationContext,
        event: Event,
        deadline: float | None = None,
        capacity: int = 1,
    ) -> None:
        # We do not assign new leases if we are not in the OK state.
        if bot_session.status != BotStatus.OK.value:
            LOGGER.debug("BotSession not healthy. Skipping lease request.", tags=bot_log_tags(bot_session))
            return

        # Skip waiting for new leases if we're at capacity
        if len(bot_session.leases) == capacity:
            LOGGER.debug(
                "BotSession already assigned to capacity. Skipping lease request.",
                tags=bot_log_tags(bot_session),
            )
            return

        # If no deadline is set default to the max we allow workers to long-poll for work
        if deadline is None:
            deadline = MAX_WORKER_TTL

        # If the specified bot session keepalive timeout is greater than the
        # deadline it can result in active bot sessions being reaped
        deadline = min(deadline, self.scheduler.bot_session_keepalive_timeout)

        # Use 80% of the given deadline to give time to respond but no less than NETWORK_TIMEOUT
        ttl = deadline * 0.8
        if ttl < NETWORK_TIMEOUT:
            LOGGER.info(
                "BotSession expires in less time than timeout. No leases will be assigned.",
                tags={**bot_log_tags(bot_session), "network_timeout": NETWORK_TIMEOUT},
            )
            return

        # Wait for an update to the bot session and then resynchronize the lease.
        LOGGER.debug("Waiting for job assignment.", tags={**bot_log_tags(bot_session), "deadline": deadline})
        context.on_cancel(event.set)
        event.wait(ttl)

        # This is a best-effort check the see if the original request is still alive. Depending on
        # network and proxy configurations, this status may not accurately reflect the state of the
        # client connection. If we know for certain that the request is no longer being monitored,
        # we can exit now to avoid state changes not being acked by the bot.
        if context.is_cancelled():
            LOGGER.debug("Bot request cancelled. Skipping lease synchronization.", tags=bot_log_tags(bot_session))
            return

        # In the case that we had a timeout, we can return without post lease synchronization. This
        # helps deal with the case of uncommunicated cancellations from the bot request. If the bot
        # is actually still waiting on work, this will be immediately followed up by a new request
        # from the worker, where the initial synchronization will begin a bot ack for the pending
        # job. In the case that the request has been abandoned, it avoids competing updates to the
        # database records in the corresponding bots session.
        if not event.is_set():
            LOGGER.debug("Bot assignment timeout. Skipping lease synchronization.", tags=bot_log_tags(bot_session))
            return

        # Synchronize the lease again to pick up db changes.
        LOGGER.debug("Synchronizing leases after job assignment wait.", tags=bot_log_tags(bot_session))
        if leases := self.scheduler.synchronize_bot_leases(
            bot_session.name, bot_session.bot_id, bot_session.status, bot_session.leases, max_capacity=capacity
        ):
            del bot_session.leases[:]
            bot_session.leases.extend(leases)
