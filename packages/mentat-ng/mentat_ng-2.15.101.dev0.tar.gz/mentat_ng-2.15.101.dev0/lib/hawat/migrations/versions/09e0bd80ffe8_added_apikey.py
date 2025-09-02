"""Added apikey column to UserModel

Revision ID: 09e0bd80ffe8
Revises: 4a463e591040
Create Date: 2018-10-16 13:27:30.705652

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "09e0bd80ffe8"  # pylint: disable=locally-disabled,invalid-name
down_revision = "4a463e591040"  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column("users", sa.Column("apikey", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_apikey"), "users", ["apikey"], unique=True)  # pylint: disable=locally-disabled,no-member


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_index(op.f("ix_users_apikey"), table_name="users")  # pylint: disable=locally-disabled,no-member
    op.drop_column("users", "apikey")  # pylint: disable=locally-disabled,no-member
