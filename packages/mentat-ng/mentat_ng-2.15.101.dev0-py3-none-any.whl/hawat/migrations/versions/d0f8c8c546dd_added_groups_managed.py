"""Added managed column to GroupModel

Revision ID: d0f8c8c546dd
Revises: 4046ff1bdace
Create Date: 2019-09-03 13:24:55.299237

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d0f8c8c546dd"  # pylint: disable=locally-disabled,invalid-name
down_revision = "4046ff1bdace"  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column(
        "groups",
        sa.Column("managed", sa.Boolean(), nullable=False, default=False, server_default="f"),
    )


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_column("groups", "managed")  # pylint: disable=locally-disabled,no-member
