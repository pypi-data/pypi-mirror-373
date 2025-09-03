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

"""Add property label entry table

Revision ID: 910398062924
Revises: 0c17a7cb2bc5
Create Date: 2025-02-19 12:26:21.426898

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "910398062924"
down_revision = "0c17a7cb2bc5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "property_labels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("property_label", sa.String(), nullable=False),
        sa.Column("bot_name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["bot_name"], ["bots.name"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_property_labels_bot_name"), "property_labels", ["bot_name"], unique=False)
    op.create_index(op.f("ix_property_labels_property_label"), "property_labels", ["property_label"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_property_labels_property_label"), table_name="property_labels")
    op.drop_index(op.f("ix_property_labels_bot_name"), table_name="property_labels")
    op.drop_table("property_labels")
