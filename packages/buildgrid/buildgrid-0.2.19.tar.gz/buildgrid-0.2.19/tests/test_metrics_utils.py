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


import unittest
from datetime import timedelta

import pytest

from buildgrid.server.decorators import timed
from buildgrid.server.metrics_utils import create_timer_record, publish_timer_metric
from buildgrid.server.monitoring import get_monitoring_bus, set_monitoring_bus
from tests.utils.metrics import mock_create_timer_record


@pytest.fixture()
def mock_monitoring_bus():
    set_monitoring_bus(unittest.mock.Mock())


class NoInstanceNameObject:
    """This class has no self._instance_name"""

    def __init__(self):
        pass

    @timed("test")
    def test(self):
        pass

    @timed("test")
    def test_instanced(self):
        pass


class UnsetInstanceNameObject:
    """This class has a self.instance_name but it's not set."""

    def __init__(self):
        self._instance_name = None

    @timed("test")
    def test(self):
        pass

    @timed("test")
    def test_instanced(self):
        pass


def test_unset_instance_name_object(mock_monitoring_bus):
    """If an instance name isn't specified but is_instanced is set,
    the default empty instance name is used"""
    obj = UnsetInstanceNameObject()
    obj.test()
    get_monitoring_bus().send_record_nowait.assert_called_once()
    obj.test_instanced()


class NormalObject:
    """This class has self._instance_name set."""

    def __init__(self):
        self._instance_name = "foo"

    @timed("test")
    def test_return_5(self):
        return 5

    @timed("test")
    def test_instanced_return_6(self):
        return 6

    @timed("test")
    def test_raises_exception(self):
        raise ValueError

    @timed("test")
    def test_instanced_raises_exception(self):
        raise ValueError


def check_record_sent_and_reset():
    get_monitoring_bus().send_record_nowait.assert_called_once()
    get_monitoring_bus().reset_mock()


def test_normal_object(mock_monitoring_bus):
    """Test that methods which throw still have metrics published."""
    obj = NormalObject()

    assert obj.test_return_5() == 5
    check_record_sent_and_reset()

    assert obj.test_instanced_return_6() == 6
    check_record_sent_and_reset()

    with pytest.raises(ValueError):
        obj.test_raises_exception()
    check_record_sent_and_reset()

    with pytest.raises(ValueError):
        obj.test_instanced_raises_exception()
    check_record_sent_and_reset()


def test_ignored_exceptions_decorator_counter(mock_monitoring_bus):
    """Validate exceptions counter decorator doesn't publish ignored exception."""
    obj = NoInstanceNameObject()
    with pytest.raises(AttributeError):
        obj.test_ignored_exception(should_raise=True)
    get_monitoring_bus().send_record_nowait.assert_not_called()


@unittest.mock.patch("buildgrid.server.metrics_utils.create_timer_record", new=mock_create_timer_record)
def test_publish_timer_metric(mock_monitoring_bus):
    """Test publish_timer_metric method"""
    expected_timer_record = mock_create_timer_record("test")
    # Convert from the mock `Duration` back to a timedelta object
    test_timedelta = timedelta(
        seconds=expected_timer_record.duration.seconds, microseconds=expected_timer_record.duration.nanos * 1000
    )
    publish_timer_metric("test", test_timedelta)
    get_monitoring_bus().send_record_nowait.assert_called_once_with(expected_timer_record)


def test_timer_metric_clock():
    # Since we record timers in fractional seconds ensure that timedelta handles these correctly
    # when converting to duration
    a = 0.123
    b = 2.345

    d = timedelta(seconds=b - a)
    assert d.total_seconds() == 2.222
    duration = create_timer_record("test", d).duration
    assert duration.seconds == 2
    assert duration.nanos == 222000000
