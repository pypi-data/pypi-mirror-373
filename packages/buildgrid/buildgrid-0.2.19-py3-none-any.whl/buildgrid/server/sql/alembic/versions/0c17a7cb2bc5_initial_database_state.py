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

"""Initial database state

Revision ID: 0c17a7cb2bc5
Revises:
Create Date: 2025-03-07 15:41:58.477032

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0c17a7cb2bc5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blobs",
        sa.Column("digest_hash", sa.String(), nullable=False),
        sa.Column("digest_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint("digest_hash"),
    )
    op.create_table(
        "bots",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("bot_id", sa.String(), nullable=False),
        sa.Column("instance_name", sa.String(), nullable=False),
        sa.Column("bot_status", sa.Integer(), nullable=False),
        sa.Column("lease_id", sa.String(), nullable=True),
        sa.Column("expiry_time", sa.DateTime(), nullable=False),
        sa.Column("last_update_timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(op.f("ix_bots_bot_id"), "bots", ["bot_id"], unique=False)
    op.create_index(op.f("ix_bots_expiry_time"), "bots", ["expiry_time"], unique=False)
    op.create_index(op.f("ix_bots_last_update_timestamp"), "bots", ["last_update_timestamp"], unique=False)
    op.create_index(op.f("ix_bots_name"), "bots", ["name"], unique=False)
    op.create_table(
        "client_identities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instance", sa.String(), nullable=False),
        sa.Column("workflow", sa.String(), nullable=False),
        sa.Column("actor", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instance", "workflow", "actor", "subject"),
    )
    op.create_table(
        "index",
        sa.Column("digest_hash", sa.String(), nullable=False),
        sa.Column("digest_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("accessed_timestamp", sa.DateTime(), nullable=False),
        sa.Column("deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("inline_blob", sa.LargeBinary(), nullable=True),
        sa.PrimaryKeyConstraint("digest_hash"),
    )
    op.create_index(op.f("ix_index_accessed_timestamp"), "index", ["accessed_timestamp"], unique=False)
    op.create_index(op.f("ix_index_digest_hash"), "index", ["digest_hash"], unique=False)
    op.create_table(
        "jobs",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("instance_name", sa.String(), nullable=False),
        sa.Column("action_digest", sa.String(), nullable=False),
        sa.Column("action", sa.LargeBinary(), nullable=False),
        sa.Column("do_not_cache", sa.Boolean(), nullable=False),
        sa.Column("platform_requirements", sa.String(), nullable=False),
        sa.Column("property_label", sa.String(), server_default="unknown", nullable=False),
        sa.Column("command", sa.String(), nullable=False),
        sa.Column("stage", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("cancelled", sa.Boolean(), nullable=False),
        sa.Column("assigned", sa.Boolean(), nullable=False),
        sa.Column("n_tries", sa.Integer(), nullable=False),
        sa.Column("result", sa.String(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("create_timestamp", sa.DateTime(), nullable=True),
        sa.Column("queued_timestamp", sa.DateTime(), nullable=False),
        sa.Column("queued_time_duration", sa.Integer(), nullable=True),
        sa.Column("worker_start_timestamp", sa.DateTime(), nullable=True),
        sa.Column("worker_completed_timestamp", sa.DateTime(), nullable=True),
        sa.Column("input_fetch_start_timestamp", sa.DateTime(), nullable=True),
        sa.Column("input_fetch_completed_timestamp", sa.DateTime(), nullable=True),
        sa.Column("output_upload_start_timestamp", sa.DateTime(), nullable=True),
        sa.Column("output_upload_completed_timestamp", sa.DateTime(), nullable=True),
        sa.Column("execution_start_timestamp", sa.DateTime(), nullable=True),
        sa.Column("execution_completed_timestamp", sa.DateTime(), nullable=True),
        sa.Column("stdout_stream_name", sa.String(), nullable=True),
        sa.Column("stdout_stream_write_name", sa.String(), nullable=True),
        sa.Column("stderr_stream_name", sa.String(), nullable=True),
        sa.Column("stderr_stream_write_name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(op.f("ix_jobs_action_digest"), "jobs", ["action_digest"], unique=False)
    op.create_index(op.f("ix_jobs_instance_name"), "jobs", ["instance_name"], unique=False)
    op.create_index(op.f("ix_jobs_priority"), "jobs", ["priority"], unique=False)
    op.create_index(op.f("ix_jobs_queued_timestamp"), "jobs", ["queued_timestamp"], unique=False)
    op.create_index("ix_jobs_stage_property_label", "jobs", ["stage", "property_label"], unique=False)
    op.create_index(
        "ix_worker_completed_timestamp",
        "jobs",
        ["worker_completed_timestamp"],
        unique=False,
        postgresql_where=sa.text("worker_completed_timestamp IS NOT NULL"),
        sqlite_where=sa.text("worker_completed_timestamp IS NOT NULL"),
    )
    op.create_index(
        "ix_worker_start_timestamp",
        "jobs",
        ["worker_start_timestamp"],
        unique=False,
        postgresql_where=sa.text("worker_start_timestamp IS NOT NULL"),
        sqlite_where=sa.text("worker_start_timestamp IS NOT NULL"),
    )
    op.create_table(
        "platform_properties",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "value"),
    )
    op.create_table(
        "request_metadata",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tool_name", sa.String(), nullable=True),
        sa.Column("tool_version", sa.String(), nullable=True),
        sa.Column("invocation_id", sa.String(), nullable=True),
        sa.Column("correlated_invocations_id", sa.String(), nullable=True),
        sa.Column("action_mnemonic", sa.String(), nullable=True),
        sa.Column("target_id", sa.String(), nullable=True),
        sa.Column("configuration_id", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tool_name",
            "tool_version",
            "invocation_id",
            "correlated_invocations_id",
            "action_mnemonic",
            "target_id",
            "configuration_id",
            name="unique_metadata_constraint",
        ),
    )
    op.create_table(
        "job_platforms",
        sa.Column("job_name", sa.String(), nullable=False),
        sa.Column("platform_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["job_name"], ["jobs.name"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["platform_id"],
            ["platform_properties.id"],
        ),
        sa.PrimaryKeyConstraint("job_name", "platform_id"),
    )
    op.create_table(
        "leases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_name", sa.String(), nullable=False),
        sa.Column("status", sa.Integer(), nullable=True),
        sa.Column("state", sa.Integer(), nullable=False),
        sa.Column("worker_name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["job_name"], ["jobs.name"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leases_job_name"), "leases", ["job_name"], unique=False)
    op.create_index(op.f("ix_leases_worker_name"), "leases", ["worker_name"], unique=False)
    op.create_table(
        "operations",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("cancelled", sa.Boolean(), nullable=False),
        sa.Column("tool_name", sa.String(), nullable=True),
        sa.Column("tool_version", sa.String(), nullable=True),
        sa.Column("invocation_id", sa.String(), nullable=True),
        sa.Column("correlated_invocations_id", sa.String(), nullable=True),
        sa.Column("job_name", sa.String(), nullable=False),
        sa.Column("client_identity_id", sa.Integer(), nullable=True),
        sa.Column("request_metadata_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["client_identity_id"],
            ["client_identities.id"],
        ),
        sa.ForeignKeyConstraint(["job_name"], ["jobs.name"], onupdate="CASCADE", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["request_metadata_id"],
            ["request_metadata.id"],
        ),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(op.f("ix_operations_job_name"), "operations", ["job_name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_operations_job_name"), table_name="operations")
    op.drop_table("operations")
    op.drop_index(op.f("ix_leases_worker_name"), table_name="leases")
    op.drop_index(op.f("ix_leases_job_name"), table_name="leases")
    op.drop_table("leases")
    op.drop_table("job_platforms")
    op.drop_table("request_metadata")
    op.drop_table("platform_properties")
    op.drop_index(
        "ix_worker_start_timestamp",
        table_name="jobs",
        postgresql_where=sa.text("worker_start_timestamp IS NOT NULL"),
        sqlite_where=sa.text("worker_start_timestamp IS NOT NULL"),
    )
    op.drop_index(
        "ix_worker_completed_timestamp",
        table_name="jobs",
        postgresql_where=sa.text("worker_completed_timestamp IS NOT NULL"),
        sqlite_where=sa.text("worker_completed_timestamp IS NOT NULL"),
    )
    op.drop_index(op.f("ix_jobs_worker_name"), table_name="jobs")
    op.drop_index("ix_jobs_stage_property_label", table_name="jobs")
    op.drop_index(op.f("ix_jobs_queued_timestamp"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_priority"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_instance_name"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_action_digest"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_index_digest_hash"), table_name="index")
    op.drop_index(op.f("ix_index_accessed_timestamp"), table_name="index")
    op.drop_table("index")
    op.drop_table("client_identities")
    op.drop_index(op.f("ix_bots_name"), table_name="bots")
    op.drop_index(op.f("ix_bots_last_update_timestamp"), table_name="bots")
    op.drop_index(op.f("ix_bots_expiry_time"), table_name="bots")
    op.drop_index(op.f("ix_bots_bot_id"), table_name="bots")
    op.drop_table("bots")
    op.drop_table("blobs")
