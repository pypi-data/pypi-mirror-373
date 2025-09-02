"""Add detectors table

Revision ID: 1a58ce62406a
Revises: 1c380ebe027e
Create Date: 2022-08-15 09:23:47.292309

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "1a58ce62406a"
down_revision = "4fea3df63b55"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "CREATE TABLE detectors (name character varying(100) NOT NULL, description character varying, source character varying(100) NOT NULL, credibility double precision NOT NULL, id integer NOT NULL, createtime timestamp without time zone)"
    )
    op.execute(
        "CREATE SEQUENCE public.detectors_id_seq AS integer START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1"
    )
    op.execute("ALTER SEQUENCE detectors_id_seq OWNED BY detectors.id")
    op.execute("ALTER TABLE ONLY detectors ALTER COLUMN id SET DEFAULT nextval('detectors_id_seq'::regclass)")
    op.execute("ALTER TABLE ONLY detectors ADD CONSTRAINT detectors_pkey PRIMARY KEY (id)")
    op.execute("CREATE UNIQUE INDEX ix_detectors_name ON detectors USING btree (name)")


def downgrade():
    op.execute("DROP TABLE detectors")
