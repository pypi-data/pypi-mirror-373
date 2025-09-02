"""Added wanted group membership relationship between UserModel and GroupModel

Revision ID: 4046ff1bdace
Revises: 5d7586830397
Create Date: 2019-08-29 13:47:41.277792

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4046ff1bdace"  # pylint: disable=locally-disabled,invalid-name
down_revision = "5d7586830397"  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.create_table(  # pylint: disable=locally-disabled,no-member
        "asoc_group_members_wanted",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["groups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
    )


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_table("asoc_group_members_wanted")  # pylint: disable=locally-disabled,no-member
