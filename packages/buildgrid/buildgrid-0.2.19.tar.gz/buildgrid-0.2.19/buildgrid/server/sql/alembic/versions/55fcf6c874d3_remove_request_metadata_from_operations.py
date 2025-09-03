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

"""Remove request metadata from Operations

Revision ID: 55fcf6c874d3
Revises: 910398062924
Create Date: 2024-07-19 14:55:37.668554

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "55fcf6c874d3"
down_revision = "910398062924"
branch_labels = None
depends_on = None


def upgrade() -> None:
    meta = sa.MetaData()
    table = sa.Table(
        "operations",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column(
            "job_name",
            sa.String,
            sa.ForeignKey("jobs.name", ondelete="CASCADE", onupdate="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.Column("cancelled", sa.Boolean, default=False, nullable=False),
        sa.Column("tool_name", sa.String, nullable=True),
        sa.Column("tool_version", sa.String, nullable=True),
        sa.Column("invocation_id", sa.String, nullable=True),
        sa.Column("correlated_invocations_id", sa.String, nullable=True),
        sa.Column("client_identity_id", sa.Integer, sa.ForeignKey("client_identities.id"), nullable=True),
        sa.Column("request_metadata_id", sa.Integer, sa.ForeignKey("request_metadata.id"), nullable=True),
    )

    with op.batch_alter_table("operations", copy_from=table) as batch_op:
        batch_op.drop_column("correlated_invocations_id")
        batch_op.drop_column("invocation_id")
        batch_op.drop_column("tool_version")
        batch_op.drop_column("tool_name")


def downgrade() -> None:
    meta = sa.MetaData()
    table = sa.Table(
        "operations",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column(
            "job_name",
            sa.String,
            sa.ForeignKey("jobs.name", ondelete="CASCADE", onupdate="CASCADE"),
            index=True,
            nullable=False,
        ),
        sa.Column("cancelled", sa.Boolean, default=False, nullable=False),
        sa.Column("client_identity_id", sa.Integer, sa.ForeignKey("client_identities.id"), nullable=True),
        sa.Column("request_metadata_id", sa.Integer, sa.ForeignKey("request_metadata.id"), nullable=True),
    )

    with op.batch_alter_table("operations", copy_from=table) as batch_op:
        batch_op.add_column(sa.Column("tool_name", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("tool_version", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("invocation_id", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("correlated_invocations_id", sa.VARCHAR(), autoincrement=False, nullable=True))
