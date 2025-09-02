#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This package contains the web user interface for the Mentat system.


Architecture
--------------------------------------------------------------------------------

Hawat is implemented on top of the `Flask <http://flask.pocoo.org/>`__ microframework
and attempts to use many of its advanced features for application extendability,
modularity and configurability. The `Flask <http://flask.pocoo.org/>`__ documentation
is a great place to start if you want to write your own custom Hawat plugins or
somehow extend or customize the default features or behavior.

Hawat was designed with a focus on application modularity. Only very small part of
the application is mandatory and _core_, virtually everything is a pluggable module
that can be dynamically enabled or disabled in configuration. Following is a list
of key application features:


Prerequisites and dependencies
--------------------------------------------------------------------------------

Hawat is implemented on top of the `Flask <http://flask.pocoo.org/>`__ microframework
and with the use of following Python3 key libraries:

    * `blinker <http://pythonhosted.org/blinker/>`__
    * `jinja2 <http://jinja.pocoo.org/>`__
    * `werkzeug <http://werkzeug.pocoo.org/>`__
    * `wtforms <https://wtforms.readthedocs.io/en/latest/>`__
    * `flask-babel <https://pythonhosted.org/Flask-Babel/>`__
    * `flask-debugtoolbar <https://flask-debugtoolbar.readthedocs.io/en/latest/>`__
    * `flask-login <https://flask-login.readthedocs.io/en/latest/>`__
    * `flask-mail <http://pythonhosted.org/Flask-Mail/>`__
    * `flask-principal <https://pythonhosted.org/Flask-Principal/>`__
    * `flask-wtf <https://flask-wtf.readthedocs.io/en/stable/>`__

The application frontend is built on top of following key libraries:

    * `jQuery <http://jquery.com/>`__
    * `bootstrap3 <https://getbootstrap.com/docs/3.3/>`__
    * bootstrap-select
    * `font-awesome <http://fontawesome.io/>`__


.. todo::

    * Secure redirect back after login:
        * http://flask.pocoo.org/snippets/62/
        * http://flask.pocoo.org/snippets/63/
    * Flask security considerations:
        * https://damyanon.net/flask-series-security/
    * Internationalization
        * https://damyanon.net/flask-series-internationalization/
    * Flask principal tweaks:
        * https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
        * https://pythonhosted.org/Flask-Principal/
        * https://github.com/mattupstate/flask-principal/blob/master/flask_principal.py
        * https://github.com/jetpackdata/flask-login-principal/blob/master/app/mod_auth/views.py
        * https://github.com/saltycrane/flask-principal-example/blob/master/main.py
        * https://github.com/mickey06/Flask-principal-example/blob/master/FPrincipals.py
    * Flask tutorial considerations:
        * https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import click
from flask.cli import FlaskGroup

# Expose main application factories to current namespace
from .app import create_app, create_app_full

assert create_app  # type: ignore
assert create_app_full  # type: ignore


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Command line interface for the Hawat application."""


__all__ = ["cli", "create_app_full"]
