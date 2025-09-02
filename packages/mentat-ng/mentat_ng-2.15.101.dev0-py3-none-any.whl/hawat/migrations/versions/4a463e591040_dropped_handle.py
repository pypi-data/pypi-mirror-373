"""Removed handle column from EventReportModel

Revision ID: 4a463e591040
Revises: 13b6099bbeee
Create Date: 2018-10-12 12:40:24.705053

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a463e591040"  # pylint: disable=locally-disabled,invalid-name
down_revision = "13b6099bbeee"  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_index("ix_reports_events_handle", table_name="reports_events")  # pylint: disable=locally-disabled,no-member
    op.drop_column("reports_events", "handle")  # pylint: disable=locally-disabled,no-member


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column(
        "reports_events",
        sa.Column("handle", sa.VARCHAR(), autoincrement=False, nullable=False),
    )  # pylint: disable=locally-disabled,no-member
    op.create_index("ix_reports_events_handle", "reports_events", ["handle"], unique=True)  # pylint: disable=locally-disabled,no-member
