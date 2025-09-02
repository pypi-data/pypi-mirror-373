"""Add event class table

Revision ID: 9bab23fbdc37
Revises: 6d6520de5a57
Create Date: 2024-01-04 00:31:24.345605

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9bab23fbdc37"
down_revision = "599df19e7f9c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "event_classes",
        sa.Column("name", sa.String(length=250), nullable=False, unique=True),
        sa.Column("label_en", sa.String(), nullable=False),
        sa.Column("label_cz", sa.String(), nullable=False),
        sa.Column("reference", sa.String(), nullable=False),
        sa.Column(
            "displayed_main",
            postgresql.ARRAY(sa.String(), dimensions=1),
            nullable=False,
        ),
        sa.Column(
            "displayed_source",
            postgresql.ARRAY(sa.String(), dimensions=1),
            nullable=False,
        ),
        sa.Column(
            "displayed_target",
            postgresql.ARRAY(sa.String(), dimensions=1),
            nullable=False,
        ),
        sa.Column("rule", sa.String(), nullable=False),
        sa.Column(
            "severity",
            postgresql.ENUM("low", "medium", "high", "critical", name="event_class_severities"),
            nullable=False,
        ),
        sa.Column("subclassing", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("createtime", sa.DateTime(), nullable=True),
        sa.Column("last_update", sa.DateTime(), index=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("event_classes")
    postgresql.ENUM("low", "medium", "high", "critical", name="event_class_severities").drop(op.get_bind())
