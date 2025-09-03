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


import re
from threading import RLock
from typing import Iterator

from buildgrid._protos.build.buildgrid.query_build_events_pb2 import QueryEventStreamsResponse
from buildgrid._protos.google.devtools.build.v1.build_events_pb2 import StreamId
from buildgrid._protos.google.devtools.build.v1.publish_build_event_pb2 import OrderedBuildEvent
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.servicer import Instance

LOGGER = buildgrid_logger(__name__)


class DuplicateStreamError(Exception):
    """Error when encountering a name collision between event streams."""

    pass


class BuildEventStream:
    """Internal representation of a stream of OrderedBuildEvents.

    This class provides in-memory storage of the events in a given Build Event
    Stream. Many of these Build Event Streams may relate to the same build, or
    even to the same invocation of a tool.

    Args:
        stream_id (StreamId): A gRPC message defining the ID of this stream.

    """

    def __init__(self, stream_id: StreamId):
        self._stream_id = stream_id
        self._events: list[OrderedBuildEvent] = []
        LOGGER.debug("Created BuildEventStream.", tags=dict(stream_id=self._stream_id))

    def __len__(self) -> int:
        return len(self._events)

    def publish_event(self, event: OrderedBuildEvent) -> None:
        """Publish an ``OrderedBuildEvent`` into the stream.

        Args:
            event (OrderedBuildEvent): The event to publish to the stream.
                This is an ``OrderedBuildEvent`` message from the
                ``publish_build_event`` proto.
        """
        self._events.append(event)
        LOGGER.debug("Stored BuildEvent in stream.", tags=dict(stream_id=self._stream_id))

    def query_events(self, query: str | None = None) -> Iterator[OrderedBuildEvent]:
        """Query the contents of this stream.

        Filter the contents of the event stream by some query, returning an
        iterator of matching OrderedBuildEvents.

        .. note::
            The filtering functionality of this method is currently not
            implemented, and the iterator returned contains all the events
            in the stream no matter what query is used.

        Args:
            query (str): The filter string to use when querying events.
        """
        # TODO(SotK): Implement some basic querying here
        if query is not None:
            raise NotImplementedError("Specifying a build events query is not supported yet.")
        yield from self._events

    def to_grpc_message(self) -> QueryEventStreamsResponse.BuildEventStream:
        """Convert this object to a ``BuildEventStream`` gRPC message.

        This method converts this internal event stream representation into
        a ``QueryEventStreamsResponse.BuildEventStream`` gRPC message, as
        defined in the ``query_build_events`` proto.

        """
        return QueryEventStreamsResponse.BuildEventStream(stream_id=self._stream_id, events=self._events)


class BuildEventStreamStorage(Instance):
    """In-memory storage of Build Event Streams.

    This class stores a collection of Build Event Streams, and handles both
    creation of new streams and querying the streams which already exist
    based on their stream ID. Streams are stored in-memory and are lost on
    service restart, so shouldn't be relied on as a source of persistent
    data when using this storage class.

    This class is similar to the ``.*Instance`` classes used by other
    BuildGrid services, in that it is instantiated by the config parser
    and used by a ``.*Service`` class instantiated by the server class.
    Unlike the other instance classes however, this class doesn't have an
    ``instance_name`` attribute due to the Build Events protos not having
    the concept of multiple instances.

    """

    # Hack in a service name here to fit the pattern
    SERVICE_NAME = "BuildEvents"

    def __init__(self) -> None:
        self._streams: dict[str, BuildEventStream] = {}
        self._streams_lock = RLock()

    def new_stream(self, stream_id: StreamId) -> BuildEventStream:
        """Create and return a new ``BuildEventStream`` with the given ID.

        This method creates a new :class:`BuildEventStream` with the given
        ``StreamId``, and returns it. If a stream with that ID already exists
        in this ``BuildEventStreamStorage``, then a :class:`DuplicateStreamError`
        is raised.

        Args:
            stream_id (StreamId): The gRPC StreamId message containing the
                ID of the stream to create.

        """
        key = self._get_stream_key(stream_id)
        with self._streams_lock:
            if key in self._streams:
                raise DuplicateStreamError(f"Stream with key {key} already exists.")

            stream = BuildEventStream(stream_id)
            self._streams[key] = stream
            return stream

    def get_stream(self, stream_id: StreamId) -> BuildEventStream:
        """Return a ``BuildEventStream`` with the given stream ID.

        This method takes a stream ID, converts it to a stream key, and
        returns the stream with that key if one exists.

        This method will create a new :class:`BuildEventStream` if one with
        the given ID doesn't exist.

        Args:
            stream_id (StreamId): The StreamID message from an event to
                get the ``BuildEventStream`` for.

        Returns:
            A ``BuildEventStream`` with the given ID, or None.
        """
        key = self._get_stream_key(stream_id)
        with self._streams_lock:
            stream = self._streams.get(key)
            if stream is None:
                stream = self.new_stream(stream_id)
            return stream

    def get_matching_streams(self, stream_key_regex: str) -> list[BuildEventStream]:
        """Return a list of event streams which match the given key pattern.

        This method takes a regular expression as a string, and returns
        a list of :class:`BuildEventStream` objects whose stream key (based
        on the events' StreamId) matches the regex.

        Args:
            stream_key_regex (str): A regular expression to use to find
                matching streams.

        Returns:
            List of :class:`BuildEventStream` objects which have a key
            matching the given regex.

        """
        regex = re.compile(stream_key_regex)
        return [stream for key, stream in self._streams.items() if regex.search(key) is not None]

    def _get_stream_key(self, stream_id: StreamId) -> str:
        return f"{stream_id.build_id}.{stream_id.component}.{stream_id.invocation_id}"
