# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------

"""
This module contains environment setup for `Alembic-based <https://alembic.sqlalchemy.org/en/latest/index.html>`__
database migrations for metadata database ``mentat_main``.
"""

import logging
from logging.config import fileConfig

from alembic import context
from flask import current_app
from sqlalchemy import engine_from_config, pool

# This is the Alembic Config object, which provides access to the values within
# the .ini file in use.
CONFIG = context.config

if CONFIG.config_file_name is None:
    raise RuntimeError("CONFIG.config_file_name is None")

# Interpret the config file for Python logging. This line sets up loggers basically.
fileConfig(CONFIG.config_file_name)
LOGGER = logging.getLogger("alembic.env")

# Add your model's MetaData object here for 'autogenerate' support.
CONFIG.set_main_option("sqlalchemy.url", current_app.config["SQLALCHEMY_DATABASE_URI"])
TARGET_METADATA = current_app.extensions["migrate"].db.metadata

# Other values from the config, defined by the needs of env.py, can be acquired:
#   my_important_option = config.get_main_option("my_important_option")
#   ... etc.


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an
    Engine is acceptable here as well.  By skipping the Engine creation we don't
    even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = CONFIG.get_main_option("sqlalchemy.url")
    context.configure(url=url)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection with
    the context.
    """

    # This callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema.
    #   reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(ctxt, rev, directives):  # pylint: disable=locally-disabled,unused-argument
        if getattr(CONFIG.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                LOGGER.info("No changes in schema detected.")

    engine = engine_from_config(
        CONFIG.get_section(CONFIG.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=TARGET_METADATA,
        process_revision_directives=process_revision_directives,
        **current_app.extensions["migrate"].configure_args,
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
