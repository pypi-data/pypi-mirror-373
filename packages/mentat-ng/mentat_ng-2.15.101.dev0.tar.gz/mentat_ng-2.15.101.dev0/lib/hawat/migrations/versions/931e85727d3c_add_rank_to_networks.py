"""Add rank to networks

Revision ID: 931e85727d3c
Revises: 0df0d44a1429
Create Date: 2021-03-12 06:35:14.045287

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "931e85727d3c"
down_revision = "4a172cd00ef0"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE IF EXISTS networks ADD COLUMN rank INTEGER")


def downgrade():
    op.execute("ALTER TABLE IF EXISTS networks DROP COLUMN IF EXISTS rank")
