"""User lowercase

Revision ID: 426e6e986b40
Revises: 878a5655f9a8
Create Date: 2022-06-20 11:42:04.329244

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "426e6e986b40"
down_revision = "878a5655f9a8"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE users SET email = lower(email) WHERE email <> lower(email)")
    # Add a random number and '_CONFLICT_CASE' string as a suffix to logins which
    # are not in lowercase and are not unique when in lowercase and disable users
    # with such logins.
    op.execute(
        "UPDATE users u1 SET login = concat(u1.login, '_', floor(random() * 10000 + 1), '_CONFLICT_CASE'), enabled = FALSE FROM (SELECT lower(login) login FROM users GROUP BY lower(login) HAVING count(*) > 1) u2 WHERE lower(u1.login) = u2.login"
    )
    op.execute("UPDATE users SET login = lower(login) WHERE login <> lower(login)")


def downgrade():
    pass
