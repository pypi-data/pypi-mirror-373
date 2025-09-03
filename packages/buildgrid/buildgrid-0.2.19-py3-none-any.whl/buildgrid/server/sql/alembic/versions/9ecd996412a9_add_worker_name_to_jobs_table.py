# Copyright (C) 2025 Bloomberg LP
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

"""Add worker name to jobs table

Revision ID: 9ecd996412a9
Revises: 55fcf6c874d3
Create Date: 2025-04-01 13:58:14.330985

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9ecd996412a9"
down_revision = "55fcf6c874d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # This is needed to support generating offline migrations for SQLite.
    # Context: https://alembic.sqlalchemy.org/en/latest/batch.html#working-in-offline-mode
    meta = sa.MetaData()
    table = sa.Table(
        "jobs",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("instance_name", sa.String, index=True, nullable=False),
        sa.Column("action_digest", sa.String, index=True, nullable=False),
        sa.Column("action", sa.LargeBinary, nullable=False),
        sa.Column("do_not_cache", sa.Boolean, default=False, nullable=False),
        sa.Column("platform_requirements", sa.String, nullable=False),
        sa.Column("property_label", sa.String, nullable=False, server_default="unknown"),
        sa.Column("command", sa.String, nullable=False),
        sa.Column("stage", sa.Integer, default=0, nullable=False),
        sa.Column("priority", sa.Integer, default=1, index=True, nullable=False),
        sa.Column("cancelled", sa.Boolean, default=False, nullable=False),
        sa.Column("assigned", sa.Boolean, default=False, nullable=False),
        sa.Column("n_tries", sa.Integer, default=0, nullable=False),
        sa.Column("result", sa.String, nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("create_timestamp", sa.DateTime, nullable=True),
        sa.Column("queued_timestamp", sa.DateTime, index=True, nullable=False),
        sa.Column("queued_time_duration", sa.Integer, nullable=True),
        sa.Column("worker_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("worker_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("input_fetch_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("input_fetch_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("output_upload_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("output_upload_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("execution_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("execution_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("stdout_stream_name", sa.String, nullable=True),
        sa.Column("stdout_stream_write_name", sa.String, nullable=True),
        sa.Column("stderr_stream_name", sa.String, nullable=True),
        sa.Column("stderr_stream_write_name", sa.String, nullable=True),
    )

    with op.batch_alter_table("jobs", copy_from=table) as batch_op:
        batch_op.add_column(sa.Column("worker_name", sa.String(), nullable=True))
        batch_op.create_index(batch_op.f("ix_jobs_worker_name"), ["worker_name"], unique=False)


def downgrade() -> None:
    meta = sa.MetaData()
    table = sa.Table(
        "jobs",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("instance_name", sa.String, index=True, nullable=False),
        sa.Column("action_digest", sa.String, index=True, nullable=False),
        sa.Column("action", sa.LargeBinary, nullable=False),
        sa.Column("do_not_cache", sa.Boolean, default=False, nullable=False),
        sa.Column("platform_requirements", sa.String, nullable=False),
        sa.Column("property_label", sa.String, nullable=False, server_default="unknown"),
        sa.Column("command", sa.String, nullable=False),
        sa.Column("stage", sa.Integer, default=0, nullable=False),
        sa.Column("priority", sa.Integer, default=1, index=True, nullable=False),
        sa.Column("cancelled", sa.Boolean, default=False, nullable=False),
        sa.Column("assigned", sa.Boolean, default=False, nullable=False),
        sa.Column("n_tries", sa.Integer, default=0, nullable=False),
        sa.Column("worker_name", sa.String, index=True, nullable=False),
        sa.Column("result", sa.String, nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("create_timestamp", sa.DateTime, nullable=True),
        sa.Column("queued_timestamp", sa.DateTime, index=True, nullable=False),
        sa.Column("queued_time_duration", sa.Integer, nullable=True),
        sa.Column("worker_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("worker_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("input_fetch_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("input_fetch_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("output_upload_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("output_upload_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("execution_start_timestamp", sa.DateTime, nullable=True),
        sa.Column("execution_completed_timestamp", sa.DateTime, nullable=True),
        sa.Column("stdout_stream_name", sa.String, nullable=True),
        sa.Column("stdout_stream_write_name", sa.String, nullable=True),
        sa.Column("stderr_stream_name", sa.String, nullable=True),
        sa.Column("stderr_stream_write_name", sa.String, nullable=True),
    )

    with op.batch_alter_table("jobs", copy_from=table) as batch_op:
        batch_op.drop_index(batch_op.f("ix_jobs_worker_name"))
        batch_op.drop_column("worker_name")
