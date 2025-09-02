"""Lowercase check constraint

Revision ID: 432c8bc8e49b
Revises: 426e6e986b40
Create Date: 2022-07-19 11:48:46.111909

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "432c8bc8e49b"
down_revision = "426e6e986b40"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE users ADD CONSTRAINT login_lowercase CHECK (login = lower(login))")
    op.execute("ALTER TABLE users ADD CONSTRAINT email_lowercase CHECK (email = lower(email))")


def downgrade():
    op.execute("ALTER TABLE users DROP CONSTRAINT login_lowercase")
    op.execute("ALTER TABLE users DROP CONSTRAINT email_lowercase")
