"""Removed managed column from GroupModel

Revision ID: c2b4c2af6196
Revises: 0df0d44a1429
Create Date: 2021-10-13 17:59:47.008910

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2b4c2af6196"
down_revision = "0df0d44a1429"
branch_labels = None
depends_on = None


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_column("groups", "managed")  # pylint: disable=locally-disabled,no-member


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column(
        "groups",
        sa.Column(
            "managed",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            default=False,
            server_default="f",
        ),
    )
