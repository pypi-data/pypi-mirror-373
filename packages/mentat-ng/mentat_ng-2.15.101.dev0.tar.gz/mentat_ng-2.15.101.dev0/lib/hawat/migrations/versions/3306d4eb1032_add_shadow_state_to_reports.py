"""add shadow state to reports

Revision ID: 3306d4eb1032
Revises: 5b366442ec4d
Create Date: 2025-04-02 14:43:13.004832

"""

import sqlalchemy as sa
from alembic import op

from mentat.datatype.sqldb import EventClassState

# revision identifiers, used by Alembic.
revision = "3306d4eb1032"
down_revision = "5b366442ec4d"
branch_labels = None
depends_on = None


def upgrade():
    event_class_state_enum = sa.Enum(EventClassState, name="event_class_state")
    event_class_state_enum.create(op.get_bind())
    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "state",
                event_class_state_enum,
                nullable=False,
                server_default="DISABLED",
            )
        )

    # enabled -> state
    op.execute("""
           UPDATE event_classes
           SET state = CASE
               WHEN enabled = TRUE THEN 'ENABLED'::event_class_state
               ELSE 'DISABLED'::event_class_state
           END
       """)

    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.drop_column("enabled")

    with op.batch_alter_table("reports_events", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "flag_shadow",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            )
        )


def downgrade():
    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "enabled",
                sa.BOOLEAN(),
                autoincrement=False,
                nullable=False,
                server_default=sa.text("false"),
            )
        )

    # state -> enabled
    op.execute("""
            UPDATE event_classes
            SET enabled = (state = 'ENABLED')
        """)

    with op.batch_alter_table("event_classes", schema=None) as batch_op:
        batch_op.drop_column("state")
    op.execute("DROP TYPE event_class_state")

    with op.batch_alter_table("reports_events", schema=None) as batch_op:
        batch_op.drop_column("flag_shadow")
