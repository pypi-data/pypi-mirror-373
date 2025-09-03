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

"""Drop the leases table

Revision ID: 1f959c3834d3
Revises: 9ecd996412a9
Create Date: 2025-04-03 11:30:07.536808

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1f959c3834d3"
down_revision = "9ecd996412a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("leases")


def downgrade() -> None:
    op.create_table(
        "leases",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("job_name", sa.VARCHAR(), autoincrement=False, nullable=False, index=True),
        sa.Column("status", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("state", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("worker_name", sa.VARCHAR(), autoincrement=False, nullable=True, index=True),
        sa.ForeignKeyConstraint(
            ["job_name"], ["jobs.name"], name="leases_job_name_fkey", onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="leases_pkey"),
    )
