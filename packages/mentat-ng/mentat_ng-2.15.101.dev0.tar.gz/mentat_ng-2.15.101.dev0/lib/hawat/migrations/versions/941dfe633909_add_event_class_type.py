"""Add event class type.

Revision ID: 941dfe633909
Revises: 7977a3878aac
Create Date: 2024-07-24 14:54:46.246772

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "941dfe633909"
down_revision = "7977a3878aac"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "source_based",
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.true(),
            )
        )


def downgrade():
    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.drop_column("source_based")
