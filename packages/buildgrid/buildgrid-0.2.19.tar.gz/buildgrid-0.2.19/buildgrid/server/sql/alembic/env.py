# Copyright (C) 2019 Bloomberg LP
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

import os
import sys
from logging import getLogger
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.base import Connection

from buildgrid.server.sql.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
try:
    fileConfig(config.config_file_name)  # type: ignore[arg-type]  # covariance in union issue. Not a real error.
except TypeError:
    pass

LOGGER = getLogger(__name__)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# PL/pgSQL block to abort the migration for unexpected database versions
VERSION_CHECK_PLPGSQL = """
DO $$
DECLARE
    current_version TEXT;
BEGIN
    SELECT version_num INTO current_version FROM alembic_version;
    IF current_version <> '{expected_version}' THEN
        RAISE EXCEPTION 'Database version mismatch: expected {expected_version}, but found %', current_version;
    END IF;
END $$;
"""


def run_migrations_offline() -> None:  # pragma: no cover
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    start = context.get_starting_revision_argument()
    destination = context.get_revision_argument()

    filename = f"{start}->{destination}.sql"
    if start is None and destination == context.get_head_revision():
        filename = "all.sql"
    elif start is None:
        filename = f"base->{destination}.sql"

    path = os.path.join("data", "revisions", filename)

    with open(path, "w") as out:
        context.configure(
            url=url, target_metadata=target_metadata, literal_binds=True, output_buffer=out, render_as_batch=True
        )

        with context.begin_transaction():
            migration_context = context.get_context()
            current_rev = migration_context.get_current_revision()
            if current_rev and url and url.startswith("postgresql:"):
                migration_context.output_buffer.write(VERSION_CHECK_PLPGSQL.format(expected_version=current_rev))

            context.run_migrations()


def _run_migrations_online(connection: Connection) -> None:  # pragma: no cover
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:  # pragma: no cover
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    try:
        connection = config.attributes["connection"]
        _run_migrations_online(connection)

    except KeyError:
        config_section = config.get_section(config.config_ini_section)
        if config_section is not None:
            connectable = engine_from_config(config_section, prefix="sqlalchemy.", poolclass=pool.NullPool)
            with connectable.connect() as connection:
                _run_migrations_online(connection)
        else:
            LOGGER.error(
                "Configuration file must define either `connection` or SQLAlchemy config "
                f"keys prefixed with `sqlalchemy` in the {config.config_ini_section} section."
            )
            sys.exit(1)


if context.is_offline_mode():  # pragma: no cover
    run_migrations_offline()
else:  # pragma: no cover
    run_migrations_online()
