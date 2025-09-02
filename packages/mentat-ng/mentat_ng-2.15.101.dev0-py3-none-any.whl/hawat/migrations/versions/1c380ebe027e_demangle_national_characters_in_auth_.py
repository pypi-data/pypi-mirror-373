"""Demangle national characters in auth attributes

Revision ID: 1c380ebe027e
Revises: 432c8bc8e49b
Create Date: 2022-07-25 12:38:15.843315

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1c380ebe027e"
down_revision = "432c8bc8e49b"
branch_labels = None
depends_on = None


def demangle(value):
    """National character demangling helper"""
    try:
        return value.encode("iso-8859-1").decode()
    except (UnicodeDecodeError, UnicodeEncodeError):
        return value


def upgrade():
    conn = op.get_bind()
    rows = conn.execute("SELECT id, fullname, organization FROM users").fetchall()
    for rid, fnm_old, org_old in rows:
        fnm = demangle(fnm_old)
        org = demangle(org_old)
        if fnm != fnm_old or org != org_old:
            conn.execute(
                "UPDATE users SET fullname = %s, organization = %s WHERE id = %s",
                (fnm, org, rid),
            )


def downgrade():
    pass
