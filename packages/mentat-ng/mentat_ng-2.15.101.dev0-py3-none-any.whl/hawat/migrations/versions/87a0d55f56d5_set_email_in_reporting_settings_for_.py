"""set email in reporting settings for group name

Revision ID: 87a0d55f56d5
Revises: d76d19d30c2c
Create Date: 2023-02-21 11:00:12.434598

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "87a0d55f56d5"
down_revision = "d76d19d30c2c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
UPDATE settings_reporting
SET emails_low = ARRAY[groups.name]
FROM groups
WHERE
  settings_reporting.emails_low = '{}' AND
  settings_reporting.emails_medium = '{}' AND
  settings_reporting.emails_high = '{}' AND
  settings_reporting.emails_critical = '{}' AND
  groups.id = settings_reporting.group_id""")


def downgrade():
    # Downgrade is not possible, but also is not necessary,
    # because it doesn't break anything in the old code.
    pass
