"""Add registered and hits columns

Revision ID: 4e6cef4ff5ce
Revises: 1a58ce62406a
Create Date: 2023-01-02 12:13:41.583488

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4e6cef4ff5ce"
down_revision = "1a58ce62406a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE detectors ADD COLUMN registered TIMESTAMP without time zone")
    op.execute("ALTER TABLE detectors ADD COLUMN hits INTEGER NOT NULL DEFAULT 0")


def downgrade():
    op.execute("ALTER TABLE detectors DROP COLUMN registered")
    op.execute("ALTER TABLE detectors DROP COLUMN hits")
