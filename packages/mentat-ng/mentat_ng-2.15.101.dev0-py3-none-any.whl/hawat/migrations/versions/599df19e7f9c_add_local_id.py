"""Add local id

Revision ID: 599df19e7f9c
Revises: 51635d1dcc94
Create Date: 2023-07-03 12:27:47.879512

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "599df19e7f9c"
down_revision = "51635d1dcc94"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE groups ADD COLUMN local_id VARCHAR(20)")
    op.execute("ALTER TABLE networks ADD COLUMN local_id VARCHAR(20)")


def downgrade():
    op.execute("ALTER TABLE groups DROP COLUMN local_id")
    op.execute("ALTER TABLE networks DROP COLUMN local_id")
