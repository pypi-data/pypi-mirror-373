#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains custom commands for ``hawat-cli`` command line interface.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import contextlib
import functools
import re
import sys
import traceback

import click
import flask
import sqlalchemy
from flask.cli import AppGroup

import hawat.const
import hawat.db


def account_exists(func):
    """
    Decorator: Catch SQLAlchemy exceptions for non-existing user accounts.
    """

    @functools.wraps(func)
    def wrapper_account_exists(login, *args, **kwargs):
        try:
            return func(login, *args, **kwargs)
        except sqlalchemy.orm.exc.NoResultFound:
            click.secho(f"[FAIL] User account '{login}' was not found.", fg="red")

        except Exception:  # pylint: disable=locally-disabled,broad-except
            hawat.db.db_session().rollback()
            click.echo(traceback.TracebackException(*sys.exc_info()))

    return wrapper_account_exists


def validate_email(_ctx, _param, value):
    """Validate ``login/email`` command line parameter."""
    if value:
        if hawat.const.CRE_EMAIL.match(value):
            return value
        raise click.BadParameter(f"Value '{value}' does not look like valid email address.")
    return None


def validate_roles(_ctx, _param, value):
    """Validate ``role`` command line parameter."""
    if value:
        for val in value:
            if val not in hawat.const.ROLES:
                raise click.BadParameter(f"Value '{val}' does not look like valid user role.")
        return value
    return None


user_cli = AppGroup("users", help="User account management module.")


@user_cli.command("create")
@click.argument("login", callback=validate_email)
@click.argument("fullname")
@click.option(
    "--email",
    callback=validate_email,
    help="Optional email, login will be used as default",
)
@click.password_option()
@click.option("--enabled/--no-enabled", default=False)
@click.option(
    "--role",
    callback=validate_roles,
    help="Role to be assigned to the user (multiple)",
    multiple=True,
)
def users_create(login, fullname, email, password, enabled, role):
    """Create new user account."""
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    sqlobj = user_model()

    sqlobj.login = login
    sqlobj.fullname = fullname
    sqlobj.email = email or login
    sqlobj.roles = role or [hawat.const.ROLE_USER]
    sqlobj.enabled = enabled
    if password:
        sqlobj.set_password(password)

    click.echo("Creating new user account:")
    click.echo(f"    - Login:     {sqlobj.login}")
    click.echo(f"    - Full name: {sqlobj.fullname}")
    click.echo(f"    - Email:     {sqlobj.email}")
    click.echo("    - Roles:     {}".format(",".join(sqlobj.roles)))
    click.echo(f"    - Enabled:   {sqlobj.enabled}")
    click.echo(f"    - Password:  {sqlobj.password}")
    try:
        hawat.db.db_session().add(sqlobj)
        hawat.db.db_session().commit()
        click.secho("[OK] User account was successfully created", fg="green")

    except sqlalchemy.exc.IntegrityError as exc:
        hawat.db.db_session().rollback()
        match = re.search(r"Key \((\w+)\)=\(([^)]+)\) already exists.", str(exc))
        if match:
            click.secho(
                f"[FAIL] User account with {match.group(1)} '{match.group(2)}' already exists.",
                fg="red",
            )
        else:
            click.secho("[FAIL] There already is an user account with similar data.", fg="red")
            click.secho(f"\n{exc}", fg="blue")

    except Exception:  # pylint: disable=locally-disabled,broad-except
        hawat.db.db_session().rollback()
        click.echo(traceback.TracebackException(*sys.exc_info()))


@user_cli.command("passwd")
@click.argument("login", callback=validate_email)
@click.password_option()
@account_exists
def users_passwd(login, password):
    """Change/set password to given user account."""
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    if password:
        click.echo(f"Setting password for user account '{login}'")
        item.set_password(password)
        hawat.db.db_session().add(item)
        hawat.db.db_session().commit()
        click.secho("[OK] User account was successfully updated", fg="green")


@user_cli.command("roleadd")
@click.argument("login", callback=validate_email)
@click.argument("role", callback=validate_roles, nargs=-1)
@account_exists
def users_roleadd(login, role):
    """Add role(s) to given user account."""
    if not role:
        return
    click.echo("Adding roles '{}' to user account '{}'".format(",".join(role), login))
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    current_roles = set(item.roles)
    for i in role:
        current_roles.add(i)
    item.roles = list(current_roles)

    hawat.db.db_session().add(item)
    hawat.db.db_session().commit()
    click.secho("[OK] User account was successfully updated", fg="green")


@user_cli.command("roledel")
@click.argument("login", callback=validate_email)
@click.argument("role", callback=validate_roles, nargs=-1)
@account_exists
def users_roledel(login, role):
    """Delete role(s) to given user account."""
    click.echo("Deleting roles '{}' from user account '{}'".format(",".join(role), login))
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    current_roles = set(item.roles)
    for i in role:
        with contextlib.suppress(KeyError):
            current_roles.remove(i)
    item.roles = list(current_roles)

    hawat.db.db_session().add(item)
    hawat.db.db_session().commit()
    click.secho("[OK] User account was successfully updated", fg="green")


@user_cli.command("enable")
@click.argument("login", callback=validate_email)
@account_exists
def users_enable(login):
    """Enable given user account."""
    click.echo(f"Enabling user account '{login}'")
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    if not item.enabled:
        item.enabled = True

        hawat.db.db_session().add(item)
        hawat.db.db_session().commit()
        click.secho("[OK] User account was successfully enabled", fg="green")
    else:
        click.secho("[OK] User account was already enabled", fg="green")


@user_cli.command("disable")
@click.argument("login", callback=validate_email)
@account_exists
def users_disable(login):
    """Disable given user account."""
    click.echo(f"Disabling user account '{login}'")
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    if item.enabled:
        item.enabled = False

        hawat.db.db_session().add(item)
        hawat.db.db_session().commit()
        click.secho("[OK] User account was successfully disabled", fg="green")
    else:
        click.secho("[OK] User account was already disabled", fg="green")


@user_cli.command("delete")
@click.argument("login", callback=validate_email)
@account_exists
def users_delete(login):
    """Delete existing user account."""
    click.echo(f"Deleting user account '{login}'")
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    item = hawat.db.db_session().query(user_model).filter(user_model.login == login).one()

    hawat.db.db_session().delete(item)
    hawat.db.db_session().commit()
    click.secho("[OK] User account was successfully deleted", fg="green")


@user_cli.command("list")
def users_list():
    """List all available user accounts."""
    try:
        user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
        items = hawat.db.db_session().query(user_model).all()
        if items:
            click.echo("List of existing user accounts:")
            for item in items:
                click.echo("    - {}: {} ({})".format(item.login, item.fullname, ",".join(item.roles)))
        else:
            click.echo("There are currently no user accounts in the database.")

    except Exception:  # pylint: disable=locally-disabled,broad-except
        hawat.db.db_session().rollback()
        click.echo(traceback.TracebackException(*sys.exc_info()))


# -------------------------------------------------------------------------------


def setup_cli(app):
    """
    Setup custom application CLI commands.
    """
    app.cli.add_command(user_cli)
