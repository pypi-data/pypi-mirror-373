"""make group optional in filters

Revision ID: 5b366442ec4d
Revises: 025e7bfe68b5
Create Date: 2024-11-22 18:01:53.589228

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5b366442ec4d"
down_revision = "025e7bfe68b5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.INTEGER(),
            nullable=True,
        )


def downgrade():
    with op.batch_alter_table("filters", schema=None) as batch_op:
        batch_op.alter_column(
            "group_id",
            existing_type=sa.INTEGER(),
            nullable=False,
        )
