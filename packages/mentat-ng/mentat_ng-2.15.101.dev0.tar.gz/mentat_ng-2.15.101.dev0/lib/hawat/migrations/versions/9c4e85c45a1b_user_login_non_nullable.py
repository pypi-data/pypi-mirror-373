"""user login non nullable

Revision ID: 9c4e85c45a1b
Revises: 0d38ee7bd902
Create Date: 2024-11-01 10:06:20.974233

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9c4e85c45a1b"
down_revision = "0d38ee7bd902"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "login",
            existing_type=sa.VARCHAR(length=50),
            nullable=False,
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.alter_column(
            "login",
            existing_type=sa.VARCHAR(length=50),
            nullable=True,
        )
