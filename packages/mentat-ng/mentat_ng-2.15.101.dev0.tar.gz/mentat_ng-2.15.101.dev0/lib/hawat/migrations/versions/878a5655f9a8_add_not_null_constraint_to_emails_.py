"""Add not null constraint to emails_medium, emails_high and emails_critical

Revision ID: 878a5655f9a8
Revises: c91b23f77fc1
Create Date: 2022-01-21 23:33:37.117842

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "878a5655f9a8"
down_revision = "c91b23f77fc1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE settings_reporting SET emails_medium = ARRAY[]::varchar[] WHERE emails_medium IS NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_medium SET NOT NULL")
    op.execute("UPDATE settings_reporting SET emails_high = ARRAY[]::varchar[] WHERE emails_high IS NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_high SET NOT NULL")
    op.execute("UPDATE settings_reporting SET emails_critical = ARRAY[]::varchar[] WHERE emails_critical IS NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_critical SET NOT NULL")


def downgrade():
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_medium DROP NOT NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_high DROP NOT NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails_critical DROP NOT NULL")
