#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains core application features for Hawat, the official user web
interface for the Mentat system.

The most important fetures of this module are the :py:func:`hawat.app.create_app`
and :py:func:`hawat.app.create_app_full` factory methods, that are responsible
for bootstrapping the whole application (see their documentation for more details).
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os

import pyzenkit.utils

import hawat.base
import hawat.config
from hawat.const import CFGKEY_MENTAT_CORE
from mentat.const import CKEY_CORE_DATABASE, CKEY_CORE_DATABASE_SQLSTORAGE

APP_NAME = "hawat"
"""Name of the application as a constant for Flask."""


# -------------------------------------------------------------------------------


def create_app_full(
    config_dict=None,
    config_object="hawat.config.ProductionConfig",
    config_file=None,
    config_env="HAWAT_CONFIG_FILE",
    config_func=None,
):
    """
    Factory function for building Hawat application. This function takes number of
    optional arguments, that can be used to create a very customized instance of
    Hawat application. This can be very usefull when extending applications`
    capabilities or for purposes of testing. Each of these arguments has default
    value for the most common application setup, so for disabling it entirely it
    is necessary to provide ``None`` as a value.

    :param dict config_dict: Initial default configurations
    :param str config_object: Name of the class or module containing configurations
    :param str config_file: Name of the file containing additional configurations
    :param str config_env:  Name of the environment variable pointing to file containing configurations
    :param callable config_func: Callable that will receive app.config as parameter
    :return: Hawat application
    :rtype: hawat.base.HawatApp
    """
    app = hawat.base.HawatApp(APP_NAME)
    app.json = hawat.base.HawatJSONEncoder(app)

    if config_dict and isinstance(config_dict, dict):
        app.config.update(config_dict)
    if config_object:
        app.config.from_object(config_object)
    if config_file:
        app.config.from_pyfile(config_file)
    if config_env and os.getenv(config_env, None):
        app.config.from_envvar(config_env)
    config_func = config_func or _config_app
    if config_func and callable(config_func):
        config_func(app.config)

    app.setup_app()

    return app


def create_app():
    """
    Factory function for building Hawat application. This function does not take
    any arguments, any necessary customizations must be done using environment
    variables.

    :return: Hawat application
    :rtype: hawat.base.HawatApp
    """
    config_name = os.getenv("FLASK_CONFIG", "default")
    config_file = hawat.config.get_default_config_file()
    if not os.path.isfile(config_file):
        config_file = None
    return create_app_full(config_object=hawat.config.CONFIG_MAP[config_name], config_file=config_file)


def _config_app(app_config):
    app_config.update(hawat.config.get_app_root_relative_config())

    dbcfg = app_config[CFGKEY_MENTAT_CORE][CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_SQLSTORAGE]
    app_config["SQLALCHEMY_DATABASE_URI"] = dbcfg["url"]
    app_config["SQLALCHEMY_ECHO"] = dbcfg["echo"]

    app_config["BABEL_TRANSLATION_DIRECTORIES"] = "translations;"
    app_config["BABEL_TRANSLATION_DIRECTORIES"] += pyzenkit.utils.get_resource_path_fr(
        os.path.join(
            app_config["MENTAT_CORE"]["__core__reporter"]["templates_dir"],
            "translations;",
        )
    )
