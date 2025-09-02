"""Added password column to users table.

Revision ID: 9df1fd06f819
Revises: 29c1e46e89c7
Create Date: 2020-03-12 16:03:20.139515

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9df1fd06f819"  # pylint: disable=locally-disabled,invalid-name
down_revision = "29c1e46e89c7"  # pylint: disable=locally-disabled,invalid-name
branch_labels = None  # pylint: disable=locally-disabled,invalid-name
depends_on = None  # pylint: disable=locally-disabled,invalid-name


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.add_column("users", sa.Column("password", sa.String(), nullable=True))  # pylint: disable=locally-disabled,no-member


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.drop_column("users", "password")  # pylint: disable=locally-disabled,no-member
