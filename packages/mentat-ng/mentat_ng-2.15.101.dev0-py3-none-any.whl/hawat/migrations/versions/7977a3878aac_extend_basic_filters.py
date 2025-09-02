"""Extend basic filters

Revision ID: 7977a3878aac
Revises: 9bab23fbdc37
Create Date: 2024-06-03 15:16:46.894640

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7977a3878aac"
down_revision = "9bab23fbdc37"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "event_classes",
                postgresql.ARRAY(sa.String(), dimensions=1),
                default=[],
                server_default="{}",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "targets",
                postgresql.ARRAY(sa.String(), dimensions=1),
                default=[],
                server_default="{}",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "protocols",
                postgresql.ARRAY(sa.String(), dimensions=1),
                default=[],
                server_default="{}",
                nullable=False,
            )
        )


def downgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.drop_column("protocols")
        batch_op.drop_column("targets")
        batch_op.drop_column("event_classes")
