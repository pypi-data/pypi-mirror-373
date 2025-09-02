"""Convert networks to ip4r type

Revision ID: 4fea3df63b55
Revises: 1c380ebe027e
Create Date: 2022-09-26 11:32:08.296165

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4fea3df63b55"
down_revision = "1c380ebe027e"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE networks ALTER COLUMN network TYPE iprange USING network::iprange")


def downgrade():
    op.execute("ALTER TABLE networks ALTER COLUMN network TYPE varchar")
