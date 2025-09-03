# Copyright (C) 2023 Bloomberg LP
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


from contextlib import contextmanager
from datetime import timedelta
from tempfile import NamedTemporaryFile
from threading import Lock
from typing import Any, Generator, Iterator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from buildgrid.server.exceptions import DatabaseError, RetriableDatabaseError
from buildgrid.server.logging import buildgrid_logger
from buildgrid.server.metrics_names import METRIC
from buildgrid.server.metrics_utils import publish_counter_metric, publish_gauge_metric
from buildgrid.server.settings import (
    COOLDOWN_TIME_AFTER_POOL_DISPOSE_SECONDS,
    COOLDOWN_TIME_JITTER_BASE,
    MIN_TIME_BETWEEN_SQL_POOL_DISPOSE_MINUTES,
)
from buildgrid.server.sql.models import Base

from .utils import (
    SQLPoolDisposeHelper,
    is_psycopg2_connection_string,
    is_sqlite_connection_string,
    is_sqlite_inmemory_connection_string,
)

LOGGER = buildgrid_logger(__name__)

# Each dialect has a limit on the number of bind parameters allowed. This
# matters because it determines how large we can allow our IN clauses to get.
#
# SQLite: 1000 https://www.sqlite.org/limits.html#max_variable_number
# PostgreSQL: 32767 (Int16.MAX_VALUE) https://www.postgresql.org/docs/9.4/protocol-message-formats.html
#
# We'll refer to this as the "inlimit" in the code. The inlimits are
# set to 75% of the bind parameter limit of the implementation.
DIALECT_INLIMIT_MAP = {"postgresql": 24000, "sqlite": 750}
DEFAULT_INLIMIT = 100


# NOTE: Obviously these type annotations are useless, but sadly they're what
# is in the upstream sqlalchemy2-stubs[0].
#
# Once we upgrade to SQLAlchemy 2.0 we can make these more useful, as that
# version of SQLAlchemy has sensible type annotations[1].
#
# [0]: https://github.com/sqlalchemy/sqlalchemy2-stubs/blob/main/sqlalchemy-stubs/pool/events.pyi#L9
# [1]: https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/pool/events.py#L96-L100
def _sqlite_on_connect(conn: Any, record: Any) -> None:
    """SQLite ``PRAGMA`` statements to execute immediately upon connection.

    These statements configure the behaviour of the database, and are specific
    to SQLite.

    See https://www.sqlite.org/pragma.html for details.

    Args:
        conn (DBAPIConnection): The DBAPI connection that was just connected.
        record (_ConnectionRecord): The connection record which contains the
            DBAPI connection.

    """
    # Use journal_mode=WAL to allow read/write concurrency, as well as the
    # performance improvements it brings.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")


class SqlProvider:
    """Class which provides an interface for interacting with an SQL database.

    This class is used to allow configuration of a per-process SQL connection
    pool, which can then be shared across multiple components of BuildGrid
    which require an SQL connection.

    Args:
        connection_string (str | None): The connection string to use when
            creating a database connection. If ``None`` then a temporary
            SQLite database will be created for the lifetime of this
            object.

        connection_timeout (int): The timeout to use when attempting to
            connect to the database, in seconds. Defaults to 5 seconds if
            unset.

        lock_timeout (int): The timeout to use when the connection
        holds a lock in the database. This is supported only if the database
        backend is PostgresQL.

        connect_args (dict[str, Any] | None): Dictionary of DBAPI
            connection arguments to pass to the engine. See the
            SQLAlchemy `docs`_ for details.

        max_overflow (int | None): The number of connections to allow
            as "overflow" connections in the connection pool. This is
            the number of connections which will be able to be opened
            above the value of ``pool_size``.

        pool_pre_ping (bool | None): Whether or not to test connections
            for liveness on checkout from the connection pool.

        pool_recycle (int | None): The number of seconds after which to
            recycle database connections. If ``None`` (the default) then
            connections won't be recycled (the SQLAlchemy default value
            of -1 will be used).

        pool_size (int | None): The number of connections to keep open
            inside the engine's connection pool.

        pool_timeout (int | None): The number of seconds to wait when
            attempting to get a connection from the connection pool.

        name (str): Name of the SQLProvider, which is used for metric
            publishing.

    Raises:
        ValueError: when ``connection_string`` specifies an in-memory SQLite
            database.

    .. _docs: https://docs.sqlalchemy.org/en/14/core/engines.html#use-the-connect-args-dictionary-parameter

    """

    def __init__(
        self,
        *,
        connection_string: str | None = None,
        connection_timeout: int = 5,
        lock_timeout: int = 5,
        connect_args: dict[Any, Any] | None = None,
        max_overflow: int | None = None,
        pool_pre_ping: bool | None = None,
        pool_recycle: int | None = None,
        pool_size: int | None = None,
        pool_timeout: int | None = None,
        name: str = "sql-provider",
    ):
        """Initialize an SqlProvider."""
        self._database_tempfile = None
        # If we don't have a connection string, we'll make a tempfile to use
        # as an SQLite database. This tempfile needs to exist for the lifetime
        # of the SqlProvider.
        if not connection_string:
            self._database_tempfile = NamedTemporaryFile(prefix="bgd-", suffix=".db")
            LOGGER.warning(
                "No connection string specified for the SQL provider, will use SQLite with tempfile.",
                tags=dict(tempfile=self._database_tempfile.name),
            )
            connection_string = f"sqlite:///{self._database_tempfile.name}"

        # Set up database connection
        self._session_factory = sessionmaker(future=True)
        self._scoped_session_factory = scoped_session(self._session_factory)

        self._engine = self._create_sqlalchemy_engine(
            connection_string,
            connection_timeout,
            lock_timeout=lock_timeout,
            connect_args=connect_args,
            max_overflow=max_overflow,
            pool_pre_ping=pool_pre_ping,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            pool_timeout=pool_timeout,
        )

        # If we're using a temporary file for the database, we need to create the
        # tables before we can actually use it.
        if self._database_tempfile is not None:
            Base.metadata.create_all(self._engine)

        LOGGER.info("Created SQL provider.", tags=dict(connection=self._engine.url))

        self._sql_pool_dispose_helper = SQLPoolDisposeHelper(
            COOLDOWN_TIME_AFTER_POOL_DISPOSE_SECONDS,
            COOLDOWN_TIME_JITTER_BASE,
            MIN_TIME_BETWEEN_SQL_POOL_DISPOSE_MINUTES,
            self._engine,
        )

        self._name = name
        self._num_sessions = 0
        self._lock = Lock()

    def _create_sqlalchemy_engine(
        self,
        connection_string: str,
        connection_timeout: int,
        lock_timeout: int,
        *,
        connect_args: dict[Any, Any] | None = None,
        max_overflow: int | None = None,
        pool_pre_ping: bool | None = None,
        pool_recycle: int | None = None,
        pool_size: int | None = None,
        pool_timeout: int | None = None,
    ) -> Engine:
        """Create the SQLAlchemy Engine.

        Args:
            connection_string: The connection string to use when
                creating the ``Engine``.

            connection_timeout: The timeout to use for database
                connections, in seconds. If set as 0, no timeout
                is applied.

            lock_timeout (int): The timeout to use when the connection
            holds a lock in the database. This is supported only if the database
            backend is PostgresQL.

            connect_args: Dictionary of DBAPI
                connection arguments to pass to the engine. See the
                SQLAlchemy `docs`_ for details.

            max_overflow: The number of connections to allow
                as "overflow" connections in the connection pool. This is
                the number of connections which will be able to be opened
                above the value of ``pool_size``.

            pool_pre_ping: Whether or not to test connections
                for liveness on checkout from the connection pool.

            pool_recycle: The number of seconds after which to
                recycle database connections. If ``None`` (the default) then
                connections won't be recycled (the SQLAlchemy default value
                of -1 will be used).

            pool_size: The number of connections to keep open
                inside the engine's connection pool.
                If set as zero, no connection pool is created
                and other pool_* parameters are ignored.

            pool_timeout: The number of seconds to wait when
                attempting to get a connection from the connection pool.

        Returns:
            A :class:`sqlalchemy.engine.Engine` set up to connect to the
                database defined by ``connection_string``.

        Raises:
            ValueError: when attempting to connect to an in-memory SQLite
                database.

        .. _docs: https://docs.sqlalchemy.org/en/14/core/engines.html#use-the-connect-args-dictionary-parameter

        """
        # Disallow sqlite in-memory because multi-threaded access to it is
        # complex and potentially problematic at best
        # ref: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#threading-pooling-behavior
        if is_sqlite_inmemory_connection_string(connection_string):
            raise ValueError(
                "Cannot use SQLite in-memory with BuildGrid "
                f"(connection_string=[{connection_string}]). Use a file or "
                "leave the connection_string empty for a tempfile."
            )

        extra_engine_args: dict[str, Any] = {}
        if connect_args is not None:
            extra_engine_args["connect_args"] = connect_args
        else:
            extra_engine_args["connect_args"] = {}

        if connection_timeout > 0:
            if is_sqlite_connection_string(connection_string):
                extra_engine_args["connect_args"]["timeout"] = connection_timeout
            elif is_psycopg2_connection_string(connection_string):
                extra_engine_args["connect_args"]["connect_timeout"] = connection_timeout
        if lock_timeout > 0 and is_psycopg2_connection_string(connection_string):
            # Additional postgres specific timeouts
            # Additional libpg options
            # Note that those timeouts are in milliseconds (so *1000)
            # User might specifically set options... do not override in this case.
            extra_engine_args["connect_args"].setdefault("options", f"-c lock_timeout={lock_timeout * 1000}")

        if pool_size is not None and pool_size == 0:
            LOGGER.debug("No connection pool is created.")
            extra_engine_args["poolclass"] = NullPool
        else:
            if max_overflow is not None:
                extra_engine_args["max_overflow"] = max_overflow
            if pool_pre_ping is not None:
                extra_engine_args["pool_pre_ping"] = pool_pre_ping
            if pool_recycle is not None:
                extra_engine_args["pool_recycle"] = pool_recycle
            if pool_size is not None:
                extra_engine_args["pool_size"] = pool_size
            if pool_timeout is not None:
                extra_engine_args["pool_timeout"] = pool_timeout

        LOGGER.debug(f"Additional SQLAlchemy Engine args: [{extra_engine_args}]")

        engine = create_engine(connection_string, echo=False, future=True, **extra_engine_args)
        self._session_factory.configure(bind=engine)

        # Register sqlite-specific connection callback.
        if engine.dialect.name == "sqlite":
            event.listen(engine, "connect", _sqlite_on_connect)

        return engine

    @property
    def dialect(self) -> str:
        """The SQL dialect in use by the configured SQL engine."""
        return self._engine.dialect.name

    @property
    def default_inlimit(self) -> int:
        """Return the default inlimit size based on the current SQL dialect"""
        return DIALECT_INLIMIT_MAP.get(self.dialect, DEFAULT_INLIMIT)

    @contextmanager
    def session(
        self,
        *,
        scoped: bool = False,
        sqlite_lock_immediately: bool = False,
        exceptions_to_not_raise_on: list[type[Exception]] | None = None,
        exceptions_to_not_rollback_on: list[type[Exception]] | None = None,
        expire_on_commit: bool = True,
    ) -> Iterator[Session]:
        """ContextManager yielding an ORM ``Session`` for the configured database.

        The :class:`sqlalchemy.orm.Session` lives for the duration of the
        managed context, and any open transaction is committed upon exiting
        the context.

        This method can potentially block for a short while before yielding
        if the underlying connection pool has recently been disposed of and
        refreshed due to connectivity issues.

        When ``sqlite_lock_immediately`` is ``True``, the Session will not
        yield until the database has been locked by entering into a write
        transaction when using SQLite.

        If an Exception is raised whilst in the managed context, the ongoing
        database transaction is rolled back, and the Exception is reraised.
        Some Exceptions which suggest a transient connection issue with the
        database lead to a ``RetriableDatabaseError`` being raised from the
        Exception instead.

        ``exceptions_to_not_raise_on`` defines a list of SQLAlchemyError types
        which should be suppressed instead of re-raised when occurring within
        the managed context.

        Similarly, ``exceptions_to_not_rollback_on`` defines a list of
        SQLAlchemyError types which will not trigger a transaction rollback
        when occuring within the managed context. Instead, the open transaction
        will be committed and the session closed.

        Args:
            scoped: If true, use a ``scoped_session`` factory to create the
                session. This results in reuse of the underlying Session object
                in a given thread.

            sqlite_lock_immediately: If true, execute a ``BEGIN IMMEDIATE``
                statement as soon as the session is created when using SQLite.
                This allows locking for the lifetime of the ``Session`` within
                this ContextManager, enabling similar behaviour to
                ``SELECT ... FOR UPDATE`` in other dialects. Defaults to
                ``False``.

            exceptions_to_not_raise_on: The list of error types to be suppressed
                within the context rather than re-raised. Defaults to ``None``,
                meaning all SQLAlchemyErrors will be re-raised.

            exceptions_to_not_rollback_on: The list
                of error types which shouldn't trigger a transaction rollback.
                Defaults to ``None``, meaning all SQLAlchemyErrors will trigger
                rollback of the transaction.

            expire_on_commit: Defaults to True. When True, all instances will
                be fully expired after each commit(), so that all attribute/object
                access subsequent to a completed transaction will load from
                the most recent database state. This flag is ignored if
                ``scoped == True``

        Yields:
            A :class:`sqlalchemy.orm.Session` object.

        Raises:
            DatabaseError: when a database session cannot be obtained.

            RetriableDatabaseError: when the database connection is temporarily
                interrupted, but can be expected to recover.

            Exception: Any Exception raised within the context will be re-raised
                unless it's type is included in the ``exceptions_to_not_raise_on``
                parameter.

        """
        if exceptions_to_not_raise_on is None:
            exceptions_to_not_raise_on = []
        if exceptions_to_not_rollback_on is None:
            exceptions_to_not_rollback_on = []

        factory: "scoped_session[Session] | sessionmaker[Session]" = self._session_factory
        if scoped:
            factory = self._scoped_session_factory

        # If we recently disposed of the SQL pool due to connection issues
        # ask the client to try again when it's expected to be working again
        time_til_retry = self._sql_pool_dispose_helper.time_until_active_pool()
        if time_til_retry > timedelta(seconds=0):
            raise RetriableDatabaseError(
                "Database connection was temporarily interrupted, please retry", time_til_retry
            )

        # Try to obtain a session
        try:
            session = factory() if scoped else factory(expire_on_commit=expire_on_commit)
            if sqlite_lock_immediately and session.bind.name == "sqlite":  # type: ignore
                session.execute(text("BEGIN IMMEDIATE"))
        except Exception as e:
            LOGGER.error("Unable to obtain a database session.", exc_info=True)
            raise DatabaseError("Unable to obtain a database session.") from e

        # Yield the session and catch exceptions that occur while using it
        # to roll-back if needed
        try:
            with self._lock:
                self._num_sessions += 1
                num_sessions = self._num_sessions
            publish_gauge_metric(METRIC.SQL.SQL_ACTIVE_SESSION_GAUGE_TEMPLATE.format(name=self._name), num_sessions)
            publish_counter_metric(METRIC.SQL.SQL_SESSION_COUNT_TEMPLATE.format(name=self._name), 1)

            yield session
            session.commit()
        except Exception as e:
            transient_dberr = self._sql_pool_dispose_helper.check_dispose_pool(session, e)
            if type(e) in exceptions_to_not_rollback_on:
                try:
                    session.commit()
                except Exception:
                    pass
            else:
                session.rollback()
                if transient_dberr:
                    LOGGER.warning("Rolling back database session due to transient database error.", exc_info=True)
                else:
                    LOGGER.error("Error committing database session. Rolling back.", exc_info=True)
                if type(e) not in exceptions_to_not_raise_on:
                    if transient_dberr:
                        # Ask the client to retry when the pool is expected to be healthy again
                        raise RetriableDatabaseError(
                            "Database connection was temporarily interrupted, please retry",
                            self._sql_pool_dispose_helper.time_until_active_pool(),
                        ) from e
                    raise
        finally:
            with self._lock:
                self._num_sessions -= 1
            session.close()

    @contextmanager
    def scoped_session(
        self,
        *,
        sqlite_lock_immediately: bool = False,
        exceptions_to_not_raise_on: list[type[Exception]] | None = None,
        exceptions_to_not_rollback_on: list[type[Exception]] | None = None,
    ) -> Generator[Session, None, None]:
        """ContextManager providing a thread-local ORM session for the database.

        This is a shorthand for ``SqlProvider.session(scoped=True)``.

        This ContextManager provides a reusable thread-local
        :class:`sqlalchemy.orm.Session` object. Once the ``Session`` has been
        created by the initial call, subsequent calls to this method from
        within a given thread will return the same ``Session`` object until
        :meth:`SqlProvider.remove_scoped_session` is called.

        Args:
            See :meth:`SqlProvider.session` for further details.

        Yields:
            A persistent thread-local :class:`sqlalchemy.orm.Session`.

        """
        with self.session(
            scoped=True,
            sqlite_lock_immediately=sqlite_lock_immediately,
            exceptions_to_not_raise_on=exceptions_to_not_raise_on,
            exceptions_to_not_rollback_on=exceptions_to_not_rollback_on,
        ) as session:
            yield session

    def remove_scoped_session(self) -> None:
        """Remove the thread-local session, if any."""
        self._scoped_session_factory.remove()
