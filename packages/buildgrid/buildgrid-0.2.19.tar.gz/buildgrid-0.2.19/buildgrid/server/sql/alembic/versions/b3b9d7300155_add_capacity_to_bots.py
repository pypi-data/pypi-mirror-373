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

"""Add capacity to bots

Revision ID: b3b9d7300155
Revises: 8fd7118e215e
Create Date: 2025-06-10 16:49:26.200322

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b3b9d7300155"
down_revision = "8fd7118e215e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    meta = sa.MetaData()
    table = sa.Table(
        "bots",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("bot_id", sa.String, index=True),
        sa.Column("instance_name", sa.String, index=True),
        sa.Column("bot_status", sa.Integer),
        sa.Column("lease_id", sa.String, nullable=True),
        sa.Column("expiry_time", sa.DateTime, index=True),
        sa.Column("last_update_timestamp", sa.DateTime, index=True),
    )

    with op.batch_alter_table("bots", copy_from=table) as batch_op:
        batch_op.add_column(sa.Column("capacity", sa.Integer(), nullable=False, server_default=sa.text("1")))


def downgrade() -> None:
    meta = sa.MetaData()
    table = sa.Table(
        "bots",
        meta,
        sa.Column("name", sa.String, primary_key=True),
        sa.Column("bot_id", sa.String, index=True),
        sa.Column("instance_name", sa.String, index=True),
        sa.Column("bot_status", sa.Integer),
        sa.Column("lease_id", sa.String, nullable=True),
        sa.Column("capacity", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("expiry_time", sa.DateTime, index=True),
        sa.Column("last_update_timestamp", sa.DateTime, index=True),
    )

    with op.batch_alter_table("bots", copy_from=table) as batch_op:
        batch_op.drop_column("capacity")
