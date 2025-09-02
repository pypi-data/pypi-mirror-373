"""Add is_base flag

Revision ID: c91b23f77fc1
Revises: b7cecb12d344
Create Date: 2022-01-18 14:46:13.319415

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c91b23f77fc1"
down_revision = "b7cecb12d344"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "networks",
        sa.Column(
            "is_base",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            default=False,
            server_default="f",
        ),
    )


def downgrade():
    op.drop_column("networks", "is_base")
