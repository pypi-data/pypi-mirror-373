#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains base classes for all *hawat* application views. They are all
based on :py:class:`flask.views.View`.
"""

import datetime
import re
import sys
import traceback
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Optional

import flask
import flask.app
import flask.views
import flask_login
import flask_principal
import markupsafe
import pytz
import sqlalchemy
from flask_babel import force_locale, gettext

import hawat.const
import hawat.db
import hawat.errors
import hawat.menu
from hawat.forms import ItemActionConfirmForm
from hawat.view.mixin import HawatUtils
from mentat.datatype.sqldb import FilterModel, UserModel, jsondiff

if TYPE_CHECKING:
    from hawat.base import CsagIdentifier


class DecoratedView:
    """
    Wrapper class for classical decorated view functions.
    """

    def __init__(self, view_function):
        self.view_function = view_function

    def get_view_name(self):
        """Simple adapter method to enable support of classical decorated views."""
        return self.view_function.__name__

    def get_view_endpoint(self):
        """Simple adapter method to enable support of classical decorated views."""
        return self.get_view_name()

    def get_view_icon(self):
        """Simple adapter method to enable support of classical decorated views."""
        return f"view-{self.get_view_name()}"


class BaseView(flask.views.View):
    """
    Base class for all custom hawat application views.
    """

    module_ref = None
    """
    Weak reference to parent module/blueprint of this view.
    """

    module_name = None
    """
    Name of the parent module/blueprint. Will be set up during the process
    of registering the view into the blueprint in :py:func:`hawat.app.hawatBlueprint.register_view_class`.
    """

    authentication = False
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authentication.
    During the process of registering the view into the blueprint in
    :py:func:`hawat.app.hawatBlueprint.register_view_class` the view will be
    automatically decorated with :py:func:`flask_login.login_required` decorator.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a scalar variable that must contain boolean ``True`` or ``False``.
    """

    authorization: Sequence[flask_principal.Permission] = ()
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authorization.
    During the process of registering the view into the blueprint in
    :py:func:`hawat.app.hawatBlueprint.register_view_class` the view will be
    automatically decorated with given authorization decorators.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a list variable that must contain list of desired decorators.
    """

    url_params_unsupported: Sequence[str] = ()
    """
    List of URL parameters, that are not supported by this view and should be removed
    before generating the URL.
    """

    @classmethod
    def get_view_name(cls):
        """
        Return unique name for the view. Name must be unique in the namespace of
        parent blueprint/module and should contain only characters ``[a-z0-9]``.
        It will be used for generating endpoint name for the view.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Name for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_view_endpoint_name(cls):
        """
        Return unique name for the view endpoint. Name must be unique in the namespace of
        parent blueprint/module and should contain only characters ``[a-z0-9]``.
        It will be used for generating endpoint name for the view.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Name for the view.
        :rtype: str
        """
        return cls.get_view_name()

    @classmethod
    def get_view_endpoint(cls):
        """
        Return name of the routing endpoint for the view within the whole application.

        Default implementation generates the endpoint name by concatenating the
        module name and view name.

        :return: Routing endpoint for the view within the whole application.
        :rtype: str
        """
        return f"{cls.module_name}.{cls.get_view_endpoint_name()}"

    @classmethod
    def get_view_url(cls, **kwargs):
        """
        Return view URL.

        :param dict kwargs: Optional parameters.
        :return: URL for the view.
        :rtype: str
        """
        # Filter out unsupported URL parameters.
        params = dict(filter(lambda x: x[0] not in cls.url_params_unsupported, kwargs.items()))
        return flask.url_for(cls.get_view_endpoint(), **params)

    @classmethod
    def get_view_icon(cls):
        """
        Return menu entry icon name for the view. Given name will be used as index
        to built-in icon registry.

        Default implementation generates the icon name by concatenating the prefix
        ``module-`` with module name.

        :return: View icon.
        :rtype: str
        """
        return "module-{}".format(cls.module_name.replace("_", "-"))

    @classmethod
    def get_view_title(cls, **kwargs):
        """
        Return title for the view, that will be displayed in the ``title`` tag of
        HTML ``head`` element and also as the content of page header in ``h2`` tag.

        Default implementation returns the return value of :py:func:`hawat.view.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Title for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_menu_title(cls, **kwargs):
        """
        Return menu entry title for the view.

        Default implementation returns the return value of :py:func:`hawat.view.BaseView.get_view_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry title for the view.
        :rtype: str
        """
        return cls.get_view_title(**kwargs)

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        Return menu entry legend for the view (menu entry hover tooltip).

        Default implementation returns the return value of :py:func:`hawat.view.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry legend for the view.
        :rtype: str
        """
        return cls.get_menu_title(**kwargs)

    # ---------------------------------------------------------------------------

    @staticmethod
    def has_endpoint(endpoint):
        """
        Check if given routing endpoint is available within the application.

        :param str endpoint: Application routing endpoint.
        :return: ``True`` in case endpoint exists, ``False`` otherwise.
        :rtype: bool
        """
        return flask.current_app.has_endpoint(endpoint)

    @staticmethod
    def get_endpoint_class(endpoint, quiet=False):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :param bool quiet: Suppress the exception in case given endpoint does not exist.
        :return: Reference to view class.
        :rtype: class
        """
        return flask.current_app.get_endpoint_class(endpoint, quiet)

    @staticmethod
    def can_access_endpoint(endpoint, **kwargs):
        """
        Check, that the current user can access given endpoint/view.

        :param str endpoint: Application routing endpoint.
        :param dict kwargs: Optional endpoint parameters.
        :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
        :rtype: bool
        """
        return flask.current_app.can_access_endpoint(endpoint, **kwargs)

    @staticmethod
    def get_model(name):
        """
        Return reference to class of given model.

        :param str name: Name of the model.
        """
        return flask.current_app.get_model(name)

    @staticmethod
    def get_resource(name):
        """
        Return reference to given registered resource.

        :param str name: Name of the resource.
        """
        return flask.current_app.get_resource(name)

    # ---------------------------------------------------------------------------

    @property
    def logger(self):
        """
        Return current application`s logger object.
        """
        return flask.current_app.logger


class FileNameView(BaseView):
    """
    Base class for direct file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return "action-download"

    @classmethod
    def get_directory_path(cls):
        """
        Return absolute path to the directory, that will be used as a base path
        for serving files.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def validate_filename(cls, filename):
        """
        Validate given file name to prevent user from accessing restricted files.

        In default implementation all files pass the validation.

        :param str filename: Name of the file to be validated/filtered.
        :return: ``True`` in case file name is allowed, ``False`` otherwise.
        :rtype: bool
        """
        return bool(filename)

    def dispatch_request(self, filename):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        if not self.validate_filename(filename):
            flask.abort(400)

        self.logger.info(f"Serving file '{filename}' from directory '{self.get_directory_path()}'.")
        return flask.send_from_directory(self.get_directory_path(), filename, as_attachment=True)


class FileIdView(BaseView):
    """
    Base class for indirrect file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    The difference between this view class and :py:class:`FileNameView` is,
    that is this case some kind of identifier is used to access the file and
    provided class method is responsible for translating this identifier into
    real file name.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return "action-download"

    @classmethod
    def get_directory_path(cls, fileid, filetype):
        """
        This method must return absolute path to the directory, that will be
        used as a base path for serving files. Parameter ``fileid`` may be used
        internally to further customize the base directory, for example when
        serving some files places into subdirectories based on some part of the
        file name (for example to reduce total number of files in base directory).

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_filename(cls, fileid, filetype):
        """
        This method must return actual name of the file based on given identifier
        and type.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Translated name of the file.
        :rtype: str
        """
        raise NotImplementedError()

    def dispatch_request(self, fileid, filetype):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        basedirpath = self.get_directory_path(fileid, filetype)
        filename = self.get_filename(fileid, filetype)
        if not basedirpath or not filename:
            flask.abort(400)

        self.logger.info(f"Serving file '{filename}' from directory '{basedirpath}'.")
        return flask.send_from_directory(basedirpath, filename, as_attachment=True)


class RenderableView(BaseView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for all views, that are rendering content based on Jinja2 templates
    or returning JSON/XML data.
    """

    def __init__(self):
        self.response_context = {}
        flask.request.view_instance = self

    def mark_time(self, ident, threshold, tag="default", label="Time mark", log=False):
        """
        Mark current time with given identifier and label for further analysis.
        This method can be usefull for measuring durations of various operations.
        """
        mark = [datetime.datetime.utcnow(), ident, threshold, tag, label]
        marks = self.response_context.setdefault("time_marks", [])
        marks.append(mark)

        if log:
            if len(marks) <= 1:
                self.logger.info("Mark {}:{} ({})".format(*mark[1:]))
            else:
                self.logger.info(
                    "Mark {}:{}:{} ({});delta={};delta0={}".format(
                        *mark[1:],
                        (str(marks[-1][0] - marks[-2][0])),  # Time delta from last mark.
                        (str(marks[-1][0] - marks[0][0])),  # Time delta from first mark.
                    )
                )

    def _flash_pagination_errors(self, form):
        """
        Given a form with errors, search for errors related to limit and page fields
        and flash those errors.
        """
        for field_name, error_messages in form.errors.items():
            if field_name in ("limit", "page"):
                self.flash(error_messages[-1], hawat.const.FLASH_FAILURE)

    def _send_email(
        self,
        to: list[str],
        subject: str,
        template_path: str,
        locale: str | None = None,
        **email_body_kwargs: Any,
    ) -> None:
        """
        Send an email using the application's mailer service.

        This method constructs an email with the given subject and recipient,
        renders the email body from a Jinja2 template, and sends it via the
        application's configured mailer service. If no locale is specified,
        the default locale from the application's configuration is used.

        :param to: The recipient's email address.
        :param subject: The subject of the email.
        :param template_path: The path to the Jinja2 template used to render the email body.
        :param locale: The locale for rendering the template (default: application default).
        :param email_body_kwargs: Additional keyword arguments passed to the template for rendering.
        :return: None
        """
        if not locale:
            locale = flask.current_app.config["BABEL_DEFAULT_LOCALE"]
        with force_locale(locale):
            email_headers = {
                "subject": subject,
                "to": to,
            }
            email_body = flask.render_template(template_path, **email_body_kwargs)
            flask.current_app.mailer.send(email_headers, email_body)

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.app.hawatBlueprint.register_view_class` method.

        :return: Jinja2 template file to use to render the view.
        :rtype: str
        """
        if cls.module_name:
            return f"{cls.module_name}/{cls.get_view_endpoint_name()}.html"
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    def get_url_cancel(self):
        """
        Returns the URL to redirect to if the action is cancelled.

        This method attempts to use the referrer URL from the request. If the referrer
        is not available or is invalid (contains 'None'), it falls back to a default
        URL defined by the application's 'ENDPOINT_HOME' configuration.

        :return: URL to redirect to on action cancel.
        :rtype: str
        """
        referrer = flask.request.referrer
        if not referrer or "None" in referrer:
            referrer = flask.url_for(flask.current_app.config["ENDPOINT_HOME"])
        return referrer

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        This method will be called just before generating the response. By providing
        some meaningfull implementation you can use it for some simple item and
        response context mangling tasks.

        :param kwargs: Custom additional arguments.
        """

    def generate_response(self):
        """
        Generate the appropriate response from given response context.

        :param dict response_context: Response context as a dictionary
        """
        raise NotImplementedError()

    def get_csag_context(
        self,
        csag_identifier: "CsagIdentifier",  # pylint: disable=locally-disabled,unused-argument
        additional_context: Any,  # pylint: disable=locally-disabled,unused-argument
    ) -> Optional[dict[str, Any]]:
        """
        Get context for the given CSAG Identifier.
        Returning None should cause the CSAG entry to be skipped from rendering within the dropdown.
        """
        return flask.request.args.to_dict(flat=False)  # type: ignore[no-any-return]

    @classmethod
    def check_csag_value_supported(cls, csag_group: str, csag_value: Any) -> bool:  # pylint: disable=locally-disabled,unused-argument
        """
        Check if the given CSAG value is actually supported.

        This is useful in cases, when the view cannot support all
        possible values which are marked with a CSAG group.

        (E.g. Hostinfo does not support ip ranges and networks, but does support single IP addresses.)
        """
        return True

    @staticmethod
    def abort(status_code, message=None):
        """
        Abort request processing with HTTP status code.
        """
        raise NotImplementedError()

    def flash(self, message, level="info"):
        """
        Flash information to the user.
        """
        raise NotImplementedError()

    def redirect(self, target_url=None, default_url=None, exclude_url=None):
        """
        Redirect user to different location.
        """
        raise NotImplementedError()


class SimpleView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for simple views. These are the most, well, simple views, that are
    rendering single template file or directly returning some JSON/XML data without
    any user parameters.

    In most use cases, it should be enough to just enhance the default implementation
    of :py:func:`hawat.view.RenderableView.get_response_context` to inject
    some additional variables into the template.
    """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        redirect = self.do_before_response()  # pylint: disable=assignment-from-no-return
        if redirect:
            return redirect
        return self.generate_response()


class BaseLoginView(SimpleView):
    """
    Base class for login views.
    """

    is_sign_in = True

    @classmethod
    def get_view_name(cls):
        return hawat.const.ACTION_USER_LOGIN

    @classmethod
    def get_view_icon(cls):
        return hawat.const.ACTION_USER_LOGIN

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("Login")

    @classmethod
    def get_menu_title(cls, **kwargs):
        return gettext("Login")

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        raise NotImplementedError()

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    def fetch(self, item_id):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    def get_user_login(self):
        """
        Get login of the user that is being authenticated.
        """
        raise NotImplementedError()

    def authenticate_user(self, user):  # pylint: disable=locally-disabled,unused-argument
        """
        Authenticate given user.
        """
        return True

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """

        def _get_user(user_login):
            try:
                return self.fetch(user_login)
            except sqlalchemy.orm.exc.NoResultFound:
                return None

        if flask_login.current_user.is_authenticated:
            return self.redirect(default_url=flask.url_for(flask.current_app.config["ENDPOINT_LOGIN_REDIRECT"]))

        user_login = self.get_user_login()
        if user_login:
            user = _get_user(user_login)

            if not user:
                self.flash(
                    gettext("You have entered wrong login credentials."),
                    hawat.const.FLASH_FAILURE,
                )
                self.abort(403)

            if not user.enabled:
                self.flash(
                    markupsafe.Markup(
                        gettext(
                            "Your user account <strong>%(login)s (%(name)s)</strong> is currently disabled, you are not permitted to log in.",
                            login=markupsafe.escape(user.login),
                            name=markupsafe.escape(user.fullname),
                        )
                    ),
                    hawat.const.FLASH_FAILURE,
                )
                self.abort(403)

            if not self.authenticate_user(user):
                self.flash(
                    gettext("You have used wrong login credentials."),
                    hawat.const.FLASH_FAILURE,
                )
                self.abort(403)

            flask_login.login_user(user)

            # Tell Flask-Principal the identity changed. Access to private method
            # _get_current_object is according to the Flask documentation:
            #   http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
            flask_principal.identity_changed.send(
                flask.current_app._get_current_object(),  # pylint: disable=locally-disabled,protected-access
                identity=flask_principal.Identity(user.get_id()),
            )

            self.flash(
                markupsafe.Markup(
                    gettext(
                        "You have been successfully logged in as <strong>%(user)s</strong>.",
                        user=markupsafe.escape(str(user)),
                    )
                ),
                hawat.const.FLASH_SUCCESS,
            )
            self.logger.info(f"User '{user.login}' successfully logged in with '{self.module_name}'.")

            # Redirect user back to original page.
            return self.redirect(default_url=flask.url_for(flask.current_app.config["ENDPOINT_LOGIN_REDIRECT"]))

        self.response_context.update(next=hawat.forms.get_redirect_target())
        return self.generate_response()


class BaseSearchView(RenderableView, HawatUtils):
    """
    Base class for search views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "search"

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return "action-search"

    # ---------------------------------------------------------------------------

    @classmethod
    def get_quicksearch_by_time(cls):
        """
        Get default list of 'by time' quickseach items.
        """
        quicksearch_list = []
        for item in (
            ["1h", gettext("Search for last hour")],
            ["2h", gettext("Search for last 2 hours")],
            ["3h", gettext("Search for last 3 hours")],
            ["4h", gettext("Search for last 4 hours")],
            ["6h", gettext("Search for last 6 hours")],
            ["12h", gettext("Search for last 12 hours")],
            ["1d", gettext("Search for last day")],
            ["2d", gettext("Search for last 2 days")],
            ["3d", gettext("Search for last 3 days")],
            ["1w", gettext("Search for last week")],
            ["2w", gettext("Search for last 2 weeks")],
            ["4w", gettext("Search for last 4 weeks")],
            ["12w", gettext("Search for last 12 weeks")],
            ["td", gettext("Search for today")],
            ["tw", gettext("Search for this week")],
            ["tm", gettext("Search for this month")],
            ["ty", gettext("Search for this year")],
        ):
            try:
                dt_from = cls.get_datetime_window(
                    item[0],
                    "current",
                    moment=datetime.datetime.now(pytz.timezone(flask.session.get("timezone", "UTC"))),
                )
                dt_to = cls.get_datetime_window(item[0], "next", dt_from)
                quicksearch_list.append(
                    {
                        "label": item[1],
                        "params": {
                            "dt_from": dt_from.isoformat(sep=" "),
                            "dt_to": dt_to.isoformat(sep=" "),
                            "tiid": item[0],
                            "submit": gettext("Search"),
                        },
                    }
                )
            except:  # pylint: disable=locally-disabled,bare-except
                pass

        return quicksearch_list

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        raise NotImplementedError()

    @staticmethod
    def get_query_parameters(form, request_args):
        """
        Get query parameters by comparing contents of processed form data and
        original request arguments. Result of this method can be used for generating
        modified URLs back to current request. One of the use cases is the result
        pager/paginator.
        """
        params = {}
        for arg in request_args:
            if getattr(form, arg, None) and arg in request_args:
                # Handle multivalue request arguments separately
                # Resources:
                #   http://flask.pocoo.org/docs/1.0/api/#flask.Request.args
                #   http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.MultiDict
                try:
                    if form.is_multivalue(arg):
                        params[arg] = request_args.getlist(arg)
                    else:
                        params[arg] = request_args[arg]
                except AttributeError:
                    params[arg] = request_args[arg]
        return params

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    # ---------------------------------------------------------------------------

    @classmethod
    def get_breadcrumbs_menu(cls):
        """
        Get breadcrumbs menu.
        """
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            cls.get_view_endpoint_name(),
            endpoint=f"{cls.module_name}.{cls.get_view_endpoint_name()}",
        )
        return breadcrumbs_menu

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for all items.
        """
        return

    @classmethod
    def get_context_action_menu(cls):
        """*Implementation* of :py:func:`hawat.view.ItemListView.get_context_action_menu`."""
        context_action_menu = hawat.menu.Menu()
        context_action_menu.add_entry(
            "endpoint",
            "show",
            endpoint=f"{cls.module_name}.show",
            hidetitle=True,
        )
        return context_action_menu

    # ---------------------------------------------------------------------------

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,unused-argument
        """
        This hook method will be called before search attempt.
        """

    def do_after_search(self, items):  # pylint: disable=locally-disabled,unused-argument
        """
        This hook method will be called after successfull search.
        """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        form = self.get_search_form(flask.request.args)
        flask.g.search_form = form

        if hawat.const.FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data

                self.mark_time(
                    "preprocess",
                    "begin",
                    tag="search",
                    label=f'Begin preprocessing for "{flask.request.full_path}"',
                    log=True,
                )
                self.do_before_search(form_data)
                self.mark_time(
                    "preprocess",
                    "end",
                    tag="search",
                    label=f'Finished preprocessing for "{flask.request.full_path}"',
                    log=True,
                )

                try:
                    self.mark_time(
                        "search",
                        "begin",
                        tag="search",
                        label=f'Begin searching for "{flask.request.full_path}"',
                        log=True,
                    )
                    items = self.search(form_data)
                    self.mark_time(
                        "search",
                        "end",
                        tag="search",
                        label=f'Finished searching for "{flask.request.full_path}", items found: {len(items)}',
                        log=True,
                    )

                    self.response_context.update(
                        searched=True,
                        items=items,
                        items_count=len(items),
                        form_data=form_data,
                    )

                    # Not all search forms support result paging.
                    if "page" in form_data:
                        self.response_context.update(
                            pager_index_low=((form_data["page"] - 1) * form_data["limit"]) + 1,
                            pager_index_high=((form_data["page"] - 1) * form_data["limit"]) + len(items),
                            pager_index_limit=((form_data["page"] - 1) * form_data["limit"]) + form_data["limit"],
                        )

                    self.mark_time(
                        "postprocess",
                        "begin",
                        tag="search",
                        label=f'Begin postprocessing for "{flask.request.full_path}"',
                        log=True,
                    )
                    self.do_after_search(items)
                    self.mark_time(
                        "postprocess",
                        "end",
                        tag="search",
                        label=f'Finished postprocessing for "{flask.request.full_path}"',
                        log=True,
                    )

                except Exception as err:  # pylint: disable=locally-disabled,broad-except
                    match = re.match('invalid IP4R value: "([^"]+)"', str(err))
                    if match:
                        self.flash(
                            markupsafe.Markup(
                                gettext(
                                    "Invalid address value <strong>%(address)s</strong> in search form.",
                                    address=markupsafe.escape(str(match.group(1))),
                                )
                            ),
                            hawat.const.FLASH_FAILURE,
                        )
                    else:
                        raise

            else:
                self.response_context.update(
                    form_errors=[
                        (field_name, err)
                        for field_name, error_messages in form.errors.items()
                        for err in error_messages
                    ]
                )
                self._flash_pagination_errors(form)

        self.response_context.update(
            query_params=self.get_query_parameters(form, flask.request.args),
            search_widget_item_limit=3,
        )
        self.do_before_response()

        self.mark_time(
            "render",
            "begin",
            tag="render",
            label=f'Started rendering for "{flask.request.full_path}"',
            log=True,
        )
        return self.generate_response()


class CustomSearchView(BaseSearchView):
    """
    Base class for multi search views.
    """

    def custom_search(self, form_args):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    def do_after_search(self, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        This hook method will be called after successfull search.
        """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        form = self.get_search_form(flask.request.args)
        flask.g.search_form = form

        if hawat.const.FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data

                self.mark_time(
                    "preprocess",
                    "begin",
                    tag="search",
                    label=f'Begin preprocessing for "{flask.request.full_path}"',
                    log=True,
                )
                self.do_before_search(form_data)
                self.mark_time(
                    "preprocess",
                    "end",
                    tag="search",
                    label=f'Finished preprocessing for "{flask.request.full_path}"',
                    log=True,
                )

                try:
                    self.mark_time(
                        "search",
                        "begin",
                        tag="search",
                        label=f'Begin custom-searching for "{flask.request.full_path}"',
                        log=True,
                    )
                    self.custom_search(form_data)
                    self.mark_time(
                        "search",
                        "end",
                        tag="search",
                        label=f'Finished custom-searching for "{flask.request.full_path}"',
                        log=True,
                    )

                    self.response_context.update(searched=True, form_data=form_data)

                    self.mark_time(
                        "postprocess",
                        "begin",
                        tag="search",
                        label=f'Begin postprocessing for "{flask.request.full_path}"',
                        log=True,
                    )
                    self.do_after_search()
                    self.mark_time(
                        "postprocess",
                        "end",
                        tag="search",
                        label=f'Finished postprocessing for "{flask.request.full_path}"',
                        log=True,
                    )

                except Exception as err:  # pylint: disable=locally-disabled,broad-except
                    match = re.match('invalid IP4R value: "([^"]+)"', str(err))
                    if match:
                        self.flash(
                            markupsafe.Markup(
                                gettext(
                                    "Invalid address value <strong>%(address)s</strong> in search form.",
                                    address=markupsafe.escape(str(match.group(1))),
                                )
                            ),
                            hawat.const.FLASH_FAILURE,
                        )
                    else:
                        raise

            else:
                self.response_context.update(
                    form_errors=[
                        (field_name, err)
                        for field_name, error_messages in form.errors.items()
                        for err in error_messages
                    ]
                )

        self.response_context.update(
            query_params=self.get_query_parameters(form, flask.request.args),
            search_widget_item_limit=3,
        )
        self.do_before_response()

        self.mark_time(
            "render",
            "begin",
            tag="render",
            label=f'Started rendering for "{flask.request.full_path}"',
            log=True,
        )
        return self.generate_response()


class ItemListView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *list* views. These views provide quick and simple access
    to lists of all objects.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "list"

    @classmethod
    def get_breadcrumbs_menu(cls):
        """
        Get breadcrumbs menu.
        """
        action_menu = hawat.menu.Menu()
        action_menu.add_entry("endpoint", "home", endpoint=flask.current_app.config["ENDPOINT_HOME"])
        action_menu.add_entry(
            "endpoint",
            "list",
            endpoint=f"{cls.module_name}.{cls.get_view_endpoint_name()}",
        )
        return action_menu

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for all listed items.
        """
        return

    @classmethod
    def get_context_action_menu(cls):
        """
        Get context action menu for particular single item.
        """
        return

    @staticmethod
    def get_query_parameters(form, request_args):
        """
        Get query parameters by comparing contents of processed form data and
        original request arguments. Result of this method can be used for generating
        modified URLs back to current request. One of the use cases is the result
        pager/paginator.
        """
        params = {}
        for arg in request_args:
            if form and getattr(form, arg, None) and arg in request_args:
                # Handle multivalue request arguments separately
                # Resources:
                #   http://flask.pocoo.org/docs/1.0/api/#flask.Request.args
                #   http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.MultiDict
                try:
                    if form.is_multivalue(arg):
                        params[arg] = request_args.getlist(arg)
                    else:
                        params[arg] = request_args[arg]
                except AttributeError:
                    params[arg] = request_args[arg]
        return params

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        return

    def search(self, form_args):
        """
        Perform actual search with given form arguments.
        """
        raise NotImplementedError()

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        List of all items will be retrieved from database and injected into template
        to be displayed to the user.
        """
        form = self.get_search_form(flask.request.args)
        flask.g.search_form = form

        if form:
            form_data = form.data
            items = []
            pager_index_low = pager_index_high = pager_index_limit = 0
            if form.validate():
                form_data = form.data
                items = self.search(form_data)

                self.response_context.update(
                    form_data=form_data,
                    searched=True,
                    items=items,
                    items_count=len(items),
                )

                if "page" in form_data and "limit" in form_data:
                    pager_index_low = ((form_data["page"] - 1) * form_data["limit"]) + 1
                    pager_index_high = ((form_data["page"] - 1) * form_data["limit"]) + len(items)
                    pager_index_limit = ((form_data["page"] - 1) * form_data["limit"]) + form_data["limit"]

            else:
                self._flash_pagination_errors(form)

            self.response_context.update(
                pager_index_low=pager_index_low,
                pager_index_high=pager_index_high,
                pager_index_limit=pager_index_limit,
            )
        else:
            items = self.search({})
            self.response_context.update(items=items)

        self.response_context.update(
            query_params=self.get_query_parameters(form, flask.request.args),
            search_widget_item_limit=3,
            form=form,
        )

        self.do_before_response()
        return self.generate_response()


class ItemShowView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *show* views. These views expect unique item identifier
    as parameter and are supposed to display specific information about single
    item.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "show"

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return "action-show"

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Show")

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_url`."""
        if "item" not in kwargs or not kwargs["item"]:
            raise ValueError(f"Missing item parameter for show URL view '{cls.get_view_endpoint()}'")
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"].get_id())

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Show")

    @classmethod
    def authorize_item_action(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @classmethod
    def get_action_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        """
        Get action menu for particular item.
        """
        return

    @classmethod
    def get_breadcrumbs_menu(cls):  # pylint: disable=locally-disabled,unused-argument
        """
        Get breadcrumbs menu.
        """
        action_menu = hawat.menu.Menu()
        action_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        action_menu.add_entry(
            "endpoint",
            "list",
            endpoint=f"{cls.module_name}.list",
            paramlist=[],
        )
        action_menu.add_entry(
            "endpoint",
            "show",
            endpoint=f"{cls.module_name}.{cls.get_view_endpoint_name()}",
        )
        return action_menu

    def fetch(self, item_id):
        """
        Fetch item with given ID.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        self.response_context.update(item_id=item_id, item=item, search_widget_item_limit=100)

        self.do_before_response()
        return self.generate_response()


class ItemActionView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item action views. These views perform various actions
    (create/update/delete) with given item class.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return "action-{}".format(cls.get_view_name().replace("_", "-"))

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint(), item_id=kwargs["item"].get_id())

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`hawat.view.RenderableView.get_view_template`."""
        return "form_{}.html".format(cls.get_view_name().replace("-", "_"))

    @staticmethod
    def get_message_success(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *success*.
        The text may contain HTML characters and will be passed to :py:class:`markupsafe.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_failure(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *failure*.
        The text may contain HTML characters and will be passed to :py:class:`markupsafe.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    def get_url_next(self):  # pylint: disable=locally-disabled
        """
        *Hook method*. Must return URL for redirection after action *success*. In
        most cases there should be call for :py:func:`flask.url_for` function
        somewhere in this method.
        """
        return

    def do_before_action(self, item):  # pylint: disable=locally-disabled,unused-argument
        """
        *Hook method*. Will be called before any action handling tasks.
        """

    def do_after_action(self, item):  # pylint: disable=locally-disabled,unused-argument
        """
        *Hook method*. Will be called after successfull action handling tasks.
        """

    @classmethod
    def authorize_item_action(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        raise NotImplementedError()

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    @property
    def dbchlogmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    def fetch(self, item_id):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    def changelog_log(self, item, json_state_before="", json_state_after=""):
        """
        Log item action into changelog. One of the method arguments is permitted
        to be left out. This enables logging create and delete actions.

        :param hawat.db.MODEL item: Item that is being changed.
        :param str json_state_before: JSON representation of item state before action.
        :param str json_state_after: JSON representation of item state after action.
        """
        if not json_state_before and not json_state_after:
            raise ValueError("Invalid use of changelog_log() method, both of the item states are null.")

        # 'Author' may be an instance of 'AnonymousUserMixin' for actions performed by
        # anonymous users. In that case store 'Null' into database.
        author = flask_login.current_user._get_current_object()  # pylint: disable=locally-disabled,protected-access
        if not isinstance(author, self.get_model(hawat.const.MODEL_USER)):
            author = None

        # Do not generate empty changelog.
        chlog = None
        if jsondiff(json_state_before, json_state_after):
            chlog = self.dbchlogmodel(
                author=author,
                model=item.__class__.__name__,
                model_id=item.id,
                endpoint=self.get_view_endpoint(),
                module=self.module_name,
                operation=self.get_view_name(),
                before=json_state_before,
                after=json_state_after,
            )
            chlog.calculate_diff()
            if chlog.diff:
                self.dbsession.add(chlog)
                self.dbsession.commit()

        return chlog

    def get_affected_items(self, item, form):
        """
        Return dict of hawat.db.MODEL items affected by the change of the item
        as keys and their JSON representation before change as value.
        (e.g. dict of groups which lost a member after a user item was deleted)

        :param hawat.db.MODEL item: Item that is being changed.
        :param flask_wtf.FlaskForm form: Form representing the change.
        """
        changed = set()
        for attribute in [
            "memberships",
            "memberships_wanted",
            "managements",
            "members",
            "members_wanted",
            "managers",
        ]:
            if hasattr(item, attribute):
                changed.update(getattr(item, attribute))
            if hasattr(form, attribute):
                changed.update(getattr(form, attribute).data)
        return {obj: obj.to_json() for obj in changed}

    def handle_error(self, **kwargs):
        """
        Handle and log the error, rollback all database changes
        and show the failure message to user.
        """
        self.dbsession.rollback()
        self.flash(
            markupsafe.Markup(self.get_message_failure(**kwargs)),
            hawat.const.FLASH_FAILURE,
        )
        flask.current_app.log_exception_with_label(
            traceback.TracebackException(*sys.exc_info()),
            self.get_message_failure(**kwargs),
        )
        return self.redirect(default_url=self.get_url_next())

    def inform_about_filter_change(self, _filter, chlog):
        """
        Send information about the change of the filter to the group managers and maintainers.
        Use user`s locale for email content translations.
        """

        def _send_email(to, recipient_type=None, locale=None):
            self._send_email(
                to=to,
                subject=gettext(
                    "[%(app_name)s] Filter change - %(filter_name)s",
                    app_name=flask.current_app.config["APPLICATION_NAME"],
                    filter_name=_filter.name,
                ),
                template_path="filters/email_filter_change.txt",
                locale=locale,
                recipient=recipient_type,
                _filter=_filter,
                diff=chlog.diff,
                chlog=chlog,
                filter_was_deleted=chlog.endpoint == "filters.delete",
                author=chlog.author.fullname if chlog.author else None,
            )

        informed_users = {chlog.author}

        def _inform_users(users, recipient_type):
            for user in users:
                if user in informed_users:
                    continue
                _send_email(to=[user.email], recipient_type=recipient_type, locale=user.locale)
                informed_users.add(user)

        try:
            maintainer_emails_override = flask.current_app.config["EMAIL_MAINTAINERS"]
            if maintainer_emails_override:
                flask.current_app.logger.info(
                    f"Attempting to send information about the change of filter '{_filter.name}' to overriden maintainers '{maintainer_emails_override}'."
                )
                _send_email(maintainer_emails_override, recipient_type="maintainer")
            else:
                maintainers = self.dbsession.query(UserModel).filter(UserModel.roles.contains(["maintainer"])).all()

                # Inform maintainers.
                flask.current_app.logger.info(
                    f"Attempting to send information about the change of filter '{_filter.name}' to maintainers '{maintainers}'."
                )
                _inform_users(users=maintainers, recipient_type="maintainer")
        except ConnectionRefusedError:
            # Mail service is probably not configured.
            self.logger.error("Unable to send infomail about filter change to maintainers.")

        # Inform group managers (for non-global filters only).
        if _filter.group is not None:
            flask.current_app.logger.info(
                f"Attempting to send information about the change of filter '{_filter.name}' to managers of group '{_filter.group.name}'."
            )
            try:
                _inform_users(users=_filter.group.managers, recipient_type="manager")
            except ConnectionRefusedError:
                # Mail service is probably not configured.
                self.logger.error("Unable to send infomail about filter change to group managers.")


class ItemCreateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *create* action views. These views create new items in
    database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "create"

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.app.hawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return f"{cls.module_name}/creatupdate.html"
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Create")

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint())

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Create")

    def get_item(self):
        """
        *Hook method*. Must return instance for given item class.
        """
        return self.dbmodel()

    @staticmethod
    def get_item_form(item):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_duplicate(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *failure*.
        The text may contain HTML characters and will be passed to :py:class:`markupsafe.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        return gettext(
            'Item "%(item)s" already exists',
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "list",
            endpoint=f"{cls.module_name}.list",
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "create",
            endpoint=f"{cls.module_name}.{cls.get_view_endpoint_name()}",
        )
        return breadcrumbs_menu

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        if not self.authorize_item_action():
            self.abort(403)

        item = self.get_item()
        self.response_context.update(item=item)

        form = self.get_item_form(item)
        self.response_context.update(form=form)

        if form.validate_on_submit():
            affected_items = self.get_affected_items(item, form)

            form_data = form.data
            self.response_context.update(form_data=form_data)

            form.populate_obj(item)
            try:
                self.do_before_action(item)
            except Exception:
                return self.handle_error(item=item)

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.add(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item creation into changelog.
                    chlog = self.changelog_log(item, "", item.to_json())

                    if isinstance(item, FilterModel) and chlog:
                        self.inform_about_filter_change(item, chlog)

                    # Log changes of all affected items into changelog.
                    for affected_item, json_before in affected_items.items():
                        self.changelog_log(affected_item, json_before, affected_item.to_json())

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except sqlalchemy.exc.IntegrityError:
                    self.dbsession.rollback()
                    self.flash(
                        markupsafe.Markup(self.get_message_duplicate(item=item)),
                        hawat.const.FLASH_FAILURE,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(item=item)

        self.response_context.update(
            action_name=gettext("Create"),
            form_url=flask.url_for(self.get_view_endpoint()),
            item_action=hawat.const.ACTION_ITEM_CREATE,
            item_type=self.dbmodel.__name__.lower(),
        )

        self.do_before_response()
        return self.generate_response()


class ItemCreateForView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *createfor* action views. These views differ a little bit
    from *create* action views. They are used to create new items within database,
    but only for particular defined parent item. One example use case is creating
    network records for particular abuse group.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "createfor"

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return f"module-{cls.module_name}"

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint(), parent_id=kwargs["parent"].id)

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.app.hawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return f"{cls.module_name}/creatupdate.html"
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @property
    def dbmodel_par(self):
        """
        *Hook property*. This property must be implemented in each subclass to
        return reference to appropriate model class for parent objects and that
        is based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def dbquery_par(self):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel_par`` property.
        """
        return self.dbsession.query(self.dbmodel_par)

    def get_item(self):
        """
        *Hook method*. Must return instance for given item class.
        """
        return self.dbmodel()

    @staticmethod
    def get_item_form(item):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    @staticmethod
    def add_parent_to_item(item, parent):
        """
        *Hook method*. Use given parent object for given item object. The actual
        operation to realize this relationship is highly dependent on current
        circumstance. It is up to the developer to perform correct set of actions
        to implement parent - child relationship for particular object types.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_duplicate(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *failure*.
        The text may contain HTML characters and will be passed to :py:class:`markupsafe.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        return gettext(
            'Item "%(item)s" already exists',
            item=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "show_par",
            endpoint=f"{cls.module_name_par}.show",
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "createfor",
            endpoint=f"{cls.module_name}.createfor",
        )
        return breadcrumbs_menu

    def dispatch_request(self, parent_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        parent = self.dbquery_par.filter(self.dbmodel_par.id == parent_id).one_or_none()
        if not parent:
            self.abort(404)

        if not self.authorize_item_action(item=parent):
            self.abort(403)

        self.response_context.update(parent_id=parent_id, parent=parent)

        item = self.get_item()
        form = self.get_item_form(item)

        if form.validate_on_submit():
            affected_items = self.get_affected_items(item, form)

            form_data = form.data
            self.response_context.update(form_data=form_data)

            form.populate_obj(item)
            self.add_parent_to_item(item, parent)
            try:
                self.do_before_action(item)
            except Exception:
                return self.handle_error(parent=parent)

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.add(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item creation into changelog.
                    chlog = self.changelog_log(item, "", item.to_json())

                    # Log changes of all affected items into changelog.
                    for affected_item, json_before in affected_items.items():
                        self.changelog_log(affected_item, json_before, affected_item.to_json())

                    if isinstance(item, FilterModel) and chlog:
                        self.inform_about_filter_change(item, chlog)

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item, parent=parent)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except sqlalchemy.exc.IntegrityError:
                    self.dbsession.rollback()
                    self.flash(
                        markupsafe.Markup(self.get_message_duplicate(item=item)),
                        hawat.const.FLASH_FAILURE,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(parent=parent)

        self.response_context.update(
            action_name=gettext("Create"),
            form_url=flask.url_for(self.get_view_endpoint(), parent_id=parent_id),
            form=form,
            item_action=hawat.const.ACTION_ITEM_CREATEFOR,
            item_type=self.dbmodel.__name__.lower(),
            item=item,
            parent_type=self.dbmodel_par.__name__.lower(),
            parent=parent,
        )

        self.do_before_response()
        return self.generate_response()


class BaseRegisterView(ItemCreateView):  # pylint: disable=locally-disabled,abstract-method
    """
    View responsible for registering new user account into application.
    """

    methods = ["GET", "POST"]

    is_sign_up = True

    @classmethod
    def get_view_name(cls):
        return hawat.const.ACTION_USER_REGISTER

    @classmethod
    def get_view_icon(cls):
        return hawat.const.ACTION_USER_REGISTER

    @classmethod
    def get_menu_title(cls, **kwargs):
        return gettext("Register")

    @classmethod
    def get_view_title(cls, **kwargs):
        return gettext("User account registration")

    @classmethod
    def get_view_template(cls):
        return f"{cls.module_name}/registration.html"

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "User account <strong>%(login)s (%(name)s)</strong> was successfully registered.",
            login=kwargs["item"].login,
            name=kwargs["item"].fullname,
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext("Unable to register new user account.")

    @staticmethod
    def get_message_duplicate(**kwargs):
        return gettext(
            'Please use different login, the "%(item)s" is already taken.',
            item=str(kwargs["item"]),
        )

    def inform_maintainers(self, account: UserModel, subject: str, form_data: Any) -> None:
        """
        Send information about new account registration to maintainers.
        Use default locale for email content translations.
        """
        maintainer_emails_override = flask.current_app.config["EMAIL_MAINTAINERS"]
        if maintainer_emails_override:
            to = maintainer_emails_override
        else:
            maintainers = self.dbsession.query(UserModel).filter(UserModel.roles.contains(["maintainer"])).all()
            to = [maintainer.email for maintainer in maintainers]
        flask.current_app.logger.info(
            "Attempting to send information about registration of new account '{}' to maintainers @: '{}'.".format(
                account.login, ", ".join(to)
            )
        )
        self._send_email(
            to=to,
            subject=subject,
            template_path="registration/email_maintainers.txt",
            account=account,
            justification=form_data["justification"],
        )

    def inform_managers(self, account: UserModel, subject: str, form_data: Any) -> None:
        """
        Send information about new account registration to the group managers.
        Use manager`s locale for email content translations.
        """
        for group in account.memberships_wanted:
            flask.current_app.logger.info(
                f"Attempting to send information about registration of new account '{account.login}' to managers of group '{group.name}'."
            )

            if not group.managers:
                flask.current_app.logger.info(
                    f"Unable to send information about registration of new account '{account.login}' to managers of group '{group.name}': there are no managers configured."
                )
                return

            for manager in group.managers:
                self._send_email(
                    to=[manager.email],
                    subject=subject,
                    template_path="registration/email_managers.txt",
                    locale=manager.locale,
                    account=account,
                    group=group,
                    justification=form_data["justification"],
                )

    def inform_user(self, account: UserModel, subject: str, form_data: Any) -> None:
        """
        Send information about new account registration to the user.
        Use user`s preferred locale for email content translations.
        """
        self._send_email(
            to=[account.email],
            subject=subject,
            template_path="registration/email_user.txt",
            locale=account.locale,
            account=account,
            justification=form_data["justification"],
        )

    def do_before_action(self, item):  # pylint: disable=locally-disabled,unused-argument
        item.roles = [hawat.const.ROLE_USER]
        item.enabled = False

    def do_after_action(self, item):  # pylint: disable=locally-disabled,unused-argument
        subject = gettext(
            "[%(app_name)s] Account registration - %(item_id)s",
            app_name=flask.current_app.config["APPLICATION_NAME"],
            item_id=item.login,
        )
        form_data = self.response_context["form_data"]
        self.inform_maintainers(item, subject, form_data)
        self.inform_managers(item, subject, form_data)
        self.inform_user(item, subject, form_data)


class ItemUpdateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *update* action views. These views update existing items
    in database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "update"

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.app.hawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return f"{cls.module_name}/creatupdate.html"
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Update")

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Update")

    @staticmethod
    def get_item_form(item):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    @classmethod
    def get_breadcrumbs_menu(cls):
        breadcrumbs_menu = hawat.menu.Menu()
        breadcrumbs_menu.add_entry(
            "endpoint",
            "home",
            endpoint=flask.current_app.config["ENDPOINT_HOME"],
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "list",
            endpoint=f"{cls.module_name}.list",
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "show",
            endpoint=f"{cls.module_name}.show",
        )
        breadcrumbs_menu.add_entry(
            "endpoint",
            "update",
            endpoint=f"{cls.module_name}.{cls.get_view_endpoint_name()}",
        )
        return breadcrumbs_menu

    def get_affected_items(self, item, form):
        """
        Return dict of hawat.db.MODEL items affected by the update of the item
        as keys and their JSON representation before update as value.
        (e.g. dict of groups which lost a member after a user item was updated)
        Overrides get_affected_items(self, item, form) in ItemActionView.

        :param hawat.db.MODEL item: Item that is being changed.
        :param flask_wtf.FlaskForm form: Form representing the change.
        """
        changed = set()
        for attribute in [
            "memberships",
            "memberships_wanted",
            "managements",
            "members",
            "members_wanted",
            "managers",
        ]:
            if hasattr(item, attribute) and hasattr(form, attribute):
                changed.update(set(getattr(item, attribute)).symmetric_difference(set(getattr(form, attribute).data)))
        return {obj: obj.to_json() for obj in changed}

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and update the
        instance of appropriate item from form data and finally store the item
        back into the database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        self.dbsession.add(item)

        form = self.get_item_form(item)

        item_json_before = item.to_json()

        if form.validate_on_submit():
            affected_items = self.get_affected_items(item, form)

            form_data = form.data
            self.response_context.update(form_data=form_data)

            form.populate_obj(item)
            try:
                self.do_before_action(item)
            except Exception:
                return self.handle_error(item=item)

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext("No changes detected, no update needed."),
                            hawat.const.FLASH_INFO,
                        )
                        return self.redirect(default_url=self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item update into changelog.
                    chlog = self.changelog_log(item, item_json_before, item.to_json())

                    if isinstance(item, FilterModel) and chlog:
                        self.inform_about_filter_change(item, chlog)

                    # Log changes of all affected items into changelog.
                    for affected_item, json_before in affected_items.items():
                        self.changelog_log(affected_item, json_before, affected_item.to_json())

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(item=item)

        self.response_context.update(
            action_name=gettext("Update"),
            form_url=flask.url_for(self.get_view_endpoint(), item_id=item_id),
            form=form,
            item_action=hawat.const.ACTION_ITEM_UPDATE,
            item_type=self.dbmodel.__name__.lower(),
            item_id=item_id,
            item=item,
        )

        self.do_before_response()
        return self.generate_response()


class ItemDeleteView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *delete* action views. These views delete existing items
    from database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "delete"

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Delete")

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Delete")

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and delete the
        instance of appropriate item from database in case user agreed to the
        item removal action.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        form = ItemActionConfirmForm()

        item_json_before = item.to_json()

        if form.validate_on_submit():
            affected_items = self.get_affected_items(item, form)

            form_data = form.data
            self.response_context.update(form_data=form_data)

            try:
                self.do_before_action(item)
            except Exception:
                return self.handle_error(item=item)

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.delete(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item deletion into changelog.
                    chlog = self.changelog_log(item, item_json_before, "")

                    if isinstance(item, FilterModel) and chlog:
                        self.inform_about_filter_change(item, chlog)

                    # Log changes of all affected items into changelog.
                    for affected_item, json_before in affected_items.items():
                        self.changelog_log(affected_item, json_before, affected_item.to_json())

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(
                        default_url=self.get_url_next(),
                        exclude_url=flask.url_for("{}.{}".format(self.module_name, "show"), item_id=item.id),
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(item=item)

        self.response_context.update(
            confirm_form=form,
            confirm_url=flask.url_for(self.get_view_endpoint(), item_id=item_id),
            item_name=str(item),
            item_id=item_id,
            item=item,
            referrer=self.get_url_cancel(),
        )

        self.do_before_response()
        return self.generate_response()


class ItemChangeView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for single item change views, that are doing some simple modification
    of item attribute, like enable/disable item, etc.
    """

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        return True

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Hook method*: Change given item in any desired way.

        :param item: Item to be changed/modified.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form, then perform
        arbitrary mangling action with the item and submit the changes to the
        database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item=item):
            self.abort(403)

        if not self.validate_item_change(item=item):
            self.abort(400)

        form = ItemActionConfirmForm()

        item_json_before = item.to_json()

        if form.validate_on_submit():
            form_data = form.data
            self.response_context.update(form_data=form_data)

            try:
                self.do_before_action(item)
            except Exception:
                return self.handle_error(item=item)

            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    self.change_item(item=item)
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext("No changes detected, no update needed."),
                            hawat.const.FLASH_INFO,
                        )
                        return self.redirect(default_url=self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log the item change into changelog.
                    chlog = self.changelog_log(item, item_json_before, item.to_json())

                    if isinstance(item, FilterModel) and chlog:
                        self.inform_about_filter_change(item, chlog)

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(item=item)

        self.response_context.update(
            confirm_form=form,
            confirm_url=flask.url_for(self.get_view_endpoint(), item_id=item_id),
            item_name=str(item),
            item_id=item_id,
            item=item,
            referrer=self.get_url_cancel(),
        )

        self.do_before_response()
        return self.generate_response()


class ItemDisableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item disabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "disable"

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Disable")

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Disable")

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """*Implementation* of :py:func:`hawat.view.ItemChangeView.validate_item_change`."""
        # Reject item change in case given item is already disabled.
        return kwargs["item"].enabled

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Implementation* of :py:func:`hawat.view.ItemChangeView.change_item`.
        """
        kwargs["item"].enabled = False


class ItemEnableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item enabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_name`."""
        return "enable"

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_title`."""
        return gettext("Enable")

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_menu_title`."""
        return gettext("Enable")

    @classmethod
    def validate_item_change(cls, **kwargs):  # pylint: disable=locally-disabled,unused-argument
        """*Implementation* of :py:func:`hawat.view.ItemChangeView.validate_item_change`."""
        # Reject item change in case given item is already enabled.
        return not kwargs["item"].enabled

    @classmethod
    def change_item(cls, **kwargs):
        """
        *Implementation* of :py:func:`hawat.view.ItemChangeView.change_item`.
        """
        kwargs["item"].enabled = True


class ItemObjectRelationView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item object relation action views.
    """

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_icon`."""
        return f"module-{cls.module_name}"

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`hawat.app.hawatBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return f"{cls.module_name}/{cls.get_view_endpoint_name()}.html"
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`hawat.view.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id=kwargs["item"].get_id(),
            other_id=kwargs["other"].get_id(),
        )

    @property
    def dbmodel_other(self):
        """
        *Hook property*. This property must be implemented in each subclass to
        return reference to appropriate model class for other objects and that
        is based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def dbquery_other(self):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel_other`` property.
        """
        return self.dbsession.query(self.dbmodel_other)

    def dispatch_request(self, item_id, other_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)
        other = self.dbquery_other.filter(self.dbmodel_other.id == other_id).first()
        if not other:
            self.abort(404)

        if not self.authorize_item_action(item=item, other=other):
            self.abort(403)

        if not self.validate_item_change(item=item, other=other):
            self.abort(400)
        form = ItemActionConfirmForm()

        item_json_before = item.to_json()
        other_json_before = other.to_json()

        if form.validate_on_submit():
            form_data = form.data
            self.response_context.update(form_data=form_data)

            self.do_before_action(item)
            if form_data[hawat.const.FORM_ACTION_SUBMIT]:
                try:
                    self.change_item(item=item, other=other)
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext("No changes detected, no update needed."),
                            hawat.const.FLASH_INFO,
                        )
                        return self.redirect(default_url=self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    # Log changes of 'item' and 'other' into changelog.
                    self.changelog_log(item, item_json_before, item.to_json())
                    self.changelog_log(other, other_json_before, other.to_json())

                    self.flash(
                        markupsafe.Markup(self.get_message_success(item=item, other=other)),
                        hawat.const.FLASH_SUCCESS,
                    )
                    return self.redirect(default_url=self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    return self.handle_error(item=item, other=other)

        self.response_context.update(
            confirm_form=form,
            confirm_url=flask.url_for(
                f"{self.module_name}.{self.get_view_name()}",
                item_id=item_id,
                other_id=other_id,
            ),
            item_name=str(item),
            item_id=item_id,
            item=item,
            other_name=str(other),
            other_id=other_id,
            other=other,
            referrer=self.get_url_cancel(),
        )

        self.do_before_response()
        return self.generate_response()
