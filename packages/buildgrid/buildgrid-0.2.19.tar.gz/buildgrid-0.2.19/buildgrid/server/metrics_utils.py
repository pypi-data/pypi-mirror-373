# Copyright (C) 2020 Bloomberg LP
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

import time
from contextlib import contextmanager
from datetime import timedelta
from typing import Iterator

from buildgrid._protos.build.buildgrid.monitoring_pb2 import MetricRecord
from buildgrid.server.context import try_current_instance, try_current_method, try_current_service
from buildgrid.server.enums import MetricRecordType
from buildgrid.server.monitoring import get_monitoring_bus


def _format_metadata(metadata: dict[str, str] | None = None) -> dict[str, str]:
    if metadata is None:
        metadata = {}

    metadata = {key: value for key, value in metadata.items() if value is not None}

    # If an instance name is not specifically set, try to find one from the context.
    if "instanceName" not in metadata:
        if (instance_name := try_current_instance()) is not None:
            metadata["instanceName"] = instance_name

    # If the instance name is set and empty, set it to a default for easy querying.
    if metadata.get("instanceName") == "":
        metadata["instanceName"] = "unnamed"

    # If a service name is not specifically set, try to find one from the context.
    if "serviceName" not in metadata:
        if (service := try_current_service()) is not None:
            metadata["serviceName"] = service

    # If a method name is not specifically set, try to find one from the context.
    if "method" not in metadata:
        if (method := try_current_method()) is not None:
            metadata["method"] = method

    return metadata


def create_counter_record(name: str, count: float, **metadata: str) -> MetricRecord:
    counter_record = MetricRecord()

    counter_record.creation_timestamp.GetCurrentTime()
    counter_record.type = MetricRecordType.COUNTER.value
    counter_record.name = name
    counter_record.count = count
    counter_record.metadata.update(_format_metadata(metadata))

    return counter_record


def create_gauge_record(name: str, value: float, **metadata: str) -> MetricRecord:
    gauge_record = MetricRecord()

    gauge_record.creation_timestamp.GetCurrentTime()
    gauge_record.type = MetricRecordType.GAUGE.value
    gauge_record.name = name
    gauge_record.value = value
    gauge_record.metadata.update(_format_metadata(metadata))

    return gauge_record


def create_timer_record(name: str, duration: timedelta, **metadata: str) -> MetricRecord:
    timer_record = MetricRecord()

    timer_record.creation_timestamp.GetCurrentTime()
    timer_record.type = MetricRecordType.TIMER.value
    timer_record.name = name
    timer_record.duration.FromTimedelta(duration)
    timer_record.metadata.update(_format_metadata(metadata))

    return timer_record


def create_distribution_record(name: str, value: float, **metadata: str) -> MetricRecord:
    dist_record = MetricRecord()

    dist_record.creation_timestamp.GetCurrentTime()
    dist_record.type = MetricRecordType.DISTRIBUTION.value
    dist_record.name = name
    dist_record.count = value
    dist_record.metadata.update(_format_metadata(metadata))

    return dist_record


def publish_counter_metric(name: str, count: float, **metadata: str) -> None:
    record = create_counter_record(name, count, **metadata)
    monitoring_bus = get_monitoring_bus()
    monitoring_bus.send_record_nowait(record)


def publish_gauge_metric(name: str, value: float, **metadata: str) -> None:
    record = create_gauge_record(name, value, **metadata)
    monitoring_bus = get_monitoring_bus()
    monitoring_bus.send_record_nowait(record)


def publish_timer_metric(name: str, duration: timedelta, **metadata: str) -> None:
    record = create_timer_record(name, duration, **metadata)
    monitoring_bus = get_monitoring_bus()
    monitoring_bus.send_record_nowait(record)


def publish_distribution_metric(name: str, count: float, **metadata: str) -> None:
    record = create_distribution_record(name, float(count), **metadata)
    monitoring_bus = get_monitoring_bus()
    monitoring_bus.send_record_nowait(record)


@contextmanager
def timer(metric_name: str, **tags: str) -> Iterator[None]:
    start_time = time.perf_counter()
    error = "None"
    try:
        yield
    except Exception as e:
        error = e.__class__.__name__
        raise
    finally:
        run_time = timedelta(seconds=time.perf_counter() - start_time)
        publish_timer_metric(metric_name, run_time, exceptionType=error, **tags)
