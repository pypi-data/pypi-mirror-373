"""Added last_hit column to filters table.

Revision ID: 2814becf7e0e
Revises: 9df1fd06f819
Create Date: 2020-02-18 16:56:28.488619

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2814becf7e0e"
down_revision = "9df1fd06f819"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("filters", sa.Column("last_hit", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("filters", "last_hit")
