"""empty message

Revision ID: 0df0d44a1429
Revises: 2814becf7e0e
Create Date: 2020-05-12 19:00:15.562077

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0df0d44a1429"
down_revision = "2814becf7e0e"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("settings_reporting", "max_attachment_size")
    op.drop_column("settings_reporting", "timing_thr_hi")
    op.drop_column("settings_reporting", "timing_per_md")
    op.drop_column("settings_reporting", "timing_thr_cr")
    op.drop_column("settings_reporting", "timing_rel_lo")
    op.drop_column("settings_reporting", "template")
    op.drop_column("settings_reporting", "attachments")
    op.drop_column("settings_reporting", "timing_per_hi")
    op.drop_column("settings_reporting", "timing_thr_md")
    op.drop_column("settings_reporting", "timing_per_lo")
    op.drop_column("settings_reporting", "timing_rel_cr")
    op.drop_column("settings_reporting", "timing_rel_hi")
    op.drop_column("settings_reporting", "timing")
    op.drop_column("settings_reporting", "timing_per_cr")
    op.drop_column("settings_reporting", "timing_rel_md")
    op.drop_column("settings_reporting", "compress")
    op.drop_column("settings_reporting", "timing_thr_lo")
    op.drop_column("settings_reporting", "mute")


def downgrade():
    op.add_column(
        "settings_reporting",
        sa.Column("timing_thr_lo", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("compress", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_rel_md", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_per_cr", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column(
            "timing",
            postgresql.ENUM("default", "custom", name="timing_types"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_rel_hi", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_rel_cr", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_per_lo", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_thr_md", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_per_hi", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column(
            "attachments",
            postgresql.ENUM("json", "csv", "all", "none", name="reporting_attachments"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("template", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_rel_lo", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_thr_cr", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_per_md", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("timing_thr_hi", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("max_attachment_size", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "settings_reporting",
        sa.Column("mute", sa.BOOLEAN(), autoincrement=False, nullable=True),
    )
