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


import logging
import logging.handlers
import os
import signal
import sys
import threading
import time
import traceback
from collections import defaultdict
from contextlib import ExitStack
from datetime import datetime
from queue import Empty, Queue
from types import FrameType
from typing import Any, Iterable, Sequence

import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from grpc_reflection.v1alpha import reflection

from buildgrid._protos.build.buildgrid.monitoring_pb2 import LogRecord
from buildgrid.server.actioncache.service import ActionCacheService
from buildgrid.server.bots.service import BotsService
from buildgrid.server.build_events.service import PublishBuildEventService, QueryBuildEventsService
from buildgrid.server.capabilities.instance import CapabilitiesInstance
from buildgrid.server.capabilities.service import CapabilitiesService
from buildgrid.server.cas.service import ByteStreamService, ContentAddressableStorageService
from buildgrid.server.context import instance_context
from buildgrid.server.controller import ExecutionController
from buildgrid.server.enums import BotStatus, LogRecordLevel, MetricCategories
from buildgrid.server.exceptions import PermissionDeniedError, ShutdownDelayedError
from buildgrid.server.execution.service import ExecutionService
from buildgrid.server.introspection.service import IntrospectionService
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_gauge_metric
from buildgrid.server.monitoring import get_monitoring_bus
from buildgrid.server.operations.service import OperationsService
from buildgrid.server.scheduler import Scheduler, SchedulerMetrics
from buildgrid.server.servicer import Instance, InstancedServicer
from buildgrid.server.settings import LOG_RECORD_FORMAT, MIN_THREAD_POOL_SIZE, MONITORING_PERIOD, SHUTDOWN_ALARM_DELAY
from buildgrid.server.threading import ContextThreadPoolExecutor, ContextWorker
from buildgrid.server.types import OnServerStartCallback, PortAssignedCallback

LOGGER = buildgrid_logger(__name__)


def load_tls_server_credentials(
    server_key: str | None = None, server_cert: str | None = None, client_certs: str | None = None
) -> grpc.ServerCredentials | None:
    """Looks-up and loads TLS server gRPC credentials.

    Every private and public keys are expected to be PEM-encoded.

    Args:
        server_key(str): private server key file path.
        server_cert(str): public server certificate file path.
        client_certs(str): public client certificates file path.

    Returns:
        :obj:`ServerCredentials`: The credentials for use for a
        TLS-encrypted gRPC server channel.
    """
    if not server_key or not os.path.exists(server_key):
        return None

    if not server_cert or not os.path.exists(server_cert):
        return None

    with open(server_key, "rb") as f:
        server_key_pem = f.read()
    with open(server_cert, "rb") as f:
        server_cert_pem = f.read()

    if client_certs and os.path.exists(client_certs):
        with open(client_certs, "rb") as f:
            client_certs_pem = f.read()
    else:
        client_certs_pem = None
        client_certs = None

    credentials = grpc.ssl_server_credentials(
        [(server_key_pem, server_cert_pem)], root_certificates=client_certs_pem, require_client_auth=bool(client_certs)
    )

    # TODO: Fix this (missing stubs?) "ServerCredentials" has no attribute
    credentials.server_key = server_key  # type: ignore[attr-defined]
    credentials.server_cert = server_cert  # type: ignore[attr-defined]
    credentials.client_certs = client_certs  # type: ignore[attr-defined]

    return credentials


class Server:
    """Creates a BuildGrid server instance.

    The :class:`Server` class binds together all the gRPC services.
    """

    def __init__(
        self,
        server_reflection: bool,
        grpc_compression: grpc.Compression,
        is_instrumented: bool,
        grpc_server_options: Sequence[tuple[str, Any]] | None,
        max_workers: int | None,
        monitoring_period: float = MONITORING_PERIOD,
    ):
        self._stack = ExitStack()

        self._server_reflection = server_reflection
        self._grpc_compression = grpc_compression
        self._is_instrumented = is_instrumented
        self._grpc_server_options = grpc_server_options

        self._action_cache_service = ActionCacheService()
        self._bots_service = BotsService()
        self._bytestream_service = ByteStreamService()
        self._capabilities_service = CapabilitiesService()
        self._cas_service = ContentAddressableStorageService()
        self._execution_service = ExecutionService()
        self._operations_service = OperationsService()
        self._introspection_service = IntrospectionService()

        # Special cases
        self._build_events_service = PublishBuildEventService()
        self._query_build_events_service = QueryBuildEventsService()
        self._health_service = health.HealthServicer()

        self._schedulers: dict[str, set[Scheduler]] = defaultdict(set)

        self._ports: list[tuple[str, dict[str, str] | None]] = []
        self._port_map: dict[str, int] = {}

        self._logging_queue: Queue[Any] = Queue()
        self._monitoring_period = monitoring_period

        if max_workers is None:
            # Use max_workers default from Python 3.4+
            max_workers = max(MIN_THREAD_POOL_SIZE, (os.cpu_count() or 1) * 5)

        elif max_workers < MIN_THREAD_POOL_SIZE:
            LOGGER.warning(
                "Specified thread-limit is too small, bumping it.",
                tags=dict(requested_thread_limit=max_workers, new_thread_limit=MIN_THREAD_POOL_SIZE),
            )
            # Enforce a minumun for max_workers
            max_workers = MIN_THREAD_POOL_SIZE

        self._max_grpc_workers = max_workers

    def register_instance(self, instance_name: str, instance: Instance) -> None:
        """
        Register an instance with the server. Handled the logic of mapping instances to the
        correct servicer container.

        Args:
            instance_name (str): The name of the instance.

            instance (Instance): The instance implementation.
        """

        # Special case to handle the ExecutionController which combines the service interfaces.
        if isinstance(instance, ExecutionController):
            if bots_interface := instance.bots_interface:
                self.register_instance(instance_name, bots_interface)
            if execution_instance := instance.execution_instance:
                self.register_instance(instance_name, execution_instance)
            if operations_instance := instance.operations_instance:
                self.register_instance(instance_name, operations_instance)

        elif action_instance := self._action_cache_service.cast(instance):
            self._action_cache_service.add_instance(instance_name, action_instance)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_action_cache_instance(action_instance)

        elif bots_instance := self._bots_service.cast(instance):
            self._bots_service.add_instance(instance_name, bots_instance)
            self._schedulers[instance_name].add(bots_instance.scheduler)

        elif bytestream_instance := self._bytestream_service.cast(instance):
            self._bytestream_service.add_instance(instance_name, bytestream_instance)

        elif cas_instance := self._cas_service.cast(instance):
            self._cas_service.add_instance(instance_name, cas_instance)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_cas_instance(cas_instance)

        elif execution_instance := self._execution_service.cast(instance):
            self._execution_service.add_instance(instance_name, execution_instance)
            self._schedulers[instance_name].add(execution_instance.scheduler)
            capabilities = self._capabilities_service.instances.setdefault(instance_name, CapabilitiesInstance())
            capabilities.add_execution_instance(execution_instance)

        elif operations_instance := self._operations_service.cast(instance):
            self._operations_service.add_instance(instance_name, operations_instance)

        elif introspection_instance := self._introspection_service.cast(instance):
            self._introspection_service.add_instance(instance_name, introspection_instance)

        # The Build Events Services have no support for instance names, so this
        # is a bit of a special case where the storage backend itself is the
        # trigger for creating the gRPC services.
        elif instance.SERVICE_NAME == "BuildEvents":
            self._build_events_service.add_instance("", instance)  # type: ignore[arg-type]
            self._query_build_events_service.add_instance("", instance)  # type: ignore[arg-type]

        else:
            raise ValueError(f"Instance of type {type(instance)} not supported by {type(self)}")

    @property
    def _services(self) -> Iterable[InstancedServicer[Any]]:
        return (
            self._action_cache_service,
            self._bots_service,
            self._bytestream_service,
            self._capabilities_service,
            self._cas_service,
            self._execution_service,
            self._operations_service,
            self._introspection_service,
            # Special cases
            self._build_events_service,
            self._query_build_events_service,
        )

    def add_port(self, address: str, credentials: dict[str, str] | None) -> None:
        """Adds a port to the server.

        Must be called before the server starts. If a credentials object exists,
        it will make a secure port.

        Args:
            address (str): The address with port number.
            credentials (:obj:`grpc.ChannelCredentials`): Credentials object.
        """
        self._ports.append((address, credentials))

    def start(
        self,
        *,
        on_server_start_cb: OnServerStartCallback | None = None,
        port_assigned_callback: PortAssignedCallback | None = None,
        run_forever: bool = True,
    ) -> None:
        """Starts the BuildGrid server.

        BuildGrid server startup consists of 3 stages,

        1. Starting logging and monitoring

        This step starts up the logging coroutine, the periodic status metrics
        coroutine, and the monitoring bus' publishing subprocess. Since this
        step involves forking, anything not fork-safe needs to be done *after*
        this step.

        2. Instantiate gRPC

        This step instantiates the gRPC server, and tells all the instances
        which have been attached to the server to instantiate their gRPC
        objects. It is also responsible for creating the various service
        objects and connecting them to the server and the instances.

        After this step, gRPC core is running and its no longer safe to fork
        the process.

        3. Start instances

        Several of BuildGrid's services use background threads that need to
        be explicitly started when BuildGrid starts up. Rather than doing
        this at configuration parsing time, this step provides a hook for
        services to start up in a more organised fashion.

        4. Start the gRPC server

        The final step is starting up the gRPC server. The callback passed in
        via ``on_server_start_cb`` is executed in this step once the server
        has started. After this point BuildGrid is ready to serve requests.

        The final thing done by this method is adding a ``SIGTERM`` handler
        which calls the ``Server.stop`` method to the event loop, and then
        that loop is started up using ``run_forever()``.

        Args:
            on_server_start_cb (Callable): Callback function to execute once
                the gRPC server has started up.
            port_assigned_callback (Callable): Callback function to execute
                once the gRPC server has started up. The mapping of addresses
                to ports is passed to this callback.

        """
        # 1. Start logging and monitoring
        self._stack.enter_context(
            ContextWorker(
                self._logging_worker,
                "ServerLogger",
                # Add a dummy value to the queue to unblock the get call.
                on_shutdown_requested=lambda: self._logging_queue.put(None),
            )
        )
        if self._is_instrumented:
            self._stack.enter_context(get_monitoring_bus())
            self._stack.enter_context(ContextWorker(self._state_monitoring_worker, "ServerMonitor"))

        # 2. Instantiate gRPC objects
        grpc_server = self.setup_grpc()

        # 3. Start background threads
        for service in self._services:
            self._stack.enter_context(service)

        # 4. Start the gRPC server.
        grpc_server.start()
        self._stack.callback(grpc_server.stop, None)

        if on_server_start_cb:
            on_server_start_cb()
        if port_assigned_callback:
            port_assigned_callback(port_map=self._port_map)

        # Add the stop handler and run the event loop
        if run_forever:
            grpc_server.wait_for_termination()

    def setup_grpc(self) -> grpc.Server:
        """Instantiate the gRPC objects.

        This creates the gRPC server, and causes the instances attached to
        this server to instantiate any gRPC channels they need. This also
        sets up the services which route to those instances, and sets up
        gRPC reflection.

        """
        LOGGER.info(
            "Setting up gRPC server.",
            tags=dict(
                maximum_concurrent_rpcs=self._max_grpc_workers,
                compression=self._grpc_compression,
                options=self._grpc_server_options,
            ),
        )

        grpc_server = grpc.server(
            ContextThreadPoolExecutor(self._max_grpc_workers, "gRPC_Executor", immediate_copy=True),
            maximum_concurrent_rpcs=self._max_grpc_workers,
            compression=self._grpc_compression,
            options=self._grpc_server_options,
        )

        # Add the requested ports to the gRPC server
        for address, credentials in self._ports:
            port_number = 0
            if credentials is not None:
                LOGGER.info("Adding secure connection.", tags=dict(address=address))
                server_key = credentials.get("tls-server-key")
                server_cert = credentials.get("tls-server-cert")
                client_certs = credentials.get("tls-client-certs")
                server_credentials = load_tls_server_credentials(
                    server_cert=server_cert, server_key=server_key, client_certs=client_certs
                )
                # TODO should this error out??
                if server_credentials:
                    port_number = grpc_server.add_secure_port(address, server_credentials)

            else:
                LOGGER.info("Adding insecure connection.", tags=dict(address=address))
                port_number = grpc_server.add_insecure_port(address)

            if not port_number:
                raise PermissionDeniedError("Unable to configure socket")

            self._port_map[address] = port_number

        for service in self._services:
            service.setup_grpc(grpc_server)
            if service.enabled:
                self._health_service.set(service.FULL_NAME, health_pb2.HealthCheckResponse.SERVING)

        if self._server_reflection:
            reflection_services = [service.FULL_NAME for service in self._services if service.enabled]
            LOGGER.info("Server reflection is enabled.", tags=dict(reflection_services=reflection_services))
            reflection.enable_server_reflection([reflection.SERVICE_NAME] + reflection_services, grpc_server)
        else:
            LOGGER.info("Server reflection is not enabled.")

        health_pb2_grpc.add_HealthServicer_to_server(self._health_service, grpc_server)

        return grpc_server

    def stop(self) -> None:
        LOGGER.info("Stopping BuildGrid server.")
        self._health_service.enter_graceful_shutdown()

        def alarm_handler(_signal: int, _frame: FrameType | None) -> None:
            LOGGER.warning(
                "Shutdown still ongoing after shutdown delay.",
                tags=dict(
                    shutdown_alarm_delay_seconds=SHUTDOWN_ALARM_DELAY, active_thread_count=threading.active_count()
                ),
            )
            for thread in threading.enumerate():
                if thread.ident is not None:
                    tb = "".join(traceback.format_stack(sys._current_frames()[thread.ident]))
                    LOGGER.warning(f"Thread {thread.name} ({thread.ident})\n{tb}")
            raise ShutdownDelayedError(f"Shutdown took more than {SHUTDOWN_ALARM_DELAY} seconds")

        LOGGER.debug("Setting alarm for delayed shutdown.")
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(SHUTDOWN_ALARM_DELAY)

        try:
            self._stack.close()
        except ShutdownDelayedError:
            # Do nothing, this was raised to interrupt a potentially stuck stack close
            pass

    def _logging_worker(self, shutdown_requested: threading.Event) -> None:
        """Publishes log records to the monitoring bus."""

        logging_handler = logging.handlers.QueueHandler(self._logging_queue)

        # Setup the main logging handler:
        root_logger = logging.getLogger()

        for log_filter in root_logger.filters[:]:
            logging_handler.addFilter(log_filter)
            root_logger.removeFilter(log_filter)

        # Default formatter before extracting from root_logger handlers
        logging_formatter = logging.Formatter(fmt=LOG_RECORD_FORMAT)

        for root_log_handler in root_logger.handlers[:]:
            for log_filter in root_log_handler.filters[:]:
                logging_handler.addFilter(log_filter)
            if root_log_handler.formatter:
                logging_formatter = root_log_handler.formatter
            root_logger.removeHandler(root_log_handler)
        root_logger.addHandler(logging_handler)

        def logging_worker() -> None:
            monitoring_bus = get_monitoring_bus()

            try:
                log_record = self._logging_queue.get(timeout=self._monitoring_period)
            except Empty:
                return
            if log_record is None:
                return

            # Print log records to stdout, if required:
            if not self._is_instrumented or not monitoring_bus.prints_records:
                record = logging_formatter.format(log_record)
                # TODO: Investigate if async write would be worth here.
                sys.stdout.write(f"{record}\n")
                sys.stdout.flush()

            # Emit a log record if server is instrumented:
            if self._is_instrumented:
                log_record_level = LogRecordLevel(int(log_record.levelno / 10))
                log_record_creation_time = datetime.fromtimestamp(log_record.created)
                # logging.LogRecord.extra must be a str to str dict:
                if "extra" in log_record.__dict__ and log_record.extra:
                    log_record_metadata = log_record.extra
                else:
                    log_record_metadata = None
                forged_record = self._forge_log_record(
                    domain=log_record.name,
                    level=log_record_level,
                    message=log_record.message,
                    creation_time=log_record_creation_time,
                    metadata=log_record_metadata,
                )
                monitoring_bus.send_record_nowait(forged_record)

        while not shutdown_requested.is_set():
            try:
                logging_worker()
            except Exception:
                # The thread shouldn't exit on exceptions, but output the exception so that
                # it can be found in the logs.
                #
                # Note, we DO NOT use `LOGGER` here, because we don't want to write
                # anything new to the logging queue in case the Exception isn't some transient
                # issue.
                try:
                    sys.stdout.write("Exception in logging worker\n")
                    sys.stdout.flush()
                    traceback.print_exc()
                except Exception:
                    # There's not a lot we can do at this point really.
                    pass

        if shutdown_requested.is_set():
            # Reset logging, so any logging after shutting down the logging worker
            # still gets written to stdout and the queue doesn't get any more logs
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setFormatter(logging_formatter)
            root_logger = logging.getLogger()

            for log_filter in root_logger.filters[:]:
                stream_handler.addFilter(log_filter)
                root_logger.removeFilter(log_filter)

            for log_handler in root_logger.handlers[:]:
                for log_filter in log_handler.filters[:]:
                    stream_handler.addFilter(log_filter)
                root_logger.removeHandler(log_handler)
            root_logger.addHandler(stream_handler)

            # Drain the log message queue
            while self._logging_queue.qsize() > 0:
                logging_worker()

    def _forge_log_record(
        self,
        *,
        domain: str,
        level: LogRecordLevel,
        message: str,
        creation_time: datetime,
        metadata: dict[str, str] | None = None,
    ) -> LogRecord:
        log_record = LogRecord()

        log_record.creation_timestamp.FromDatetime(creation_time)
        log_record.domain = domain
        log_record.level = level.value
        log_record.message = message
        if metadata is not None:
            log_record.metadata.update(metadata)

        return log_record

    def _state_monitoring_worker(self, shutdown_requested: threading.Event) -> None:
        """Periodically publishes state metrics to the monitoring bus."""
        while not shutdown_requested.is_set():
            start = time.time()
            try:
                if self._execution_service.enabled:
                    for instance_name in self._execution_service.instances:
                        self._publish_client_metrics_for_instance(instance_name)

                if self._bots_service.enabled:
                    for instance_name in self._bots_service.instances:
                        self._publish_bot_metrics_for_instance(instance_name)

                if self._schedulers:
                    for instance_name in self._schedulers:
                        self._publish_scheduler_metrics_for_instance(instance_name)
            except Exception:
                # The thread shouldn't exit on exceptions, but log at a severe enough level
                # that it doesn't get lost in logs
                LOGGER.exception("Exception while gathering state metrics.")

            end = time.time()
            shutdown_requested.wait(timeout=max(0, self._monitoring_period - (end - start)))

    def _publish_client_metrics_for_instance(self, instance_name: str) -> None:
        """Queries the number of clients connected for a given instance"""
        with instance_context(instance_name):
            n_clients = self._execution_service.query_connected_clients_for_instance(instance_name)
            publish_gauge_metric(METRIC.CONNECTIONS.CLIENT_COUNT, n_clients)

    def _publish_bot_metrics_for_instance(self, instance_name: str) -> None:
        with instance_context(instance_name):
            # Bots Count
            bot_metrics = self._bots_service.get_bot_status_metrics(instance_name)

            # Post total bot counts per status
            for bot_status, number_of_bots in bot_metrics["bots_total"].items():
                publish_gauge_metric(METRIC.SCHEDULER.BOTS_COUNT, number_of_bots, state=BotStatus(bot_status).name)

            # Post bot counts for each propertyLabel
            for [bot_status, property_label], number_of_bots in bot_metrics["bots_per_property_label"].items():
                publish_gauge_metric(
                    METRIC.SCHEDULER.BOTS_COUNT,
                    number_of_bots,
                    state=BotStatus(bot_status).name,
                    propertyLabel=property_label,
                )

            n_workers = self._bots_service.query_connected_bots_for_instance(instance_name)
            publish_gauge_metric(METRIC.CONNECTIONS.WORKER_COUNT, n_workers)

    def _publish_scheduler_metrics_for_instance(self, instance_name: str) -> None:
        with instance_context(instance_name):
            # Since multiple schedulers may be active for this instance, but should
            # be using the same database, just use the first one
            scheduler_metrics: SchedulerMetrics | None = None
            for scheduler in self._schedulers[instance_name]:
                scheduler_metrics = scheduler.get_metrics(instance_name)
            if scheduler_metrics is None:
                return

            # Jobs
            for [stage_name, property_label], number_of_jobs in scheduler_metrics[MetricCategories.JOBS.value].items():
                publish_gauge_metric(
                    METRIC.SCHEDULER.JOB_COUNT, number_of_jobs, state=stage_name, propertyLabel=property_label
                )
