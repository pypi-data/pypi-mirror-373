"""add info severity

Revision ID: 025e7bfe68b5
Revises: 9c4e85c45a1b
Create Date: 2024-11-06 11:56:20.450915

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "025e7bfe68b5"
down_revision = "9c4e85c45a1b"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE event_class_severities ADD VALUE IF NOT EXISTS 'info' BEFORE 'low'")
    op.execute("ALTER TYPE report_severities ADD VALUE IF NOT EXISTS 'info' BEFORE 'low'")

    with op.batch_alter_table("settings_reporting", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "emails_info",
                postgresql.ARRAY(sa.String(), dimensions=1),
                nullable=False,
                server_default="{}",
            )
        )
    # Move all values from emails_low to emails_info.
    op.execute("""
UPDATE settings_reporting
SET
    emails_info = emails_low,
    emails_low = '{}'
WHERE emails_low IS NOT NULL;""")


# Other changes cannot be easily reverted, because removing enum
# values is not possible in Postgres.
def downgrade():
    # Move all values from emails_info to emails_low.
    op.execute("""
UPDATE settings_reporting
SET
    emails_low = ARRAY(SELECT DISTINCT UNNEST(emails_low || emails_info));""")
    with op.batch_alter_table("settings_reporting", schema=None) as batch_op:
        batch_op.drop_column("emails_info")
