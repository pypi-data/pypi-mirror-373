"""Add count of uncredible events to reports

Revision ID: d76d19d30c2c
Revises: 4e6cef4ff5ce
Create Date: 2023-01-05 11:50:03.315521

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "d76d19d30c2c"
down_revision = "4e6cef4ff5ce"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE reports_events ADD COLUMN evcount_det INTEGER")
    op.execute("ALTER TABLE reports_events ADD COLUMN evcount_det_blk INTEGER")


def downgrade():
    op.execute("ALTER TABLE reports_events DROP COLUMN evcount_det")
    op.execute("ALTER TABLE reports_events DROP COLUMN evcount_det_blk")
