#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime
import itertools
import json
import os
import pprint
import re
import sys
import traceback
import urllib.parse
import weakref
from typing import NamedTuple, Optional, TypedDict

import flask
import flask.app
import flask.views
import flask_babel
import flask_login
import flask_migrate
import flask_principal
import jinja2
import markupsafe
import werkzeug.routing
import werkzeug.utils
from flask.json.provider import DefaultJSONProvider
from flask.signals import got_request_exception
from flask_babel import gettext

import hawat.acl
import hawat.charts
import hawat.command
import hawat.const
import hawat.db
import hawat.errors
import hawat.events
import hawat.forms
import hawat.intl
import hawat.jsglue
import hawat.log
import hawat.mailer
import hawat.menu
import hawat.utils
import hawat.view
import mentat
import mentat._buildmeta
import mentat.const
import mentat.datatype.sqldb
import mentat.idea.internal
import mentat.idea.jsondict
import mentat.services.eventstorage
import mentat.services.sqlstorage

CRE_QNAME = re.compile(r"^([\d]+)_([a-z]{6})$")
RE_UQUERY = ' AS "_mentatq\\({:d}_[^)]+\\)_"'


class HawatException(Exception):
    """
    Custom class for :py:class:`hawat.app.Hawat` application exceptions.
    """


class HawatJSONEncoder(DefaultJSONProvider):
    """
    Custom JSON encoder for converting anything into JSON strings.
    """

    def default(self, o):
        try:
            if isinstance(o, mentat.idea.internal.Idea):
                return mentat.idea.jsondict.Idea(o).data
        except Exception:
            pass
        try:
            if isinstance(o, datetime.datetime):
                return o.isoformat() + "Z"
        except Exception:
            pass
        try:
            return o.to_dict()
        except Exception:
            pass
        try:
            return str(o)
        except Exception:
            pass
        return super().default(self, o)


class CsagIdentifier(NamedTuple):
    csag_group: str
    module_name: Optional[str]
    view_name: Optional[str]
    id: Optional[str]
    """
    Optional unique identifier of search action.
    Useful when generating custom context for a specific context search action,
    which cannot be solely identified by its module and view names.
    """


class CsagDict(TypedDict):
    identifier: CsagIdentifier
    title: str | flask_babel.LazyString
    title_contextless: Optional[str | flask_babel.LazyString]
    title_context_nonrelevant: Optional[str | flask_babel.LazyString]


class CsagViewDict(CsagDict):
    view: type[flask.views.View]
    params: hawat.utils.URLParamsBuilder


class CsagUrlDict(CsagDict):
    icon: str
    url: hawat.utils.URLParamsBuilder


class HawatApp(flask.Flask):
    """
    Custom implementation of :py:class:`flask.Flask` class. This class extends the
    capabilities of the base class with following additional features:

    Configuration based blueprint registration
        The application configuration file contains a directive describing list
        of requested blueprints/modules, that should be registered into the
        application. This enables administrator to very easily fine tune the
        application setup for each installation. See the :py:func:`hawat.base.HawatApp.register_blueprints`
        for more information on the topic.

    Application main menu management
        The application provides three distinct menus, that are at a disposal for
        blueprint/module designer.

    Mentat config access
        The application provides access to Mentat`s core configurations.
    """

    csag: dict[str, list[CsagViewDict | CsagUrlDict]]

    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)

        self.csrf = None

        self.mailer = None

        self.menu_main = hawat.menu.Menu()
        self.menu_auth = hawat.menu.Menu()
        self.menu_anon = hawat.menu.Menu()

        self.sign_ins = {}
        self.sign_ups = {}
        self.resources = {}
        self.infomailers = {}

        self.csag = {}
        self.oads = {}

        self.jinja_options.setdefault("extensions", []).append("jinja2_highlight.HighlightExtension")

    @property
    def mconfig(self):
        """
        Return Mentat specific configuration sub-dictionary.
        """
        return self.config[hawat.const.CFGKEY_MENTAT_CORE]

    @property
    def icons(self):
        """
        Application icon registry.
        """
        return self.config.get("ICONS")

    def add_url_rule(
        self,
        rule,
        endpoint=None,
        view_func=None,
        provide_automatic_options=None,
        **options,
    ):
        """
        Reimplementation of :py:func:`flask.Flask.add_url_rule` method. This method
        is capable of disabling selected application endpoints. Keep in mind, that
        some URL rules (like application global 'static' endpoint) are created during
        the :py:func:`flask.app.Flask.__init__` method and cannot be disabled,
        because at that point the configuration of the application is not yet loaded.
        """
        if self.config.get("DISABLED_ENDPOINTS", None) and endpoint:
            if endpoint in self.config["DISABLED_ENDPOINTS"]:
                self.logger.warning(  # pylint: disable=locally-disabled,no-member
                    "Application endpoint '%s' is disabled by configuration.", endpoint
                )
                return
        # self.logger.debug(  # pylint: disable=locally-disabled,no-member
        #    "Registering URL route %s:%s:%s:%s",
        #    str(rule),
        #    str(endpoint),
        #    str(view_func),
        #    str(view_func.view_class) if hasattr(view_func, 'view_class') else '---none---',
        # )
        super().add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

    def register_blueprint(self, blueprint, **options):
        """
        Reimplementation of :py:func:`flask.Flask.register_blueprint` method. This
        method will perform standart blueprint registration and on top of that will
        perform following additional tasks:

            * Register blueprint into custom internal registry. The registry lies
              within application`s ``config`` under key :py:const:`hawat.const.CFGKEY_ENABLED_BLUEPRINTS`.
            * Call blueprint`s ``register_app`` method, if available, with ``self`` as only argument.

        :param hawat.app.HawatBlueprint blueprint: Blueprint to be registered.
        :param dict options: Additional options, will be passed down to :py:func:`flask.Flask.register_blueprint`.
        """
        super().register_blueprint(blueprint, **options)

        if isinstance(blueprint, HawatBlueprint):
            if hasattr(blueprint, "register_app"):
                blueprint.register_app(self)

            self.sign_ins.update(blueprint.sign_ins)
            self.sign_ups.update(blueprint.sign_ups)

    def register_blueprints(self):
        """
        Register all configured application blueprints. The configuration comes
        from :py:const:`hawat.const.CFGKEY_ENABLED_BLUEPRINTS` configuration
        subkey, which must contain list of string names of required blueprints.
        The blueprint module must provide ``get_blueprint`` factory method, that
        must return valid instance of :py:class:`hawat.app.HawatBlueprint`. This
        method will call the :py:func:`hawat.app.Hawat.register_blueprint` for
        each blueprint, that is being registered into the application.

        :raises hawat.app.HawatException: In case the factory method ``get_blueprint`` is not provided by loaded module.
        """
        for name in self.config[hawat.const.CFGKEY_ENABLED_BLUEPRINTS]:
            self.logger.debug(  # pylint: disable=locally-disabled,no-member
                "Loading pluggable module %s", name
            )
            mod = werkzeug.utils.import_string(name)
            if hasattr(mod, "get_blueprint"):
                self.register_blueprint(mod.get_blueprint())
            else:
                raise HawatException(
                    f"Invalid blueprint module '{name}', does not provide the 'get_blueprint' factory method."
                )

    @staticmethod
    def _get_exception_log_message(exc_info, label=""):
        """
        Returns formatted log message about an Exception in Hawat.
        Adds extra information such as request details, traceback and environment.
        """
        request = flask.request
        if request.content_type:
            if request.content_type == "application/json":
                body = json.dumps(request.get_json(silent=True), indent=2)
            elif request.content_type.startswith("application/x-www-form-urlencoded"):
                body = pprint.pformat(request.form.to_dict())
            else:
                body = request.get_data(as_text=True)
        else:
            body = "---"

        if label:
            label += "\n\n"  # For easier formatting

        return f"""INTERNAL SERVER ERROR

Request: {request.method} {request.full_path}
User: {flask_login.current_user}
Session: {flask.session}

==================
Traceback
==================
{label}{"".join(exc_info.format()).strip()}

==================
Request body
==================
{body}

==================
Request headers
==================
{str(request.headers).strip()}

==================
Environment
==================
{pprint.pformat(dict(os.environ))}"""

    def log_exception(self, exc_info):
        """
        Reimplementation of :py:func:`flask.Flask.log_exception` method.
        """
        flask.current_app.logger.critical(
            self._get_exception_log_message(traceback.TracebackException(*sys.exc_info()))
        )

    def eh_internal_server_error(self, err):
        """Flask error handler to be called to service HTTP 500 error."""
        return hawat.errors.error_handler_switch(500, err)

    def handle_exception(self, e):
        """
        Reimplementation of :py:func:`flask.Flask.handle_exception` method.

        The original function logs exceptions only when not propagating for debugger.
        As it is helpful to have both the propagated exception and a log, this
        reimplementation logs the exception at the start.
        """
        exc_info = sys.exc_info()
        got_request_exception.send(self, _async_wrapper=self.ensure_sync, exception=e)
        self.log_exception(exc_info)
        propagate = self.config["PROPAGATE_EXCEPTIONS"]

        if propagate is None:
            propagate = self.testing or self.debug

        if propagate:
            # Re-raise if called with an active exception, otherwise
            # raise the passed in exception.
            if exc_info[1] is e:
                raise  # pylint: disable=misplaced-bare-raise  # noqa: PLE0704

            raise e

        server_error = self.ensure_sync(self.eh_internal_server_error)(e)
        return self.finalize_request(server_error, from_error_handler=True)

    def log_exception_with_label(self, tbexc, label=""):
        """
        Log given exception traceback into application logger.
        """
        self.logger.error(self._get_exception_log_message(tbexc, label))

    # --------------------------------------------------------------------------

    def get_modules(self, filter_func=None):
        """
        Get all currently registered application modules.
        """
        if not filter_func:
            return self.blueprints
        return {k: v for k, v in self.blueprints.items() if filter_func(k, v)}

    def has_endpoint(self, endpoint):
        """
        Check if given routing endpoint is available.

        :param str endpoint: Application routing endpoint.
        :return: ``True`` in case endpoint exists, ``False`` otherwise.
        :rtype: bool
        """
        return endpoint in self.view_functions

    def get_endpoints(self, filter_func=None):
        """
        Get all currently registered application endpoints.
        """
        if not filter_func:
            return {k: v.view_class for k, v in self.view_functions.items() if hasattr(v, "view_class")}
        return {
            k: v.view_class
            for k, v in self.view_functions.items()
            if hasattr(v, "view_class") and filter_func(k, v.view_class)
        }

    def get_endpoint_class(self, endpoint, quiet=False):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :param bool quiet: Suppress the exception in case given endpoint does not exist.
        :return: Reference to view class.
        :rtype: class
        """
        if endpoint not in self.view_functions:
            if quiet:
                return None
            raise HawatException(f"Unknown endpoint name '{endpoint}'.")
        try:
            return self.view_functions[endpoint].view_class
        except AttributeError:
            return hawat.view.DecoratedView(self.view_functions[endpoint])

    def can_access_endpoint(self, endpoint, **kwargs):
        """
        Check, that the current user can access given endpoint/view.

        :param str endpoint: Application routing endpoint.
        :param dict kwargs: Optional endpoint parameters.
        :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
        :rtype: bool
        """
        try:
            view_class = self.get_endpoint_class(endpoint)

            # Reject unauthenticated users in case view requires authentication.
            if view_class.authentication:
                if not flask_login.current_user.is_authenticated:
                    return False

            # Check view authorization rules.
            if view_class.authorization:
                for auth_rule in view_class.authorization:
                    if not auth_rule.can():
                        return False

            # Check item action authorization callback, if exists.
            if hasattr(view_class, "authorize_item_action"):
                if not view_class.authorize_item_action(**kwargs):
                    return False

            return True

        except HawatException:
            return False

    def get_model(self, name):
        """
        Return reference to class of given model.

        :param str name: Name of the model.
        """
        return self.config[hawat.const.CFGKEY_MODELS][name]

    def get_resource(self, name):
        """
        Return reference to given registered resource.

        :param str name: Name of the resource.
        """
        return self.resources[name]()

    def set_resource(self, name, resource):
        """
        Store reference to given resource.

        :param str name: Name of the resource.
        :param resource: Resource to be registered.
        """
        self.resources[name] = weakref.ref(resource)

    def set_infomailer(self, name, mailer):
        """
        Register mailer handle to be usable by different web interface components.

        :param str name: Name of the informailer.
        :param callable mailer: Mailer handle.
        """
        self.infomailers.setdefault(name, []).append(mailer)

    def send_infomail(self, name, **kwargs):
        """
        Send emails through all registered infomailer handles.

        :param str name: Name of the informailer.
        :param kwargs: Additional mailer arguments.
        """
        for mailer in self.infomailers[name]:
            mailer(**kwargs)

    def get_csag(self, group_name: str) -> list[CsagViewDict | CsagUrlDict]:
        """
        Return list of all registered context search actions for given group name
        (CSAG: Context Search Action Group).

        :param str group_name: Name of the group.
        :return: List of all registered context search actions.
        """
        return self.csag.get(group_name, [])

    def set_csag(
        self,
        group_name: str,
        title: str | flask_babel.LazyString,
        view_class: type[hawat.view.BaseView],
        params_builder: hawat.utils.URLParamsBuilder,
        id_: Optional[str] = None,
        title_contextless: Optional[str | flask_babel.LazyString] = None,
        title_context_nonrelevant: Optional[str | flask_babel.LazyString] = None,
    ) -> None:
        """
        Store new context search action for given group name (CSAG: Context Search
        Action Group).

        :param str group_name: Name of the group.
        :param str title: Title for the search action.
        :param class view_class: Associated view class.
        :param URLParamsBuilder params_builder: URL parameter builder for this action.
        :param str id_: Unique identifier for this action.
        :param str title_contextless: Title for the contextless search action. if not provided,
               contextless action version will not be rendered.
        :param str title_context_nonrelevant: Title for the search action to be shown in case
               the context is either not provided or not relevant. If not provided, `title` will be used.
        """
        identifier = CsagIdentifier(group_name, view_class.module_name, view_class.get_view_name(), id_)

        self.csag.setdefault(group_name, []).append(
            {
                "identifier": identifier,
                "title": title,
                "view": view_class,
                "params": params_builder,
                "title_contextless": title_contextless,
                "title_context_nonrelevant": title_context_nonrelevant,
            }
        )

    def set_csag_url(
        self,
        group_name: str,
        title: str | flask_babel.LazyString,
        icon: str,
        url_builder: hawat.utils.URLParamsBuilder,
        id_: Optional[str] = None,
        title_contextless: Optional[str | flask_babel.LazyString] = None,
        title_context_nonrelevant: Optional[str | flask_babel.LazyString] = None,
    ) -> None:
        """
        Store new URL based context search action for given group name (CSAG: Context
        Search Action Group).

        :param str group_name: Name of the group.
        :param str title: Title for the search action.
        :param str icon: Icon for the search action.
        :param func url_builder: URL builder for this action.
        :param str id_: Unique identifier for this action.
        :param str title_contextless: Title for the contextless search action. if not provided,
               contextless action version will not be rendered.
        """

        identifier = CsagIdentifier(group_name, None, None, id_)

        self.csag.setdefault(group_name, []).append(
            {
                "identifier": identifier,
                "title": title,
                "icon": icon,
                "url": url_builder,
                "title_contextless": title_contextless,
                "title_context_nonrelevant": title_context_nonrelevant,
            }
        )

    def get_oads(self, group_name):
        """
        Return list of all registered object additional data services for given
        object group name (OADS: Additional Object Data Service).

        :param str group_name: Name of the group.
        :return: List of all object additional data services.
        :rtype: list
        """
        return self.oads.get(group_name, [])

    def set_oads(self, group_name, view_class, params_builder):
        """
        Store new object additional data services for given object group name
        (OADS: Additional Object Data Service).

        :param str group_name: Name of the group.
        :param class view_class: Associated view class.
        :param URLParamsBuilder params_builder: URL parameter builder for this action.
        """
        self.oads.setdefault(group_name, []).append({"view": view_class, "params": params_builder})

    # --------------------------------------------------------------------------

    def setup_app(self):
        """
        Perform setup of the whole application.
        """
        self._setup_app_logging()
        self._setup_app_mailer()
        self._setup_app_core()
        self._setup_app_db()
        self._setup_app_auth()
        self._setup_app_acl()
        self._setup_app_intl()
        self._setup_app_menu()
        self._setup_app_blueprints()
        self._setup_app_cli()
        self._setup_app_eventdb()

    def _setup_app_logging(self):
        """
        Setup logging to file and via email for given Hawat application. Logging
        capabilities are adjustable by application configuration.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        hawat.log.setup_logging_default(self)
        hawat.log.setup_logging_file(self)
        hawat.log.setup_logging_email(self)

        return self

    def _setup_app_mailer(self):
        """
        Setup mailer service for Hawat application.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        self.mailer = hawat.mailer.MAILER

        return self

    def _setup_app_core(self):
        """
        Setup application core for given Hawat application. The application core
        contains following features:

            * Error handlers
            * Default routes
            * Additional custom Jinja template variables
            * Additional custom Jinja template macros

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """

        def _log_bad_request():
            flask.current_app.logger.critical(
                "BAD REQUEST\n\nRequest: %s\nUser: %s\nSession: %s\nTraceback:\n%s",
                flask.request.full_path,
                flask_login.current_user,
                flask.session,
                "".join(traceback.TracebackException(*sys.exc_info()).format()),
            )

        @self.errorhandler(400)
        def eh_badrequest(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called to service HTTP 400 error."""
            _log_bad_request()
            return hawat.errors.error_handler_switch(400, err)

        @self.errorhandler(403)
        def eh_forbidden(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called to service HTTP 403 error."""
            return hawat.errors.error_handler_switch(403, err)

        @self.errorhandler(404)
        def eh_page_not_found(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called to service HTTP 404 error."""
            return hawat.errors.error_handler_switch(404, err)

        @self.errorhandler(405)
        def eh_method_not_allowed(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called to service HTTP 405 error."""
            return hawat.errors.error_handler_switch(405, err)

        @self.errorhandler(410)
        def eh_gone(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called to service HTTP 410 error."""
            return hawat.errors.error_handler_switch(410, err)

        @self.errorhandler(mentat.services.eventstorage.QueryCanceledException)
        def eh_query_cancelled(err):  # pylint: disable=locally-disabled,unused-variable
            """Flask error handler to be called on QueryCanceledException"""
            return hawat.errors.error_handler_switch(499, err)

        @self.errorhandler(hawat.errors.RegistrationException)
        def eh_registration_exception(err):
            """Flask error handler to be called on RegistrationException"""
            _log_bad_request()
            return hawat.errors.error_handler_switch(400, err)

        self.register_error_handler(500, self.eh_internal_server_error)

        @self.before_request
        def before_request():  # pylint: disable=locally-disabled,unused-variable
            """
            Use Flask`s :py:func:`flask.Flask.before_request` hook for performing
            various usefull tasks before each request.
            """
            flask.g.requeststart = datetime.datetime.utcnow()

        @self.before_request
        def logout_disabled_users():
            """
            Before each request, check if the current user is disabled. If the user is disabled,
            log them out and abort the request with a 403 Forbidden status.
            """

            def _current_user_is_disabled():
                """
                Check if the current user is disabled.

                This method checks if the current user is an instance of `mentat.datatype.sqldb.UserModel`
                and if they are inactive.

                If the particular view doesn't require authentication, then it doesn't matter if the user
                is active or not (with no authentication we have an anonymous user).

                :return: True if the current user is an instance of `UserModel` and is disabled, otherwise False.
                :rtype: bool
                """
                # pylint: disable=locally-disabled,protected-access
                current_user_obj = flask_login.current_user._get_current_object()
                if isinstance(current_user_obj, mentat.datatype.sqldb.UserModel):
                    return not flask_login.current_user.is_active
                return False

            def _logout_current_user():
                """
                Log out the current user.

                This method logs out the current user using Flask-Login's `logout_user`
                and removes session keys set by Flask-Principal. It also sends an identity
                changed signal with an AnonymousIdentity.
                """
                flask_login.logout_user()

                # Remove session keys set by Flask-Principal.
                for key in ("identity.name", "identity.auth_type"):
                    flask.session.pop(key, None)

                # Tell Flask-Principal the identity changed.
                flask_principal.identity_changed.send(
                    flask.current_app._get_current_object(),  # pylint: disable=locally-disabled,protected-access
                    identity=flask_principal.AnonymousIdentity(),
                )

                return flask.abort(403)

            if _current_user_is_disabled():
                return _logout_current_user()
            return None

        @self.context_processor
        def jinja_inject_variables():  # pylint: disable=locally-disabled,unused-variable
            """
            Inject additional variables into Jinja2 global template namespace.
            """
            return {
                "hawat_appname": flask.current_app.config["APPLICATION_NAME"],
                "hawat_appid": flask.current_app.config["APPLICATION_ID"],
                "hawat_current_app": flask.current_app,
                "hawat_current_menu_main": flask.current_app.menu_main,
                "hawat_current_menu_auth": flask.current_app.menu_auth,
                "hawat_current_menu_anon": flask.current_app.menu_anon,
                "hawat_current_view": self.get_endpoint_class(flask.request.endpoint, True),
                "hawat_logger": flask.current_app.logger,
                "hawat_cdt_utc": datetime.datetime.utcnow(),
                "hawat_cdt_local": datetime.datetime.now(),
                "hawat_version": mentat.__version__,
                "hawat_bversion": mentat._buildmeta.__bversion__,  # pylint: disable=locally-disabled,protected-access
                "hawat_bversion_full": mentat._buildmeta.__bversion_full__,  # pylint: disable=locally-disabled,protected-access
                "hawat_table_aggregations": hawat.charts.TABLE_AGGREGATIONS,
                "hawat_color_list": hawat.charts.COLOR_LIST,
                "EVENT_CLASS_STATE": mentat.datatype.sqldb.EventClassState,
            }

        @self.context_processor
        def jinja2_inject_functions():  # pylint: disable=locally-disabled,unused-variable,too-many-locals
            """
            Register additional helpers into Jinja2 global template namespace.
            """

            def get_modules_dict():
                """
                Return dictionary of all registered application pluggable modules.
                """
                return flask.current_app.blueprints

            def get_endpoints_dict():
                """
                Return dictionary of all registered application view endpoints.
                """
                return {
                    k: v.view_class for k, v in flask.current_app.view_functions.items() if hasattr(v, "view_class")
                }

            def get_endpoint_class(endpoint, quiet=False):
                """
                Return class reference to given view endpoint.

                :param str endpoint: Name of the view endpoint.
                :param bool quiet: Suppress the exception in case given endpoint does not exist.
                """
                return self.get_endpoint_class(endpoint, quiet)

            def check_endpoint_exists(endpoint):
                """
                Check, that given application view endpoint exists and is registered within
                the application.

                :param str endpoint: Name of the view endpoint.
                :return: ``True`` in case endpoint exists, ``False`` otherwise.
                :rtype: bool
                """
                return endpoint in self.view_functions

            def get_icon(icon_name, default_icon="missing-icon"):
                """
                Get HTML icon markup for given icon.

                :param str icon_name: Name of the icon.
                :param str default_icon: Name of the default icon.
                :return: Icon including HTML markup.
                :rtype: markupsafe.Markup
                """
                return markupsafe.Markup(
                    self.config.get("ICONS").get(icon_name, self.config.get("ICONS").get(default_icon))
                )

            def get_module_icon(endpoint, default_icon="missing-icon"):
                """
                Get HTML icon markup for parent module of given view endpoint.

                :param str endpoint: Name of the view endpoint.
                :param str default_icon: Name of the default icon.
                :return: Icon including HTML markup.
                :rtype: markupsafe.Markup
                """
                try:
                    icon = self.config.get("ICONS").get(
                        self.get_endpoint_class(endpoint).module_ref().get_module_icon(),
                        self.config.get("ICONS").get(default_icon),
                    )
                except HawatException:
                    icon = self.config.get("ICONS").get(default_icon)
                return markupsafe.Markup(icon)

            def get_endpoint_icon(endpoint, default_icon="missing-icon"):
                """
                Get HTML icon markup for given view endpoint.

                :param str endpoint: Name of the view endpoint.
                :return: Icon including HTML markup.
                :rtype: markupsafe.Markup
                """
                try:
                    icon = self.config.get("ICONS").get(
                        self.get_endpoint_class(endpoint).get_view_icon(),
                        self.config.get("ICONS").get(default_icon),
                    )
                except HawatException:
                    icon = self.config.get("ICONS").get(default_icon)
                return markupsafe.Markup(icon)

            def get_country_flag(country):
                """
                Get URL to static country flag file.

                :param str country: Name of the icon.
                :return: Country including HTML markup.
                :rtype: markupsafe.Markup
                """
                if not hawat.const.CRE_COUNTRY_CODE.match(country):
                    return get_icon("flag")

                return markupsafe.Markup(
                    '<img class="flag-img" src="{}">'.format(
                        flask.url_for(
                            "static",
                            filename=f"images/country-flags/flags-iso/shiny/16/{country.upper()}.png",
                        )
                    )
                )

            def include_raw(filename):
                """
                Include given file in raw form directly into the generated content.
                This may be usefull for example for including JavaScript files
                directly into the HTML page.
                """
                return jinja2.utils.markupsafe.Markup(self.jinja_loader.get_source(self.jinja_env, filename)[0])

            def get_csag(group):
                """
                Return list of all registered context search actions under given group.

                :param str group: Name of the group.
                :return: List of all registered context search actions.
                :rtype: list
                """
                return self.get_csag(group)

            def get_reporting_interval_name(seconds):
                """
                Get a name of reporting interval for given time delta.

                :param int seconds: Time interval delta in seconds.
                :return: Name of the reporting interval.
                :rtype: str
                """
                return mentat.const.REPORTING_INTERVALS_INV[seconds]

            def get_limit_counter(limit=None):
                """
                Get fresh instance of limit counter.
                """
                if not limit:
                    limit = flask.current_app.config["HAWAT_LIMIT_AODS"]
                return hawat.utils.LimitCounter(limit)

            def iter_separated(string):
                """
                Iterate over string separated by either comma, semicolon, or whitespace, while keeping the separators
                """
                # In python 3.12 can be rewritten as:
                # for s, *sep in itertools.batched(re.split(r'([,;\s]{1,5})', s), 2):
                #    yield s + ''.join(sep)
                iterator = iter(re.split(r"([,;\s]{1,5})", string))  # Match at most 5 consecutive separators
                s, *sep = itertools.islice(iterator, 2)
                while sep:
                    yield s + sep[0]
                    s, *sep = itertools.islice(iterator, 2)
                yield s

            return {
                "get_modules_dict": get_modules_dict,
                "get_endpoints_dict": get_endpoints_dict,
                "get_endpoint_class": get_endpoint_class,
                "check_endpoint_exists": check_endpoint_exists,
                "get_icon": get_icon,
                "get_module_icon": get_module_icon,
                "get_endpoint_icon": get_endpoint_icon,
                "get_country_flag": get_country_flag,
                "get_redirect_target": hawat.forms.get_redirect_target,
                "get_timedelta": hawat.utils.get_timedelta,
                "get_datetime_utc": hawat.utils.get_datetime_utc,
                "get_datetime_local": hawat.utils.get_datetime_local,
                "parse_datetime": hawat.utils.parse_datetime,
                "get_datetime_window": hawat.view.mixin.HawatUtils.get_datetime_window,
                "check_file_exists": hawat.utils.check_file_exists,
                "in_query_params": hawat.utils.in_query_params,
                "generate_query_params": hawat.utils.generate_query_params,
                "current_datetime_utc": datetime.datetime.utcnow(),
                "include_raw": include_raw,
                "get_uuid4": hawat.utils.get_uuid4,
                "load_json_from_file": hawat.utils.load_json_from_file,
                "make_copy_deep": hawat.utils.make_copy_deep,
                "parse_csv": hawat.utils.parse_csv,
                "decode_url": urllib.parse.unquote,
                "get_csag": get_csag,
                "get_reporting_interval_name": get_reporting_interval_name,
                "get_limit_counter": get_limit_counter,
                "iter_separated": iter_separated,
            }

        @self.template_filter("tojson_pretty")
        def to_pretty_json(value):  # pylint: disable=locally-disabled,unused-variable
            return self.json.dumps(value, sort_keys=True, indent=4)

        @self.route("/app-main.js")
        def mainjs():  # pylint: disable=locally-disabled,unused-variable
            """
            Default route for main application JavaScript file.
            """
            return flask.make_response(
                flask.render_template("app-main.js"),
                200,
                {"Content-Type": "text/javascript"},
            )

        # Initialize JSGlue plugin for using `flask.url_for()` method in JavaScript.
        # jsglue = flask_jsglue.JSGlue()
        jsglue = hawat.jsglue.JSGlue()
        jsglue.init_app(self)

        @self.template_filter()
        def pprint_item(item):  # pylint: disable=locally-disabled,unused-variable
            """
            Custom Jinja2 filter for full object attribute dump/pretty-print.
            """
            res = [f"{key!r}: {getattr(item, key)!r}" for key in dir(item)]
            return "\n".join(res)

        return self

    def _setup_app_db(self):
        """
        Setup application database service for given Hawat application.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        dbh = hawat.db.db_setup(**self.config["SQLALCHEMY_SETUP_ARGS"])
        dbh.init_app(self)

        # Initialize database migration service and register it among the application
        # resources for possible future use.
        migrate = flask_migrate.Migrate(app=self, db=dbh, directory=self.config["MIGRATE_DIRECTORY"])
        self.set_resource(hawat.const.RESOURCE_MIGRATE, migrate)

        self.logger.debug(
            "Connected to database via SQLAlchemy (%s)",
            str(self.config["SQLALCHEMY_DATABASE_URI"]),
        )

        class StorageService:  # pylint: disable=locally-disabled,too-few-public-methods
            """
            This is a thin proxy class, that can be used in place of
            :py:class:`mentat.services.sqlstorage.StorageService`.
            This is necessary for certain services like :py:mod:`mentat.services.whois`,
            that require some access to database storage service and are hardcoded to
            use :py:class:`mentat.services.sqlstorage.StorageService`.
            This is necessary when using the services from Flask framework, because there
            is another storage service management feature in place using the py:mod:`flask_sqlalchemy`
            module.
            """

            @property
            def session(self):
                """
                Thin proxy property for retrieving reference to current database session.
                """
                return hawat.db.db_session()

        class StorageServiceManager:  # pylint: disable=locally-disabled,too-few-public-methods
            """
            This is a thin proxy class, that can be used in place of :py:class:`mentat.services.sqlstorage.StorageServiceManager`.
            This is necessary for certain services like :py:mod:`mentat.services.whois`, that require
            some access to database storage service manager and are hardcoded to use :py:class:`mentat.services.sqlstorage.StorageServiceManager`.
            This is necessary when using the services from Flask framework, because there
            is another storage service management feature in place using the py:mod:`flask_sqlalchemy`
            module.
            """

            @staticmethod
            def service():
                """
                Thin proxy property for retrieving reference to current database storage
                service.
                """
                return StorageService()

        mentat.services.sqlstorage.set_manager(StorageServiceManager())

        return self

    def _setup_app_auth(self):
        """
        Setup application authentication features.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """

        lim = flask_login.LoginManager()
        lim.init_app(self)
        lim.login_view = self.config["ENDPOINT_LOGIN"]
        lim.login_message = flask_babel.gettext("Please log in to access this page.")
        lim.login_message_category = self.config["LOGIN_MSGCAT"]

        self.set_resource(hawat.const.RESOURCE_LOGIN_MANAGER, lim)

        @lim.user_loader
        def load_user(user_id):  # pylint: disable=locally-disabled,unused-variable
            """
            Flask-Login callback for loading current user`s data.
            """
            user_model = self.get_model(hawat.const.MODEL_USER)
            return hawat.db.db_get().session.query(user_model).filter(user_model.id == user_id).one_or_none()

        @lim.unauthorized_handler
        def unauthorized():
            if "/api/" in flask.request.base_url:
                response = hawat.errors.api_error_response(401)
                flask.abort(response)
            return flask.redirect(flask.url_for(lim.login_view, next=flask.request.url))

        @self.route("/logout")
        @flask_login.login_required
        def logout():  # pylint: disable=locally-disabled,unused-variable
            """
            Flask-Login callback for logging out current user.
            """
            flask.current_app.logger.info(f"User '{flask_login.current_user!s}' just logged out.")
            flask_login.logout_user()
            flask.flash(
                flask_babel.gettext("You have been successfully logged out."),
                hawat.const.FLASH_SUCCESS,
            )

            # Remove session keys set by Flask-Principal.
            for key in ("identity.name", "identity.auth_type"):
                flask.session.pop(key, None)

            # Tell Flask-Principal the identity changed.
            flask_principal.identity_changed.send(
                flask.current_app._get_current_object(),  # pylint: disable=locally-disabled,protected-access
                identity=flask_principal.AnonymousIdentity(),
            )

            # Force user to index page.
            return flask.redirect(flask.url_for(flask.current_app.config["ENDPOINT_LOGOUT_REDIRECT"]))

        return self

    def _setup_app_acl(self):
        """
        Setup application ACL features.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        fpp = flask_principal.Principal(self, skip_static=False)
        self.set_resource(hawat.const.RESOURCE_PRINCIPAL, fpp)

        @flask_principal.identity_loaded.connect_via(self)
        def on_identity_loaded(sender, identity):  # pylint: disable=locally-disabled,unused-variable,unused-argument
            """
            Flask-Principal callback for populating user identity object after login.
            """
            # Set the identity user object.
            identity.user = flask_login.current_user

            if not flask_login.current_user.is_authenticated:
                flask.current_app.logger.debug(
                    f"Loaded ACL identity for anonymous user '{flask_login.current_user!s}'."
                )
                return
            flask.current_app.logger.debug(f"Loading ACL identity for user '{flask_login.current_user!s}'.")

            # Add the UserNeed to the identity.
            if hasattr(flask_login.current_user, "get_id"):
                identity.provides.add(flask_principal.UserNeed(flask_login.current_user.id))

            # Assuming the User model has a list of roles, update the
            # identity with the roles that the user provides.
            if hasattr(flask_login.current_user, "roles"):
                for role in flask_login.current_user.roles:
                    identity.provides.add(flask_principal.RoleNeed(role))

            # Assuming the User model has a list of group memberships, update the
            # identity with the groups that the user is member of.
            if hasattr(flask_login.current_user, "memberships"):
                for group in flask_login.current_user.memberships:
                    identity.provides.add(hawat.acl.MembershipNeed(group.id))

            # Assuming the User model has a list of group managements, update the
            # identity with the groups that the user is manager of.
            if hasattr(flask_login.current_user, "managements"):
                for group in flask_login.current_user.managements:
                    identity.provides.add(hawat.acl.ManagementNeed(group.id))

        @self.context_processor
        def utility_acl_processor():  # pylint: disable=locally-disabled,unused-variable
            """
            Register additional helpers related to authorization into Jinja global
            namespace to enable them within the templates.
            """

            def can_access_endpoint(endpoint, item=None):
                """
                Check if currently logged-in user can access given endpoint/view.

                :param str endpoint: Name of the application endpoint.
                :param item: Optional item for additional validations.
                :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
                :rtype: bool
                """
                return flask.current_app.can_access_endpoint(endpoint, item=item)

            def permission_can(permission_name):
                """
                Manually check currently logged-in user for given permission.

                :param str permission_name: Name of the permission.
                :return: Check result.
                :rtype: bool
                """
                return hawat.acl.PERMISSIONS[permission_name].can()

            def is_it_me(item):
                """
                Check if given user account is mine.
                """
                return item.id == flask_login.current_user.id

            return {
                "can_access_endpoint": can_access_endpoint,
                "permission_can": permission_can,
                "is_it_me": is_it_me,
            }

        return self

    def _setup_app_intl(self):
        """
        Setup application`s internationalization sybsystem.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        hawat.intl.BABEL.init_app(
            self,
            locale_selector=hawat.intl.get_locale,
            timezone_selector=hawat.intl.get_timezone,
        )
        self.set_resource(hawat.const.RESOURCE_BABEL, hawat.intl.BABEL)

        @self.route("/locale/<code>")
        def locale(code):  # pylint: disable=locally-disabled,unused-variable
            """
            Application route providing users with the option of changing locale.
            """
            if code not in flask.current_app.config["SUPPORTED_LOCALES"]:
                return flask.abort(404)

            if flask_login.current_user.is_authenticated:
                flask_login.current_user.locale = code
                # Make sure current user is in SQLAlchemy session. Turns out, this
                # step is not necessary and current user is already in session,
                # because it was fetched from database few moments ago.
                # hawat.db.db_session().add(flask_login.current_user)
                hawat.db.db_session().commit()

            flask.session["locale"] = code
            flask_babel.refresh()

            flask.flash(
                markupsafe.Markup(
                    flask_babel.gettext(
                        "Locale was succesfully changed to <strong>%(lcln)s (%(lclc)s)</strong>.",
                        lclc=code,
                        lcln=flask.current_app.config["SUPPORTED_LOCALES"][code],
                    )
                ),
                hawat.const.FLASH_SUCCESS,
            )

            # Redirect user back to original page.
            return flask.redirect(
                hawat.forms.get_redirect_target(default_url=flask.url_for(flask.current_app.config["ENDPOINT_HOME"]))
            )

        @self.before_request
        def before_request():  # pylint: disable=locally-disabled,unused-variable
            """
            Use Flask`s :py:func:`flask.Flask.before_request` hook for storing
            currently selected locale and timezone to request`s session storage.
            """
            if "locale" not in flask.session:
                flask.session["locale"] = hawat.intl.get_locale()
            if "timezone" not in flask.session:
                flask.session["timezone"] = hawat.intl.get_timezone()
            if flask_login.current_user.is_authenticated:
                # Mark the login time into database.
                flask_login.current_user.logintime = datetime.datetime.utcnow()
                hawat.db.db_get().session.commit()

                # Tell flask_principal that the user identity has changed.
                flask_principal.identity_changed.send(
                    flask.current_app._get_current_object(),  # pylint: disable=locally-disabled,protected-access
                    identity=flask_principal.Identity(flask_login.current_user.get_id()),
                )

        @self.context_processor
        def utility_processor():  # pylint: disable=locally-disabled,unused-variable
            """
            Register additional internationalization helpers into Jinja global namespace.
            """

            return {
                "babel_get_locale": hawat.intl.get_locale,
                "babel_get_timezone": hawat.intl.get_timezone,
                "babel_format_datetime": flask_babel.format_datetime,
                "babel_format_date": flask_babel.format_date,
                "babel_format_time": flask_babel.format_time,
                "babel_format_timedelta": flask_babel.format_timedelta,
                "babel_format_decimal": flask_babel.format_decimal,
                "babel_format_percent": flask_babel.format_percent,
                "babel_format_bytes": hawat.intl.babel_format_bytes,
                "babel_translate_locale": hawat.intl.babel_translate_locale,
                "babel_language_in_locale": hawat.intl.babel_language_in_locale,
            }

        return self

    def _setup_app_menu(self):
        """
        Setup default application menu skeleton.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        for entry in self.config[hawat.const.CFGKEY_MENU_MAIN_SKELETON]:
            self.menu_main.add_entry(**entry)

        return self

    def _setup_app_blueprints(self):
        """
        Setup application blueprints.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        self.register_blueprints()

        return self

    def _setup_app_cli(self):
        """
        Setup application command line interface.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        hawat.command.setup_cli(self)

        return self

    def _setup_app_eventdb(self):
        """
        Setup application database service for given Hawat application.

        :return: Modified Hawat application
        :rtype: hawat.app.HawatApp
        """
        hawat.events.db_init(self)
        self.logger.info("Connected to event database")

        return self


class HawatBlueprint(flask.Blueprint):
    """
    Custom implementation of :py:class:`flask.Blueprint` class. This class extends
    the capabilities of the base class with additional features:

        * Support for better integration into application and registration of view classes.
        * Support for custom tweaking of application object.
        * Support for custom style of authentication and authorization decorators
    """

    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

        self.sign_ins = {}
        self.sign_ups = {}

    @classmethod
    def get_module_title(cls):
        """
        Get human readable name for this blueprint/module.

        :return: Name (short summary) of the blueprint/module.
        :rtype: str
        """
        raise NotImplementedError()

    def get_module_icon(self):
        """
        Return icon name for the module. Given name will be used as index to
        built-in icon registry.

        :return: Icon for the module.
        :rtype: str
        """
        return f"module-{self.name}".replace("_", "-")

    def register_app(self, app):  # pylint: disable=locally-disabled,unused-argument
        """
        *Hook method:* Custom callback, which will be called from
        :py:func:`hawat.app.Hawat.register_blueprint` method and which can
        perform additional tweaking of Hawat application object.

        :param hawat.app.Hawat app: Application object.
        """
        return

    def register_view_class(self, view_class, route_spec):
        """
        Register given view class into the internal blueprint registry.

        :param hawat.view.BaseView view_class: View class (not instance!)
        :param str route_spec: Routing information for the view.
        """
        view_class.module_ref = weakref.ref(self)
        view_class.module_name = self.name

        # Obtain view function.
        view_func = view_class.as_view(view_class.get_view_name())

        # Apply authorization decorators (if requested).
        if view_class.authorization:
            for auth in view_class.authorization:
                view_func = auth.require(403)(view_func)

        # Apply authentication decorators (if requested).
        if view_class.authentication:
            view_func = flask_login.login_required(view_func)

        # Register endpoint to the application.
        self.add_url_rule(route_spec, view_func=view_func)

        # Register SIGN IN and SIGN UP views to enable further special handling.
        if hasattr(view_class, "is_sign_in") and view_class.is_sign_in:
            self.sign_ins[view_class.get_view_endpoint()] = view_class
        if hasattr(view_class, "is_sign_up") and view_class.is_sign_up:
            self.sign_ups[view_class.get_view_endpoint()] = view_class


class PsycopgMixin:
    """
    Mixin class providing generic interface for interacting with SQL database
    backend through SQLAlchemy library.
    """

    SEARCH_QUERY_QUOTA_CHECK = True

    def fetch(self, item_id):  # pylint: disable=locally-disabled
        """
        Fetch item with given primary identifier from the database.
        """
        return hawat.events.db_get().fetch_event(item_id)

    @staticmethod
    def get_db():
        """
        Get database connection service.

        :return: database connection service.
        :rtype: mentat.services.eventstorage.EventStorageService
        """
        return hawat.events.db_get()

    @staticmethod
    def get_qtype():
        """
        Get type of the event select query.
        """
        return mentat.services.eventstorage.QTYPE_SELECT

    @staticmethod
    def get_qname():
        """
        Get unique name for the event select query.
        """
        return f"{flask_login.current_user.get_id()}_{mentat.const.random_str(6)}"

    @staticmethod
    def parse_qname(qname):
        """
        Get unique name for the event select query.
        """
        match = CRE_QNAME.match(qname)
        if match is None:
            return None, None
        return match.group(1), match.group(2)

    def _check_search_query_quota(self):
        limit = flask.current_app.config["HAWAT_SEARCH_QUERY_QUOTA"]
        qlist = hawat.events.db_get().queries_status(RE_UQUERY.format(int(flask_login.current_user.get_id())))
        if len(qlist) >= limit:
            self.abort(
                400,
                gettext(
                    'You have reached your event search query quota: %(limit)s queries. Please wait for your queries to finish and try again. You may also review all your <a href="%(url)s">currently running queries</a>.',
                    limit=limit,
                    url=flask.url_for("dbstatus.queries_my"),
                ),
            )

    def search(self, form_args):
        """
        Perform actual search of IDEA events using provided query arguments.

        :param dict form_args: Search query arguments.
        :return: Tuple containing number of items as integer and list of searched items.
        :rtype: tuple
        """
        if self.SEARCH_QUERY_QUOTA_CHECK:
            self._check_search_query_quota()

        query_name = self.get_qname()
        items_count_total = 0
        items = []

        # When searching using StorageTime, ignore DetectTime values.
        if form_args.get("st_from", None) or form_args.get("st_to", None):
            form_args["dt_from"] = None
            form_args["dt_to"] = None

        # TLP authorization. If user has higher permissions, all events will be searched,
        # so it is not necessary to pass the current user to this method.
        user = None if hawat.acl.PERMISSION_POWER.can() else flask_login.current_user
        items_count_total, items = self.get_db().search_events(
            form_args, qtype=self.get_qtype(), qname=query_name, user=user
        )

        self.response_context.update(
            sqlquery=self.get_db().cursor.lastquery.decode("utf-8"),
            sqlquery_name=query_name,
        )
        return items
