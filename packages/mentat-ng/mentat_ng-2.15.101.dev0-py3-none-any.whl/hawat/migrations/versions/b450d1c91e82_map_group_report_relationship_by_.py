"""Map group*report relationship by associative table

Revision ID: b450d1c91e82
Revises: 931e85727d3c
Create Date: 2021-04-28 18:07:40.111284

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b450d1c91e82"
down_revision = "931e85727d3c"
branch_labels = None
depends_on = None


def upgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.execute(  # pylint: disable=locally-disabled,no-member
        "CREATE TABLE asoc_groups_reports AS (SELECT group_id, id AS report_id FROM reports_events)"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE asoc_groups_reports ALTER COLUMN group_id SET NOT NULL"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE asoc_groups_reports ALTER COLUMN report_id SET NOT NULL"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE asoc_groups_reports ADD CONSTRAINT asoc_groups_reports_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE asoc_groups_reports ADD CONSTRAINT asoc_groups_reports_report_id_fkey FOREIGN KEY (report_id) REFERENCES reports_events(id) ON UPDATE CASCADE ON DELETE CASCADE"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE reports_events DROP COLUMN group_id"
    )


def downgrade():  # pylint: disable=locally-disabled,missing-docstring
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE reports_events ADD COLUMN group_id INTEGER"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE reports_events ADD CONSTRAINT reports_events_group_id_fkey FOREIGN KEY (group_id) REFERENCES groups(id) ON UPDATE CASCADE ON DELETE CASCADE"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "UPDATE reports_events t2 SET group_id = t1.group_id FROM asoc_groups_reports t1 WHERE t2.id = t1.report_id AND t2.group_id IS DISTINCT FROM t1.group_id"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "ALTER TABLE reports_events ALTER COLUMN group_id SET NOT NULL"
    )
    op.execute(  # pylint: disable=locally-disabled,no-member
        "DROP TABLE asoc_groups_reports"
    )
