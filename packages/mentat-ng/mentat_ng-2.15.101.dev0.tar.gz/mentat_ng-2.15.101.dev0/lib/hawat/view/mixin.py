#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains usefull view mixin classes for *Hawat* application views.
"""

import contextlib
import datetime
from collections.abc import Callable
from typing import NotRequired, TypedDict

import flask
import flask.app
import flask.views
import sqlalchemy
from flask_babel import gettext

import hawat.const
import hawat.db
import hawat.errors
import hawat.menu
from hawat.forms import get_redirect_target


class SnippetDictType(TypedDict):
    """
    Type definition for dictionary representing a snippet.
    """

    name: str
    file: NotRequired[str]
    condition: NotRequired[Callable[[dict], bool]]


class HawatUtils:
    """
    Small utility method class to enable use of those methods both in the view
    classes and in the Jinja2 templates.
    """

    @staticmethod
    def get_datetime_window(tiid, wtype, moment=None):
        """
        Get timestamp of given type ('current', 'previous', 'next') for given time
        window and optional time moment.
        """
        try:
            if not moment:
                moment = datetime.datetime.utcnow()
            return hawat.const.TIME_WINDOWS[tiid][wtype](moment)
        except:  # pylint: disable=locally-disabled,bare-except
            return None


class HTMLMixin:
    """
    Mixin class enabling rendering responses as HTML. Use it in your custom view
    classess based on :py:class:`hawat.view.RenderableView` to provide the
    ability to render Jinja2 template files into HTML documents.
    """

    @staticmethod
    def abort(status_code, message=None):  # pylint: disable=locally-disabled,unused-argument
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as HTML error document.
        """
        flask.abort(status_code, message)

    def flash(self, message, level="info"):
        """
        Display a one time message to the user. This implementation uses the
        :py:func:`flask.flash` method.

        :param str message: Message text.
        :param str level: Severity level of the flash message.
        """
        flask.flash(message, level)

    def redirect(self, target_url=None, default_url=None, exclude_url=None):
        """
        Redirect user to different page. This implementation uses the
        :py:func:`flask.redirect` method to return valid HTTP redirection response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        return flask.redirect(get_redirect_target(target_url, default_url, exclude_url))

    def generate_response(self, view_template=None):
        """
        Generate the response appropriate for this view class, in this case HTML
        page.

        :param str view_template: Override internally preconfigured page template.
        """
        return flask.render_template(view_template or self.get_view_template(), **self.response_context)


class AJAXMixin:
    """
    Mixin class enabling rendering responses as JSON documents. Use it in your
    custom view classess based on based on :py:class:`hawat.view.RenderableView`
    to provide the ability to generate JSON responses.
    """

    KW_RESP_VIEW_TITLE = "view_title"
    KW_RESP_VIEW_ICON = "view_icon"
    KW_RESP_FLASH_MESSAGES = "flash_messages"

    ALWAYS_JSON = True

    @staticmethod
    def abort(status_code, message=None):
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as JSON document.
        """
        flask.abort(hawat.errors.api_error_response(status_code, message))

    def flash(self, message, level="info"):
        """
        Display a one time message to the user. This implementation uses the
        ``flash_messages`` subkey in returned JSON document to store the messages.

        :param str message: Message text.
        :param str level: Severity level of the flash message.
        """
        self.response_context.setdefault(self.KW_RESP_FLASH_MESSAGES, {}).setdefault(level, []).append(message)

    def redirect(self, target_url=None, default_url=None, exclude_url=None):
        """
        Redirect user to different page. This implementation stores the redirection
        target to the JSON response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        self.response_context.update(redirect=get_redirect_target(target_url, default_url, exclude_url))
        self.process_response_context()
        return flask.jsonify(self.response_context)

    def get_blocked_response_context_keys(self):
        """
        Returns a list of reponse context keys that will be removed in the
        :py:func:`hawat.view.mixin.AJAXMixin.process_response_context`

        :return: a list of response context keys to be removed
        """
        return ["search_form", "item_form"]

    def process_response_context(self):
        """
        Perform additional mangling with the response context before generating
        the response. This method can be useful to delete some context keys, that
        should not leave the server.

        :return: Possibly updated response context.
        :rtype: dict
        """
        self.response_context[self.KW_RESP_VIEW_TITLE] = self.get_view_title()
        self.response_context[self.KW_RESP_VIEW_ICON] = self.get_view_icon()

        flashed_messages = flask.get_flashed_messages(with_categories=True)
        if flashed_messages:
            for category, message in flashed_messages:
                self.response_context.setdefault(self.KW_RESP_FLASH_MESSAGES, {}).setdefault(category, []).append(
                    message
                )

        # Prevent certain response context keys to appear in final response.
        for key in self.get_blocked_response_context_keys():
            with contextlib.suppress(KeyError):
                del self.response_context[key]

        return self.response_context

    def generate_response(self, view_template=None):  # pylint: disable=locally-disabled,unused-argument
        """
        Generate the response appropriate for this view class, in this case JSON
        document.

        :param str view_template: Override internally preconfigured page template.
        """
        self.process_response_context()
        return flask.jsonify(self.response_context)


class SnippetMixin(AJAXMixin):
    """
    Mixin class enabling rendering responses as JSON documents. Use it in your
    custom view classes based on :py:class:`hawat.view.RenderableView`
    to provide the ability to generate JSON responses.
    """

    KW_RESP_SNIPPETS = "snippets"
    KW_RESP_RENDER = "_render"

    renders: list[str] = []
    snippets: list[SnippetDictType] = []

    def _render_snippet(self, snippet, snippet_file=None):
        if "condition" in snippet and not snippet["condition"](self.response_context):
            return

        if not snippet_file:
            snippet_file = "{mod}/spt_{rdr}_{spt}.html".format(
                mod=self.module_name,
                rdr=self.response_context[self.KW_RESP_RENDER],
                spt=snippet["name"],
            )

        self.response_context.setdefault(self.KW_RESP_SNIPPETS, {})[snippet["name"]] = flask.render_template(
            snippet_file, **self.response_context
        )

    def flash(self, message, level="info"):
        """
        Display a one time message to the user. This implementation uses the
        ``flash_messages`` subkey in returned JSON document to store the messages.

        :param str message: Message text.
        :param str level: Severity level of the flash message.
        """
        self.response_context.setdefault(self.KW_RESP_SNIPPETS, {}).setdefault(
            self.KW_RESP_FLASH_MESSAGES, {}
        ).setdefault(level, []).append(flask.render_template("spt_flashmessage.html", level=level, message=message))

    def process_response_context(self):
        """
        Reimplementation of :py:func:`hawat.view.mixin.AJAXMixin.process_response_context`.
        """
        self.response_context[self.KW_RESP_VIEW_TITLE] = self.get_view_title()
        self.response_context[self.KW_RESP_VIEW_ICON] = self.get_view_icon()
        self.response_context[self.KW_RESP_RENDER] = (
            flask.request.args.get("render", self.renders[0]) or self.renders[0]
        )
        if self.response_context[self.KW_RESP_RENDER] not in self.renders:
            self.abort(
                400,
                gettext(
                    "Invalid value %(val)s for snippet rendering parameter.",
                    val=self.response_context[self.KW_RESP_RENDER],
                ),
            )

        flashed_messages = flask.get_flashed_messages(with_categories=True)
        if flashed_messages:
            for category, message in flashed_messages:
                self.response_context.setdefault(self.KW_RESP_SNIPPETS, {}).setdefault(
                    self.KW_RESP_FLASH_MESSAGES, {}
                ).setdefault(category, []).append(
                    flask.render_template("spt_flashmessage.html", level=category, message=message)
                )

        for snippet in self.snippets:
            self._render_snippet(snippet)

        # Prevent certain response context keys to appear in final response.
        for key in self.get_blocked_response_context_keys():
            with contextlib.suppress(KeyError):
                del self.response_context[key]

        return self.response_context


class SQLAlchemyMixin:
    """
    Mixin class providing generic interface for interacting with SQL database
    backend through SQLAlchemy library.
    """

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to return reference to
        appropriate model class based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def search_by(self):
        """
        Return model`s attribute (column) according to which to search for a single item.
        """
        return self.dbmodel.id

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        return hawat.db.db_get().session

    def dbquery(self, dbmodel=None):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel`` property.
        """
        return self.dbsession.query(dbmodel or self.dbmodel)

    def dbcolumn_min(self, dbcolumn):
        """
        Find and return the minimal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.min(dbcolumn)).one_or_none()  # pylint: disable=locally-disabled,not-callable
        if result:
            return result[0]
        return None

    def dbcolumn_max(self, dbcolumn):
        """
        Find and return the maximal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.max(dbcolumn)).one_or_none()  # pylint: disable=locally-disabled,not-callable
        if result:
            return result[0]
        return None

    @staticmethod
    def build_query(query, model, form_args):  # pylint: disable=locally-disabled,unused-argument
        """
        *Hook method*. Modify given query according to the given arguments.
        """
        return query

    def fetch(self, item_id):
        """
        Fetch item with given primary identifier from the database.
        """
        return self.dbquery().filter(self.search_by == item_id).first()

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        query = self.build_query(self.dbquery(), self.dbmodel, form_args)

        # Adjust the query according to the paging parameters.
        if form_args.get("limit"):
            query = query.limit(int(form_args["limit"]))
            if "page" in form_args and form_args["page"] and int(form_args["page"]) > 1:
                query = query.offset((int(form_args["page"]) - 1) * int(form_args["limit"]))

        return query.all()
