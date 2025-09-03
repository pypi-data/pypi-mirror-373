import json
import re
from dataclasses import dataclass, field
from logging import DEBUG, ERROR, INFO, WARNING, getLevelName
from typing import Any, Callable

import pytest

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest, FindMissingBlobsRequest
from buildgrid.server.enums import OperationStage
from buildgrid.server.logging import JSONFormatter, buildgrid_logger

LOGGER = buildgrid_logger(__name__)

# This anchor proves that our logger is preserving the stack information correctly.
LOC = r"tests.test_logging:test_logging.py:\d+"


@dataclass
class LoggerTest:
    name: str
    expected: str
    level: int = DEBUG
    method: Callable = LOGGER.info
    exc_info: bool = False
    tags: dict[str, Any] = field(default_factory=dict)
    formatted_tags: dict[str, Any] = field(default_factory=dict)


logger_test_params = [
    #
    # Test respects logging levels for debug
    #
    LoggerTest(name="debug", level=DEBUG, method=LOGGER.debug, expected=rf"^DEBUG\s+{LOC} foo$"),
    LoggerTest(name="debug", level=INFO, method=LOGGER.debug, expected=r"^$"),
    LoggerTest(name="debug", level=WARNING, method=LOGGER.debug, expected=r"^$"),
    LoggerTest(name="debug", level=ERROR, method=LOGGER.debug, expected=r"^$"),
    #
    # Test respects logging levels for info
    #
    LoggerTest(name="info", level=DEBUG, method=LOGGER.info, expected=rf"^INFO\s+{LOC} foo$"),
    LoggerTest(name="info", level=INFO, method=LOGGER.info, expected=rf"^INFO\s+{LOC} foo$"),
    LoggerTest(name="info", level=WARNING, method=LOGGER.info, expected=r"^$"),
    LoggerTest(name="info", level=ERROR, method=LOGGER.info, expected=r"^$"),
    #
    # Test respects logging levels for warning
    #
    LoggerTest(name="warning", level=DEBUG, method=LOGGER.warning, expected=rf"^WARNING\s+{LOC} foo$"),
    LoggerTest(name="warning", level=INFO, method=LOGGER.warning, expected=rf"^WARNING\s+{LOC} foo$"),
    LoggerTest(name="warning", level=WARNING, method=LOGGER.warning, expected=rf"^WARNING\s+{LOC} foo$"),
    LoggerTest(name="warning", level=ERROR, method=LOGGER.warning, expected=r"^$"),
    #
    # Test respects logging levels for error
    #
    LoggerTest(name="error", level=DEBUG, method=LOGGER.error, expected=rf"^ERROR\s+{LOC} foo$"),
    LoggerTest(name="error", level=INFO, method=LOGGER.error, expected=rf"^ERROR\s+{LOC} foo$"),
    LoggerTest(name="error", level=WARNING, method=LOGGER.error, expected=rf"^ERROR\s+{LOC} foo$"),
    LoggerTest(name="error", level=ERROR, method=LOGGER.error, expected=rf"^ERROR\s+{LOC} foo$"),
    #
    # Test respects logging levels for exception
    #
    LoggerTest(
        name="exception", level=DEBUG, method=LOGGER.exception, expected=rf"^ERROR\s+{LOC} foo\nNoneType: None$"
    ),
    LoggerTest(
        name="exception", level=INFO, method=LOGGER.exception, expected=rf"^ERROR\s+{LOC} foo\nNoneType: None$"
    ),
    LoggerTest(
        name="exception", level=WARNING, method=LOGGER.exception, expected=rf"^ERROR\s+{LOC} foo\nNoneType: None$"
    ),
    LoggerTest(
        name="exception", level=ERROR, method=LOGGER.exception, expected=rf"^ERROR\s+{LOC} foo\nNoneType: None$"
    ),
    #
    # Test respects logging levels for exc_info on all levels
    #
    LoggerTest(
        name="exc_info",
        method=LOGGER.debug,
        exc_info=True,
        expected=rf"^DEBUG\s+{LOC} foo\nNoneType: None$",
    ),
    LoggerTest(
        name="exc_info",
        method=LOGGER.info,
        exc_info=True,
        expected=rf"^INFO\s+{LOC} foo\nNoneType: None$",
    ),
    LoggerTest(
        name="exc_info",
        method=LOGGER.warning,
        exc_info=True,
        expected=rf"^WARNING\s+{LOC} foo\nNoneType: None$",
    ),
    LoggerTest(
        name="exc_info",
        method=LOGGER.error,
        exc_info=True,
        expected=rf"^ERROR\s+{LOC} foo\nNoneType: None$",
    ),
    #
    # Test encoding of value types
    #
    LoggerTest(
        name="None",
        tags=dict(foo=None),
        expected=rf"^INFO\s+{LOC} foo foo=\"\"$",
        formatted_tags={"foo": ""},
    ),
    LoggerTest(
        name="int",
        tags=dict(foo=1234),
        expected=rf"^INFO\s+{LOC} foo foo=1234$",
        formatted_tags={"foo": 1234},
    ),
    LoggerTest(
        name="float",
        tags=dict(foo=1234.1234),
        expected=rf"^INFO\s+{LOC} foo foo=1234.12$",
        formatted_tags={"foo": "1234.12"},
    ),
    LoggerTest(
        name="Digest",
        tags=dict(foo=Digest(hash="deadbeef", size_bytes=123)),
        expected=rf'^INFO\s+{LOC} foo foo="deadbeef/123"$',
        formatted_tags={"foo": "deadbeef/123"},
    ),
    LoggerTest(
        name="Message",
        tags=dict(foo=FindMissingBlobsRequest(blob_digests=[Digest(hash="deadbeef", size_bytes=123)])),
        expected=rf'^INFO\s+{LOC} foo foo="blob_digests {{ hash: \\"deadbeef\\" size_bytes: 123 }}"$',
        formatted_tags={"foo": 'blob_digests { hash: "deadbeef" size_bytes: 123 }'},
    ),
    LoggerTest(
        name="string",
        tags=dict(foo="bar"),
        expected=rf'^INFO\s+{LOC} foo foo="bar"$',
        formatted_tags={"foo": "bar"},
    ),
    LoggerTest(
        name="string-quotes",
        tags=dict(foo='"bar"'),
        expected=rf'^INFO\s+{LOC} foo foo="\\"bar\\""$',
        formatted_tags={"foo": '"bar"'},
    ),
    LoggerTest(
        name="enum",
        tags=dict(foo=OperationStage.EXECUTING),
        expected=rf"^INFO\s+{LOC} foo foo=EXECUTING$",
        formatted_tags={"foo": "EXECUTING"},
    ),
    LoggerTest(
        name="bool",
        tags=dict(foo=True),
        expected=rf"^INFO\s+{LOC} foo foo=True$",
        formatted_tags={"foo": True},
    ),
    # Test tags with non-python variable names
    LoggerTest(
        name="tags",
        tags={"foo.bar": "fizz", "fizz.buzz": 1},
        expected=rf'^INFO\s+{LOC} foo fizz.buzz=1 foo.bar="fizz"$',
        formatted_tags={"foo.bar": "fizz", "fizz.buzz": 1},
    ),
]


@pytest.mark.parametrize("tc", logger_test_params, ids=lambda tc: tc.name)
def test_buildgrid_logger(tc, caplog):
    with caplog.at_level(tc.level):
        if tc.exc_info:
            tc.method("foo", tags=tc.tags, exc_info=tc.exc_info)
        else:
            tc.method("foo", tags=tc.tags)
    assert re.match(tc.expected, caplog.text.strip()), caplog.text


@pytest.mark.parametrize("tc", logger_test_params, ids=lambda tc: tc.name)
def test_json_formatting(tc):
    method_to_level = {
        LOGGER.debug: DEBUG,
        LOGGER.info: INFO,
        LOGGER.warning: WARNING,
        LOGGER.error: ERROR,
        LOGGER.exception: ERROR,
    }

    effective_level = method_to_level[tc.method]
    record = LOGGER._logger.makeRecord(
        name=tc.name,
        level=effective_level,
        fn=None,
        lno=0,
        msg="foo",
        args=None,
        exc_info=None,
        extra={"request_id": "---", "tags": tc.tags},
    )

    formatter = JSONFormatter()
    log_output = formatter.format(record)
    log_json = json.loads(log_output)

    assert log_json["log_level"] == getLevelName(effective_level)
    assert log_json["logger_name"] == tc.name
    assert log_json["request_id"] == "---"
    assert set(tc.formatted_tags.items()).issubset(log_json.items())


def test_duplicate_json_key():
    tc = LoggerTest(name="duplicate", expected=rf"^DEBUG\s+{LOC} foo$", tags={"logger_name": "duplicate key"})

    record = LOGGER._logger.makeRecord(
        name=tc.name,
        level=DEBUG,
        fn=None,
        lno=0,
        msg="foo",
        args=None,
        exc_info=None,
        extra={"request_id": "---", "tags": tc.tags},
    )

    formatter = JSONFormatter()
    log_output = formatter.format(record)
    log_json = json.loads(log_output)

    assert log_json["logger_name"] == tc.name
    assert log_json["tag_logger_name"] == "duplicate key"
