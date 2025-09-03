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

"""Holds constants and utility functions for the SQL scheduler."""


import operator
import random
from collections import namedtuple
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, cast

from sqlalchemy import ColumnElement, UnaryExpression
from sqlalchemy.engine import Engine
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.session import Session as SessionType
from sqlalchemy.sql.expression import and_, or_

from buildgrid.server.exceptions import InvalidArgumentError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.operations.filtering import OperationFilter, SortKey
from buildgrid.server.sql.models import (
    ClientIdentityEntry,
    JobEntry,
    OperationEntry,
    PlatformEntry,
    RequestMetadataEntry,
)

LOGGER = buildgrid_logger(__name__)


DATETIME_FORMAT = "%Y-%m-%d-%H-%M-%S-%f"


LIST_OPERATIONS_PARAMETER_MODEL_MAP = cast(
    dict[str, InstrumentedAttribute[Any]],
    {
        "stage": JobEntry.stage,
        "name": OperationEntry.name,
        "queued_time": JobEntry.queued_timestamp,
        "start_time": JobEntry.worker_start_timestamp,
        "completed_time": JobEntry.worker_completed_timestamp,
        "input_fetch_start_time": JobEntry.input_fetch_start_timestamp,
        "input_fetch_completed_time": JobEntry.input_fetch_completed_timestamp,
        "output_upload_start_time": JobEntry.output_upload_start_timestamp,
        "output_upload_completed_time": JobEntry.output_upload_completed_timestamp,
        "execution_start_time": JobEntry.execution_start_timestamp,
        "execution_completed_time": JobEntry.execution_completed_timestamp,
        "invocation_id": RequestMetadataEntry.invocation_id,
        "correlated_invocations_id": RequestMetadataEntry.correlated_invocations_id,
        "tool_name": RequestMetadataEntry.tool_name,
        "tool_version": RequestMetadataEntry.tool_version,
        "action_mnemonic": RequestMetadataEntry.action_mnemonic,
        "target_id": RequestMetadataEntry.target_id,
        "configuration_id": RequestMetadataEntry.configuration_id,
        "action_digest": JobEntry.action_digest,
        "command": JobEntry.command,
        "platform": PlatformEntry.key,
        "platform-value": PlatformEntry.value,
        "client_workflow": ClientIdentityEntry.workflow,
        "client_actor": ClientIdentityEntry.actor,
        "client_subject": ClientIdentityEntry.subject,
    },
)


SortKeySpec = namedtuple("SortKeySpec", ["column_name", "table_name"])


LIST_OPERATIONS_SORT_KEYS = {
    "stage": SortKeySpec("stage", JobEntry.__tablename__),
    "name": SortKeySpec("name", OperationEntry.__tablename__),
    "queued_time": SortKeySpec("queued_timestamp", JobEntry.__tablename__),
    "start_time": SortKeySpec("worker_start_timestamp", JobEntry.__tablename__),
    "completed_time": SortKeySpec("worker_completed_timestamp", JobEntry.__tablename__),
    "action_digest": SortKeySpec("action_digest", JobEntry.__tablename__),
    "command": SortKeySpec("command", JobEntry.__tablename__),
}


def is_sqlite_connection_string(connection_string: str) -> bool:
    if connection_string:
        return connection_string.startswith("sqlite")
    return False


def is_psycopg2_connection_string(connection_string: str) -> bool:
    if connection_string:
        if connection_string.startswith("postgresql:"):
            return True
        if connection_string.startswith("postgresql+psycopg2:"):
            return True
    return False


def is_sqlite_inmemory_connection_string(full_connection_string: str) -> bool:
    if is_sqlite_connection_string(full_connection_string):
        # Valid connection_strings for in-memory SQLite which we don't support could look like:
        # "sqlite:///file:memdb1?option=value&cache=shared&mode=memory",
        # "sqlite:///file:memdb1?mode=memory&cache=shared",
        # "sqlite:///file:memdb1?cache=shared&mode=memory",
        # "sqlite:///file::memory:?cache=shared",
        # "sqlite:///file::memory:",
        # "sqlite:///:memory:",
        # "sqlite:///",
        # "sqlite://"
        # ref: https://www.sqlite.org/inmemorydb.html
        # Note that a user can also specify drivers, so prefix could become 'sqlite+driver:///'
        connection_string = full_connection_string

        uri_split_index = connection_string.find("?")
        if uri_split_index != -1:
            connection_string = connection_string[0:uri_split_index]

        if connection_string.endswith((":memory:", ":///", "://")):
            return True
        elif uri_split_index != -1:
            opts = full_connection_string[uri_split_index + 1 :].split("&")
            if "mode=memory" in opts:
                return True

    return False


class SQLPoolDisposeHelper:
    """Helper class for disposing of SQL session connections"""

    def __init__(
        self,
        cooldown_time_in_secs: int,
        cooldown_jitter_base_in_secs: int,
        min_time_between_dispose_in_minutes: int,
        sql_engine: Engine,
    ) -> None:
        self._cooldown_time_in_secs = cooldown_time_in_secs
        self._cooldown_jitter_base_in_secs = cooldown_jitter_base_in_secs
        self._min_time_between_dispose_in_minutes = min_time_between_dispose_in_minutes
        self._last_pool_dispose_time: datetime | None = None
        self._last_pool_dispose_time_lock = Lock()
        self._sql_engine = sql_engine
        self._dispose_pool_on_exceptions: tuple[Any, ...] = tuple()
        if self._sql_engine.dialect.name == "postgresql":
            import psycopg2

            self._dispose_pool_on_exceptions = (psycopg2.errors.ReadOnlySqlTransaction, psycopg2.errors.AdminShutdown)

    def check_dispose_pool(self, session: SessionType, e: Exception) -> bool:
        """For selected exceptions invalidate the SQL session
        - returns True when a transient sql connection error is detected
        - returns False otherwise
        """

        # Only do this if the config is relevant
        if not self._dispose_pool_on_exceptions:
            return False

        # Make sure we have a SQL-related cause to check, otherwise skip
        if e.__cause__ and not isinstance(e.__cause__, Exception):
            return False

        cause_type = type(e.__cause__)
        # Let's see if this exception is related to known disconnect exceptions
        is_connection_error = cause_type in self._dispose_pool_on_exceptions
        if not is_connection_error:
            return False

        # Make sure this connection will not be re-used
        session.invalidate()
        LOGGER.info(
            "Detected a SQL exception related to the connection. Invalidating this connection.",
            tags=dict(exception=cause_type.__name__),
        )

        # Only allow disposal every self.__min_time_between_dispose_in_minutes
        now = datetime.utcnow()
        only_if_after = None

        # Check if we should dispose the rest of the checked in connections
        with self._last_pool_dispose_time_lock:
            if self._last_pool_dispose_time:
                only_if_after = self._last_pool_dispose_time + timedelta(
                    minutes=self._min_time_between_dispose_in_minutes
                )
            if only_if_after and now < only_if_after:
                return True

            # OK, we haven't disposed the pool recently
            self._last_pool_dispose_time = now
            LOGGER.info(
                "Disposing connection pool. New requests will have a fresh SQL connection.",
                tags=dict(cooldown_time_in_secs=self._cooldown_time_in_secs),
            )
            self._sql_engine.dispose()

        return True

    def time_until_active_pool(self) -> timedelta:
        """The time at which the pool is expected to become
        active after a pool disposal. This adds small amounts of jitter
        to help spread out load due to retrying clients
        """
        if self._last_pool_dispose_time:
            time_til_active = self._last_pool_dispose_time + timedelta(seconds=self._cooldown_time_in_secs)
            if datetime.utcnow() < time_til_active:
                return timedelta(
                    seconds=self._cooldown_time_in_secs
                    + random.uniform(-self._cooldown_jitter_base_in_secs, self._cooldown_jitter_base_in_secs)
                )
        return timedelta(seconds=0)


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError(f"invalid truth value {val}")


def parse_list_operations_sort_value(value: str, column: InstrumentedAttribute[Any]) -> Any:
    """Convert the string representation of a value to the proper Python type."""
    python_type = column.expression.type.python_type
    if python_type == datetime:
        return datetime.strptime(value, DATETIME_FORMAT)
    elif python_type == bool:
        # Using this distutils function to cover a few different bool representations
        return strtobool(value)
    else:
        return python_type(value)


def dump_list_operations_token_value(token_value: Any) -> str:
    """Convert a value to a string for use in the page_token."""
    if isinstance(token_value, datetime):
        return datetime.strftime(token_value, DATETIME_FORMAT)
    else:
        return str(token_value)


def build_pagination_clause_for_sort_key(
    sort_value: Any, previous_sort_values: list[Any], sort_keys: list[SortKey]
) -> ColumnElement[bool]:
    """Build part of a filter clause to figure out the starting point of the page given
    by the page_token. See the docstring of build_page_filter for more details."""
    if len(sort_keys) <= len(previous_sort_values):
        raise ValueError("Not enough keys to unpack")

    filter_clause_list = []
    for i, previous_sort_value in enumerate(previous_sort_values):
        previous_sort_col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_keys[i].name]
        filter_clause_list.append(previous_sort_col == previous_sort_value)
    sort_key = sort_keys[len(previous_sort_values)]
    sort_col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
    if sort_key.descending:
        filter_clause_list.append(sort_col < sort_value)
    else:
        filter_clause_list.append(sort_col > sort_value)
    return and_(*filter_clause_list)


def build_page_filter(page_token: str, sort_keys: list[SortKey]) -> ColumnElement[bool]:
    """Build a filter to determine the starting point of the rows to fetch, based
    on the page_token.

    The page_token is directly related to the sort order, and in this way it acts as a
    "cursor." It is given in the format Xval|Yval|Zval|..., where each element is a value
    corresponding to an orderable column in the database. If the corresponding rows are
    X, Y, and Z, then X is the primary sort key, with Y breaking ties between X, and Z
    breaking ties between X and Y. The corresponding filter clause is then:

    (X > Xval) OR (X == XVal AND Y > Yval) OR (X == Xval AND Y == Yval AND Z > Zval) ...
    """
    # The page token is used as a "cursor" to determine the starting point
    # of the rows to fetch. It is derived from the sort keys.
    token_elements = page_token.split("|")
    if len(token_elements) != len(sort_keys):
        # It is possible that an extra "|" was in the input
        # TODO: Handle extra "|"s somehow? Or at least allow escaping them
        raise InvalidArgumentError(
            f'Wrong number of "|"-separated elements in page token [{page_token}]. '
            f"Expected {len(sort_keys)}, got {len(token_elements)}."
        )

    sort_key_clause_list = []
    previous_sort_values: list[Any] = []
    # Build the compound clause for each sort key in the token
    for i, sort_key in enumerate(sort_keys):
        col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
        sort_value = parse_list_operations_sort_value(token_elements[i], col)
        filter_clause = build_pagination_clause_for_sort_key(sort_value, previous_sort_values, sort_keys)
        sort_key_clause_list.append(filter_clause)
        previous_sort_values.append(sort_value)

    return or_(*sort_key_clause_list)


def build_page_token(operation: OperationEntry, sort_keys: list[SortKey]) -> str:
    """Use the sort keys to build a page token from the given operation."""
    token_values = []
    for sort_key in sort_keys:
        spec = LIST_OPERATIONS_SORT_KEYS.get(sort_key.name)
        if not spec:
            raise ValueError(f"Invalid sort key: {sort_key}")
        if spec.table_name == "operations":
            token_value = getattr(operation, spec.column_name)
        elif spec.table_name == "jobs":
            token_value = getattr(operation.job, spec.column_name)
        else:
            raise ValueError(
                f"Got invalid table {spec.table_name} for sort key {sort_key.name} while building page_token"
            )

        token_values.append(dump_list_operations_token_value(token_value))

    next_page_token = "|".join(token_values)
    return next_page_token


def extract_sort_keys(operation_filters: list[OperationFilter]) -> tuple[list[SortKey], list[OperationFilter]]:
    """Splits the operation filters into sort keys and non-sort filters, returning both as
    separate lists.

    Sort keys are specified with the "sort_order" parameter in the filter string. Multiple
    "sort_order"s can appear in the filter string, and all are extracted and returned."""
    sort_keys = []
    non_sort_filters = []
    for op_filter in operation_filters:
        if op_filter.parameter == "sort_order":
            if op_filter.operator != operator.eq:
                raise InvalidArgumentError('sort_order must be specified with the "=" operator.')
            sort_keys.append(op_filter.value)
        else:
            non_sort_filters.append(op_filter)

    return sort_keys, non_sort_filters


def build_sort_column_list(sort_keys: list[SortKey]) -> list[UnaryExpression[Any]]:
    """Convert the list of sort keys into a list of columns that can be
    passed to an order_by.

    This function checks the sort keys to ensure that they are in the
    parameter-model map and raises an InvalidArgumentError if they are not."""
    sort_columns: list[UnaryExpression[Any]] = []
    for sort_key in sort_keys:
        try:
            col = LIST_OPERATIONS_PARAMETER_MODEL_MAP[sort_key.name]
            if sort_key.descending:
                sort_columns.append(col.desc())
            else:
                sort_columns.append(col.asc())
        except KeyError:
            raise InvalidArgumentError(f"[{sort_key.name}] is not a valid sort key.")
    return sort_columns


def convert_filter_to_sql_filter(operation_filter: OperationFilter) -> ColumnElement[bool]:
    """Convert the internal representation of a filter to a representation that SQLAlchemy
    can understand. The return type is a "ColumnElement," per the end of this section in
    the SQLAlchemy docs: https://docs.sqlalchemy.org/en/13/core/tutorial.html#selecting-specific-columns

    This function assumes that the parser has appropriately converted the filter
    value to a Python type that can be compared to the parameter."""
    try:
        param = LIST_OPERATIONS_PARAMETER_MODEL_MAP[operation_filter.parameter]
    except KeyError:
        raise InvalidArgumentError(f"Invalid parameter: [{operation_filter.parameter}]")

    if operation_filter.parameter == "command":
        if operation_filter.operator == operator.eq:
            return param.like(f"%{operation_filter.value}%")
        elif operation_filter.operator == operator.ne:
            return param.notlike(f"%{operation_filter.value}%")

    if operation_filter.parameter == "platform":
        key, value = operation_filter.value.split(":", 1)
        value_column = LIST_OPERATIONS_PARAMETER_MODEL_MAP["platform-value"]
        return and_(param == key, operation_filter.operator(value_column, value))

    # Better type? Returning Any from function declared to return "ClauseElement"
    return operation_filter.operator(param, operation_filter.value)  # type: ignore[no-any-return]


def build_custom_filters(operation_filters: list[OperationFilter]) -> list[ColumnElement[bool]]:
    return [
        convert_filter_to_sql_filter(operation_filter)
        for operation_filter in operation_filters
        if operation_filter.parameter != "platform"
    ]
