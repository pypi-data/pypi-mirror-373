"""Added max_attachment_size column to SettingsReportingModel

Revision ID: 13b6099bbeee
Revises:
Create Date: 2018-09-19 20:38:39.636118

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "13b6099bbeee"  # pylint: disable=locally-disabled,invalid-name
down_revision = None  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column(
        "settings_reporting",
        sa.Column("max_attachment_size", sa.Integer(), nullable=True),
    )


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_column("settings_reporting", "max_attachment_size")  # pylint: disable=locally-disabled,no-member
