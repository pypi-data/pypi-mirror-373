"""Drop reports_events message not null constraint

Revision ID: 29c1e46e89c7
Revises: d0f8c8c546dd
Create Date: 2019-10-31 16:21:28.065851

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "29c1e46e89c7"
down_revision = "d0f8c8c546dd"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "reports_events",
        "message",
        existing_type=sa.VARCHAR(),
        nullable=True,
    )


def downgrade():
    op.alter_column(
        "reports_events",
        "message",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
