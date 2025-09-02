"""split filters into source and target

Revision ID: 0d38ee7bd902
Revises: 730d26cb66c8
Create Date: 2024-09-03 22:54:41.631042

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0d38ee7bd902"
down_revision = "730d26cb66c8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "source_based",
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.true(),
            )
        )


def downgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.drop_column("source_based")
