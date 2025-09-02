"""Clean mail_to, emails and add not null constraints

Revision ID: 4a172cd00ef0
Revises: c2b4c2af6196
Create Date: 2021-07-20 10:46:04.138409

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "4a172cd00ef0"
down_revision = "c2b4c2af6196"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """CREATE OR REPLACE FUNCTION alembic_4a172cd00ef0_trim_array(character varying[])
           RETURNS character varying[]
           AS
           $$
           DECLARE
              arr ALIAS FOR $1;
              element character varying;
              retVal character varying[];
           BEGIN
              FOREACH element IN ARRAY arr
              LOOP
               retVal := array_append(retVal, trim(element)::varchar);
              END LOOP;
           RETURN retVal;
           END;
           $$
           LANGUAGE plpgsql
              STABLE
           RETURNS NULL ON NULL INPUT;"""
    )
    op.execute(
        """CREATE OR REPLACE FUNCTION alembic_4a172cd00ef0_split_strings(character varying[])
           RETURNS character varying[]
           AS
           $$
           DECLARE
              arr ALIAS FOR $1;
              element character varying;
              retVal character varying[];
           BEGIN
              FOREACH element IN ARRAY arr
              LOOP
               retVal := retVal || alembic_4a172cd00ef0_trim_array(string_to_array(element, ',')::varchar[]);
              END LOOP;
           RETURN retVal;
           END;
           $$
           LANGUAGE plpgsql
              STABLE
           RETURNS NULL ON NULL INPUT;"""
    )

    op.execute("UPDATE reports_events SET mail_to = alembic_4a172cd00ef0_trim_array(mail_to)")
    op.execute("UPDATE reports_events SET mail_to = ARRAY[]::varchar[] WHERE mail_to IS NULL OR mail_to = '{None}'")
    op.execute("ALTER TABLE reports_events ALTER COLUMN mail_to SET NOT NULL")

    op.execute("UPDATE settings_reporting SET emails = alembic_4a172cd00ef0_split_strings(emails)")
    op.execute("UPDATE settings_reporting SET emails = ARRAY[]::varchar[] WHERE emails IS NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails SET NOT NULL")

    op.execute("DROP FUNCTION alembic_4a172cd00ef0_split_strings(character varying[])")
    op.execute("DROP FUNCTION alembic_4a172cd00ef0_trim_array(character varying[])")


def downgrade():
    op.execute("ALTER TABLE reports_events ALTER COLUMN mail_to DROP NOT NULL")
    op.execute("ALTER TABLE settings_reporting ALTER COLUMN emails DROP NOT NULL")
