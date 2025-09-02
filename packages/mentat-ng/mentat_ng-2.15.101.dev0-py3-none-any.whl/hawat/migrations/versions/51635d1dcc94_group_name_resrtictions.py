"""convert group names to newer restrictions

Revision ID: 51635d1dcc94
Revises: 87a0d55f56d5
Create Date: 2023-04-21 15:00:18.308504

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "51635d1dcc94"
down_revision = "87a0d55f56d5"
branch_labels = None
depends_on = None


def upgrade():
    # If group name contains invalid characters, replace every invalid character by '_',
    # and prepend 'INVALID_NAME_' to the start. If the only invalid characters group name contains
    # are '+' and ',', these are converted to '_' without prepending. If this mapping creates a duplicity,
    # this duplicity is attempted to be resolved by appending _<group id>_CONFLICT_CASE to the end.
    op.execute(
        "UPDATE groups SET name = CASE WHEN CARDINALITY(t.id) = 1 THEN t.name ELSE left(t.name, 100 - LENGTH('_CONFLICT_CASE') - LENGTH(groups.id::text) - 1) || '_' || groups.id :: text || '_CONFLICT_CASE' END FROM (SELECT name, ARRAY_AGG(id) AS id FROM (SELECT CASE WHEN name ~ '^[-_@.a-zA-Z0-9]+$' THEN name WHEN name ~ '^[-+,_@.a-zA-Z0-9]+$' THEN regexp_replace(name, '[+,]', '_', 'g') ELSE 'INVALID_NAME_' || regexp_replace(left(name, 100 - LENGTH('INVALID_NAME_')), '[^-_@.a-zA-Z0-9]', '_', 'g') END AS name, id FROM groups) u GROUP BY name) t WHERE groups.id = ANY (t.id)"
    )


def downgrade():
    pass
