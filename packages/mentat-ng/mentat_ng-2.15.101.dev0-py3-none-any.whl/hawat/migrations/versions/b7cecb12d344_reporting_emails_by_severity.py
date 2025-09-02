"""Reporting emails by severity

Revision ID: b7cecb12d344
Revises: b450d1c91e82
Create Date: 2021-05-07 07:09:03.517970

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b7cecb12d344"
down_revision = "b450d1c91e82"
branch_labels = None
depends_on = None


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting RENAME COLUMN emails TO emails_low"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting ADD COLUMN emails_medium VARCHAR[]"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting ADD COLUMN emails_high VARCHAR[]"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting ADD COLUMN emails_critical VARCHAR[]"
    )


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting DROP COLUMN emails_critical"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting DROP COLUMN emails_high"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting DROP COLUMN emails_medium"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE settings_reporting RENAME COLUMN emails_low TO emails"
    )
