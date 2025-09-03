# Copyright (C) 2024 Bloomberg LP
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

import json
import logging
from enum import Enum
from types import TracebackType
from typing import Any, Union

from google.protobuf import text_format
from google.protobuf.message import Message

from buildgrid._protos.build.bazel.remote.execution.v2.remote_execution_pb2 import Digest
from buildgrid.server.settings import LOG_RECORD_FORMAT
from buildgrid.server.version import __version__

Exc = Union[
    bool,
    tuple[type[BaseException], BaseException, TracebackType | None],
    tuple[None, None, None],
    BaseException,
]

Tags = dict[str, Any]


def _str_escape(s: str) -> str:
    return str(s).replace('"', r"\"")


def _format_log_tag_value(value: Any) -> Any:
    if value is None:
        return '""'
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return f"{value:.2f}"
    elif isinstance(value, Digest):
        return f'"{value.hash}/{value.size_bytes}"'
    elif isinstance(value, Message):
        return f'"{_str_escape(text_format.MessageToString(value, as_one_line=True))}"'
    elif isinstance(value, Enum):
        return value.name
    else:
        return f'"{_str_escape(value)}"'


def _json_format_log_tag_value(value: Any) -> Any:
    if value is None:
        return ""
    elif isinstance(value, int):
        return value
    elif isinstance(value, float):
        return f"{value:.2f}"
    elif isinstance(value, Digest):
        return f"{value.hash}/{value.size_bytes}"
    elif isinstance(value, Message):
        return f"{text_format.MessageToString(value, as_one_line=True)}"
    elif isinstance(value, Enum):
        return value.name
    else:
        return f"{value}"


def _format_log_tags(tags: Tags | None) -> str:
    if not tags:
        return ""
    return "".join([f" {key}={_format_log_tag_value(value)}" for key, value in sorted(tags.items())])


def _format_message(record: logging.LogRecord) -> str:
    # LOG_RECORD_FORMAT should still be used for the message field
    msg_formatter = logging.Formatter(LOG_RECORD_FORMAT)
    return msg_formatter.format(record)


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "date": self.formatTime(record),
            "message": _format_message(record),
            "log_level": record.levelname,
            "logger_name": record.name,
            "request_id": getattr(record, "request_id", ""),
            "bgd_version": __version__,
        }

        if record_tags := getattr(record, "tags", {}):
            tags = {}
            for tag, tag_value in record_tags.items():
                if tag in log_record.keys():
                    tag = "tag_" + tag
                tags[tag] = _json_format_log_tag_value(tag_value)
            log_record.update(tags)

        return json.dumps(log_record)


class BuildgridLogger:
    def __init__(self, logger: logging.Logger) -> None:
        """
        The buildgrid logger is a helper utility wrapped around a standard logger instance.
        It allows placing key=value strings at the end of log lines, reducing boilerplate in
        displaying values and adding standardization to our log lines. Within each logging method,
        tags may be added by setting the "tags" argument.

        Each logger is set to log at stacklevel=2 such that function names and source line numbers
        show the line at which this utility is invoked.

        Special encoding rules for tag values:
         - int: reported as is. `value=1`
         - float: rounded to the nearest two decimals. `value=1.23`
         - Digest: unpacked as hash/size. `value=deadbeef/123`
         - proto.Message: text_format, escaped, and quoted. `value="blob_digests { hash: \"deadbeef\" }"`
         - Enum: attribute name is used. `value=OK`
         - others: converted to str, escaped, and quoted. `value="foo: \"bar\""`

        Encoding is only performed if logging is enabled for that level.
        """
        self._logger = logger

    def is_enabled_for(self, level: int) -> bool:
        return self._logger.isEnabledFor(level)

    def debug(self, msg: Any, *, exc_info: Exc | None = None, tags: Tags | None = None) -> None:
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(
                str(msg) + _format_log_tags(tags), extra={"tags": tags or {}}, exc_info=exc_info, stacklevel=2
            )

    def info(self, msg: Any, *, exc_info: Exc | None = None, tags: Tags | None = None) -> None:
        if self._logger.isEnabledFor(logging.INFO):
            self._logger.info(
                str(msg) + _format_log_tags(tags), extra={"tags": tags or {}}, exc_info=exc_info, stacklevel=2
            )

    def warning(self, msg: Any, *, exc_info: Exc | None = None, tags: Tags | None = None) -> None:
        if self._logger.isEnabledFor(logging.WARNING):
            self._logger.warning(
                str(msg) + _format_log_tags(tags), extra={"tags": tags or {}}, exc_info=exc_info, stacklevel=2
            )

    def error(self, msg: Any, *, exc_info: Exc | None = None, tags: Tags | None = None) -> None:
        if self._logger.isEnabledFor(logging.ERROR):
            self._logger.error(
                str(msg) + _format_log_tags(tags), extra={"tags": tags or {}}, exc_info=exc_info, stacklevel=2
            )

    def exception(self, msg: Any, *, exc_info: Exc | None = True, tags: Tags | None = None) -> None:
        if self._logger.isEnabledFor(logging.ERROR):
            # Note we call error here instead of exception.
            # logger.exception is a helper around calling error with exc_info defaulting to True.
            # On python<3.11 that helper causes the stacklevel to report incorrectly.
            self._logger.error(
                str(msg) + _format_log_tags(tags), extra={"tags": tags or {}}, exc_info=exc_info, stacklevel=2
            )


def buildgrid_logger(name: str) -> BuildgridLogger:
    return BuildgridLogger(logging.getLogger(name))
