"""add target report type

Revision ID: 730d26cb66c8
Revises: 941dfe633909
Create Date: 2024-08-07 18:43:24.261234

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "730d26cb66c8"
down_revision = "941dfe633909"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE report_types ADD VALUE 'target'")


def downgrade():
    # Not easily possible, because Postgres does not support removing
    # a value from a type.
    pass
