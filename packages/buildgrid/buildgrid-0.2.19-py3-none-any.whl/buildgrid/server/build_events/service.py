# Copyright (C) 2021 Bloomberg LP
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
PublishBuildEvent service
=========================

"""


from typing import Iterable, Iterator

import grpc
from google.protobuf.empty_pb2 import Empty

from buildgrid._protos.build.buildgrid.query_build_events_pb2 import DESCRIPTOR as QBE_DESCRIPTOR
from buildgrid._protos.build.buildgrid.query_build_events_pb2 import (
    QueryEventStreamsRequest,
    QueryEventStreamsResponse,
)
from buildgrid._protos.build.buildgrid.query_build_events_pb2_grpc import (
    QueryBuildEventsServicer,
    add_QueryBuildEventsServicer_to_server,
)
from buildgrid._protos.google.devtools.build.v1.build_events_pb2 import BuildEvent
from buildgrid._protos.google.devtools.build.v1.publish_build_event_pb2 import DESCRIPTOR as PBE_DESCRIPTOR
from buildgrid._protos.google.devtools.build.v1.publish_build_event_pb2 import (
    OrderedBuildEvent,
    PublishBuildToolEventStreamRequest,
    PublishBuildToolEventStreamResponse,
    PublishLifecycleEventRequest,
)
from buildgrid._protos.google.devtools.build.v1.publish_build_event_pb2_grpc import (
    PublishBuildEventServicer,
    add_PublishBuildEventServicer_to_server,
)
from buildgrid.server.build_events.storage import BuildEventStream, BuildEventStreamStorage
from buildgrid.server.decorators import rpc
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.servicer import InstancedServicer

LOGGER = buildgrid_logger(__name__)


def is_lifecycle_event(event: BuildEvent) -> bool:
    lifecycle_events = [
        "build_enqueued",
        "invocation_attempt_started",
        "invocation_attempt_finished",
        "build_finished",
    ]
    return event.WhichOneof("event") in lifecycle_events


class PublishBuildEventService(PublishBuildEventServicer, InstancedServicer[BuildEventStreamStorage]):
    SERVICE_NAME = "PublishBuildEvent"
    REGISTER_METHOD = add_PublishBuildEventServicer_to_server
    FULL_NAME = PBE_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc()
    def PublishLifecycleEvent(self, request: PublishLifecycleEventRequest, context: grpc.ServicerContext) -> Empty:
        """Handler for PublishLifecycleEvent requests.

        This method takes a request containing a build lifecycle event, and
        uses it to update the high-level state of a build (with a corresponding)
        event stream.

        """
        ordered_build_event = request.build_event
        if is_lifecycle_event(ordered_build_event.event):
            stream = self._get_stream_for_event(ordered_build_event)
            stream.publish_event(ordered_build_event)

        else:
            LOGGER.warning("Got a build tool event in a PublishLifecycleEvent request.")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)

        return Empty()

    @rpc()
    def PublishBuildToolEventStream(
        self,
        request_iterator: Iterable[PublishBuildToolEventStreamRequest],
        context: grpc.ServicerContext,
    ) -> Iterator[PublishBuildToolEventStreamResponse]:
        for request in request_iterator:
            LOGGER.info("Got a BuildToolEvent on the stream.")

            # We don't need to give any special treatment to BuildToolEvents, so
            # just call the underlying `get_stream` method here.
            stream = self.get_instance("").get_stream(request.ordered_build_event.stream_id)

            # `stream` should never be `None`, but in case the internals change
            # in future lets be safe.
            if stream is not None:
                stream.publish_event(request.ordered_build_event)

            yield PublishBuildToolEventStreamResponse(
                stream_id=request.ordered_build_event.stream_id,
                sequence_number=request.ordered_build_event.sequence_number,
            )

    def _get_stream_for_event(self, event: OrderedBuildEvent) -> BuildEventStream:
        # If this is the start of a new build, then we want a new stream
        if event.event.WhichOneof("event") == "build_enqueued":
            return self.get_instance("").new_stream(event.stream_id)
        return self.get_instance("").get_stream(event.stream_id)


class QueryBuildEventsService(QueryBuildEventsServicer, InstancedServicer[BuildEventStreamStorage]):
    SERVICE_NAME = "QueryBuildEvents"
    REGISTER_METHOD = add_QueryBuildEventsServicer_to_server
    FULL_NAME = QBE_DESCRIPTOR.services_by_name[SERVICE_NAME].full_name

    @rpc()
    def QueryEventStreams(
        self, request: QueryEventStreamsRequest, context: grpc.ServicerContext
    ) -> QueryEventStreamsResponse:
        streams = self.get_instance("").get_matching_streams(stream_key_regex=request.build_id_pattern)
        return QueryEventStreamsResponse(streams=[stream.to_grpc_message() for stream in streams])
