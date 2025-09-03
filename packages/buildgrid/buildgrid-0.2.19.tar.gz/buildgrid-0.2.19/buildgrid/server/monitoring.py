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


import asyncio
import ctypes
import os
import socket
import sys
import threading
import time
from contextvars import ContextVar
from enum import Enum
from multiprocessing import Event, Process, Queue
from queue import Empty
from typing import IO, TYPE_CHECKING, Any, Sequence, Union, cast

from google.protobuf import json_format

from buildgrid._protos.build.buildgrid.monitoring_pb2 import BusMessage, LogRecord, MetricRecord
from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.logging import buildgrid_logger

if TYPE_CHECKING:
    from asyncio.streams import StreamWriter

LOGGER = buildgrid_logger(__name__)


class MonitoringOutputType(Enum):
    # Standard output stream.
    STDOUT = "stdout"
    # On-disk file.
    FILE = "file"
    # UNIX domain socket.
    SOCKET = "socket"
    # UDP IP:port
    UDP = "udp"
    # Silent
    SILENT = "silent"


class MonitoringOutputFormat(Enum):
    # Protobuf binary format.
    BINARY = "binary"
    # JSON format.
    JSON = "json"
    # StatsD format. Only metrics are kept - logs are dropped.
    STATSD = "statsd"


class StatsDTagFormat(Enum):
    NONE = "none"
    INFLUX_STATSD = "influx-statsd"
    DOG_STATSD = "dogstatsd"
    GRAPHITE = "graphite"


class UdpWrapper:
    """Wraps socket sendto() in write() so it can be used polymorphically"""

    def __init__(self, endpoint_location: str) -> None:
        try:
            addr, port = endpoint_location.split(":")
            self._addr, self._port = addr, int(port)
        except ValueError as e:
            error_msg = f"udp endpoint-location {endpoint_location} does not have the form address:port"
            raise ValueError(error_msg) from e
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write(self, message: bytes) -> None:
        self._socket.sendto(message, (self._addr, self._port))

    def close(self) -> None:
        return self._socket.close()


MonitoringEndpoint = Union[IO[bytes], UdpWrapper, "StreamWriter"]


class MonitoringBus:
    def __init__(
        self,
        endpoint_type: MonitoringOutputType = MonitoringOutputType.SOCKET,
        endpoint_location: str | None = None,
        metric_prefix: str = "",
        serialisation_format: MonitoringOutputFormat = MonitoringOutputFormat.STATSD,
        tag_format: StatsDTagFormat = StatsDTagFormat.INFLUX_STATSD,
        additional_tags: dict[str, str] | None = None,
    ) -> None:
        self.__event_loop: asyncio.AbstractEventLoop | None = None
        self._streaming_process: Process | None = None
        self._stop_streaming_worker = Event()
        self._streaming_process_ppid: int | None = None

        self.__message_queue: "Queue[Any]" = Queue()
        self.__sequence_number = 1

        self.__output_location = None
        self.__async_output = False
        self.__json_output = False
        self.__statsd_output = False
        self.__print_output = False
        self.__udp_output = False
        self.__is_silent = False

        if endpoint_type == MonitoringOutputType.FILE:
            self.__output_location = endpoint_location

        elif endpoint_type == MonitoringOutputType.SOCKET:
            self.__output_location = endpoint_location
            self.__async_output = True

        elif endpoint_type == MonitoringOutputType.STDOUT:
            self.__print_output = True

        elif endpoint_type == MonitoringOutputType.UDP:
            self.__output_location = endpoint_location
            self.__udp_output = True

        elif endpoint_type == MonitoringOutputType.SILENT:
            self.__is_silent = True

        else:
            raise InvalidArgumentError(f"Invalid endpoint output type: [{endpoint_type}]")

        self.__metric_prefix = metric_prefix

        if serialisation_format == MonitoringOutputFormat.JSON:
            self.__json_output = True
        elif serialisation_format == MonitoringOutputFormat.STATSD:
            self.__statsd_output = True

        self.__tag_format = tag_format
        self._additional_tags = additional_tags or {}

    # --- Public API ---

    @property
    def is_enabled(self) -> bool:
        """Whether monitoring is enabled.

        The send_record methods perform this check so clients don't need to
        check this before sending a record to the monitoring bus, but it is
        provided for convenience."""
        return self._streaming_process is not None and self._streaming_process.is_alive()

    @property
    def prints_records(self) -> bool:
        """Whether or not messages are printed to standard output."""
        return self.__print_output

    @property
    def is_silent(self) -> bool:
        """Whether or not this is a silent monitoring bus."""
        return self.__is_silent

    def process_should_exit(self) -> bool:
        """Whether the streaming worker process should exit.

        The streaming worker process should exit if explicitly told to by the
        _stop_streaming_worker event or if it has been orphaned by the parent.
        """

        try:
            assert self._streaming_process_ppid, "Streaming process pid access before initialization"
            os.kill(self._streaming_process_ppid, 0)
            return self._stop_streaming_worker.is_set()
        except ProcessLookupError:
            LOGGER.info("Monitoring bus process was orphaned, exiting.")
            return True
        except Exception as e:
            LOGGER.info(f"Exception when checking if parent process of monitoring bus is still alive, exiting: {e}")
            return True

    def __enter__(self) -> "MonitoringBus":
        self.start()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.stop()

    def start(self) -> None:
        """Starts the monitoring bus worker task."""
        if self.__is_silent or self._streaming_process is not None:
            return

        self._streaming_process = Process(target=self._streaming_worker)
        self._streaming_process_ppid = os.getpid()
        self._streaming_process.start()

    def stop(self) -> None:
        """Cancels the monitoring bus worker task."""
        if self.__is_silent or self._streaming_process is None:
            return

        self._stop_streaming_worker.set()
        self._streaming_process.join()

    def prefix_record_nowait(self, record: MetricRecord) -> MetricRecord:
        """Prefix the record's metric name. This is the same as prefix_record, but called synchronously.

        See the prefix_record docstring for notes on the prefixing rules.

        Args:
            record (Message): The record to prefix.
        """
        record.name = f"{self.__metric_prefix}{record.name}"
        return record

    def send_record_nowait(self, record: MetricRecord | LogRecord) -> None:
        """Publishes a record onto the bus synchronously.

        Args:
            record (Message): The record to send.
        """
        if not self.is_enabled:
            return

        if record.DESCRIPTOR is MetricRecord.DESCRIPTOR:
            record = self.prefix_record_nowait(cast(MetricRecord, record))

        self.__message_queue.put_nowait(record)

    # --- Private API ---
    def _format_statsd_with_tags(self, name: str, tags: list[str], value: int | float, metric_type: str) -> str:
        if not tags or self.__tag_format == StatsDTagFormat.NONE:
            return f"{name}:{value}|{metric_type}\n"

        if self.__tag_format == StatsDTagFormat.INFLUX_STATSD:
            tag_string = ",".join(tags)
            return f"{name},{tag_string}:{value}|{metric_type}\n"

        elif self.__tag_format == StatsDTagFormat.DOG_STATSD:
            tag_string = ",".join(tags)
            return f"{name}:{value}|{metric_type}|#{tag_string}\n"

        elif self.__tag_format == StatsDTagFormat.GRAPHITE:
            tag_string = ";".join(tags)
            return f"{name};{tag_string}:{value}|{metric_type}\n"

        else:
            return f"{name}:{value}|{metric_type}\n"

    def _format_record_as_statsd_string(self, record: MetricRecord) -> str:
        """Helper function to convert metrics to a string in the statsd format.

        See https://github.com/statsd/statsd/blob/master/docs/metric_types.md for valid metric types.

        Note that BuildGrid currently only supports Counters, Timers, and Gauges, and it has the custom
        Distribution type as an alias for Timers.

        Args:
            record (Message): The record to convert.
        """

        tag_assignment_symbol = "="
        if self.__tag_format == StatsDTagFormat.DOG_STATSD:
            tag_assignment_symbol = ":"

        for key, value in self._additional_tags.items():
            if key not in record.metadata:
                record.metadata[key] = value

        tags = [
            f"{key}{tag_assignment_symbol}{record.metadata[key]}"
            for key in sorted(record.metadata.keys())
            if str(record.metadata[key]) != ""
        ]

        if record.type == MetricRecord.COUNTER:
            if record.count is None:
                raise ValueError(f"COUNTER record {record.name} is missing a count")
            return self._format_statsd_with_tags(record.name, tags, record.count, "c")
        elif record.type is MetricRecord.TIMER:
            if record.duration is None:
                raise ValueError(f"TIMER record {record.name} is missing a duration")
            return self._format_statsd_with_tags(record.name, tags, record.duration.ToMilliseconds(), "ms")
        elif record.type is MetricRecord.DISTRIBUTION:
            if record.count is None:
                raise ValueError(f"DISTRIBUTION record {record.name} is missing a count")
            return self._format_statsd_with_tags(record.name, tags, record.count, "ms")
        elif record.type is MetricRecord.GAUGE:
            if record.value is None:
                raise ValueError(f"GAUGE record {record.name} is missing a value")
            return self._format_statsd_with_tags(record.name, tags, record.value, "g")
        raise ValueError("Unknown record type.")

    def _streaming_worker(self) -> None:
        """Fetch records from the monitoring queue, and publish them.

        This method loops until the `self._stop_streaming_worker` event is set.
        Intended to run in a subprocess, it fetches messages from the message
        queue in this class, formats the record appropriately, and publishes
        them to whatever output endpoints were specified in the configuration
        passed to this monitoring bus.

        This method won't exit immediately when `self._stop_streaming_worker`
        is set. It may be waiting to fetch a message from the queue, which
        blocks for up to a second. It also needs to do some cleanup of the
        output endpoints once looping has finished.

        """

        def __streaming_worker(end_points: Sequence[MonitoringEndpoint]) -> bool:
            """Get a LogRecord or a MetricRecord, and publish it.

            This function fetches the next record from the internal queue,
            formats it in the configured output style, and writes it to
            the endpoints provided in `end_points`.

            If there is no record available within 1 second, or the record
            received wasn't a LogRecord or MetricRecord protobuf message,
            then this function returns False. Otherwise this returns True
            if publishing was successful (an exception will be raised if
            publishing goes wrong for some reason).

            Args:
                end_points (List): The list of output endpoints to write
                    formatted records to.

            Returns:
                bool, indicating whether or not a record was written.

            """
            try:
                record = self.__message_queue.get(timeout=1)
            except Empty:
                return False

            message = BusMessage()
            message.sequence_number = self.__sequence_number

            if record.DESCRIPTOR is LogRecord.DESCRIPTOR:
                message.log_record.CopyFrom(record)

            elif record.DESCRIPTOR is MetricRecord.DESCRIPTOR:
                message.metric_record.CopyFrom(record)

            else:
                return False

            if self.__json_output:
                blob_message = json_format.MessageToJson(message).encode()

                for end_point in end_points:
                    end_point.write(blob_message)

            elif self.__statsd_output:
                if record.DESCRIPTOR is MetricRecord.DESCRIPTOR:
                    statsd_message = self._format_record_as_statsd_string(record)
                    for end_point in end_points:
                        end_point.write(statsd_message.encode())

            else:
                blob_size = ctypes.c_uint32(message.ByteSize())
                blob_message = message.SerializeToString()

                for end_point in end_points:
                    end_point.write(bytes(blob_size))
                    end_point.write(blob_message)

            return True

        # TODO clean this up. Way too much happening to understand it well.
        output_writers: list[Any] = []
        output_file: Any = None

        async def __client_connected_callback(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
            output_writers.append(writer)

        # TODO clean this up. Total mess of what type this should or can be.
        async def _wait_closed(event: threading.Event, writer: Any) -> None:
            try:
                await writer.wait_closed()
            finally:
                event.set()

        self.__event_loop = asyncio.new_event_loop()

        # In good circumstances we stay in the first iteration of this loop forever.
        # The loop exists so that the subprocess is more resilient to temporary
        # failures (e.g. failing to connect to a socket immediately on startup)
        while not self.process_should_exit():
            try:
                if self.__async_output and self.__output_location:
                    async_done = threading.Event()

                    async def _async_output() -> None:
                        await asyncio.start_unix_server(
                            __client_connected_callback, path=self.__output_location, loop=self.__event_loop
                        )

                        while not self.process_should_exit():
                            try:
                                if __streaming_worker(output_writers):
                                    self.__sequence_number += 1

                                    for writer in output_writers:
                                        await writer.drain()
                            except asyncio.CancelledError:
                                raise
                            except Exception:
                                LOGGER.warning("Caught exception when publishing metric.", exc_info=True)
                        async_done.set()

                    asyncio.ensure_future(_async_output(), loop=self.__event_loop)
                    async_done.wait()

                elif self.__udp_output and self.__output_location:
                    output_writers.append(UdpWrapper(self.__output_location))
                    while not self.process_should_exit():
                        try:
                            if __streaming_worker(output_writers):
                                self.__sequence_number += 1
                        except Exception:
                            LOGGER.warning("Caught exception when publishing metric.", exc_info=True)

                elif self.__output_location:
                    with open(self.__output_location, mode="wb") as output_file:
                        output_writers.append(output_file)

                        while not self.process_should_exit():
                            try:
                                if __streaming_worker([output_file]):
                                    self.__sequence_number += 1

                                    output_file.flush()
                            except Exception:
                                LOGGER.warning("Caught exception when publishing metric.", exc_info=True)

                elif self.__print_output:
                    output_writers.append(sys.stdout.buffer)

                    while not self.process_should_exit():
                        try:
                            if __streaming_worker(output_writers):
                                self.__sequence_number += 1
                        except Exception:
                            LOGGER.warning("Caught exception when publishing metric.", exc_info=True)
                else:
                    LOGGER.error(
                        "Unsupported monitoring configuration, metrics won't be published.",
                        tags=dict(
                            output_location=self.__output_location,
                            async_output=self.__async_output,
                            udp_output=self.__udp_output,
                            print_output=self.__print_output,
                        ),
                        exc_info=True,
                    )
                    raise InvalidArgumentError("Unsupported monitoring configuration")

            except Exception:
                LOGGER.warning(
                    "Caught exception in metrics publisher loop, sleeping for 5s before retrying.", exc_info=True
                )
                time.sleep(5)

        # We exited the publishing loop, which means we've been told to shutdown
        # by the parent process. Clean up the output writers.
        if output_file is not None:
            output_file.close()

        elif output_writers:
            for writer in output_writers:
                writer.close()
                if self.__async_output and self.__output_location:
                    async_closed = threading.Event()
                    asyncio.ensure_future(_wait_closed(async_closed, writer))
                    async_closed.wait()


MonitoringContext: "ContextVar[MonitoringBus]" = ContextVar(
    "MonitoringBus", default=MonitoringBus(MonitoringOutputType.SILENT)
)


def set_monitoring_bus(monitoring_bus: MonitoringBus) -> None:
    MonitoringContext.set(monitoring_bus)


def get_monitoring_bus() -> MonitoringBus:
    return MonitoringContext.get()
