#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This pluggable module provides API key based authentication service. When this
module is enabled, users may generate and use API keys to authenticate themselves
when accessing various API application endpoints.

Currently, the API key may be provided via one of the following methods:

* The ``Authorization`` HTTP header.

  You may provide your API key by adding ``Authorization`` HTTP header to your
  requests. Following forms are accepted::

    Authorization: abcd1234
    Authorization: key abcd1234
    Authorization: token abcd1234

* The ``api_key`` or ``api_token`` parameter of the HTTP ``POST`` request.

  You may provide your API key as additional HTTP parameter ``api_key`` or
  ``api_token`` of your ``POST`` request to particular application endpoint.
  Using ``GET`` requests is forbidden due to the fact that request URLs are getting
  logged on various places and your keys could thus be easily compromised.


Provided endpoints
--------------------------------------------------------------------------------

``/auth_api/<user_id>/key-generate``
    Page enabling generation of new API key.

    * *Authentication:* login required
    * *Authorization:* ``admin``
    * *Methods:* ``GET``, ``POST``

``/auth_api/<user_id>/key-delete``
    Page enabling deletion of existing API key.

    * *Authentication:* login required
    * *Authorization:* ``admin``
    * *Methods:* ``GET``, ``POST``
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import flask
import flask_principal
import itsdangerous
import markupsafe
from flask_babel import gettext, lazy_gettext

import hawat.acl
import hawat.const
import hawat.db
import hawat.forms
from hawat.base import HawatBlueprint
from hawat.view import ItemChangeView
from hawat.view.mixin import HTMLMixin, SQLAlchemyMixin

BLUEPRINT_NAME = "auth_api"
"""Name of the blueprint as module global constant."""


class GenerateKeyView(HTMLMixin, SQLAlchemyMixin, ItemChangeView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for generating API keys for user accounts.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "key-generate"

    @classmethod
    def get_view_icon(cls):
        return "action-genkey"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Generate API key")

    @classmethod
    def get_view_template(cls):
        return "auth_api/key-generate.html"

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_USER)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        # Each user must be able to manage his/her API keys.
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_me.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "API key for user account <strong>%(item_id)s</strong> was successfully generated.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to generate API key for user account <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def change_item(cls, **kwargs):
        serializer = itsdangerous.URLSafeTimedSerializer(
            flask.current_app.config["SECRET_KEY"],
            salt="apikey-user",
        )
        kwargs["item"].apikey = serializer.dumps(kwargs["item"].id)


class DeleteKeyView(HTMLMixin, SQLAlchemyMixin, ItemChangeView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting API keys from user accounts.
    """

    methods = ["GET", "POST"]

    authentication = True

    @classmethod
    def get_view_name(cls):
        return "key-delete"

    @classmethod
    def get_view_icon(cls):
        return "action-delete"

    @classmethod
    def get_view_title(cls, **kwargs):
        return lazy_gettext("Delete API key")

    @classmethod
    def get_view_template(cls):
        return "auth_api/key-delete.html"

    @property
    def dbmodel(self):
        return self.get_model(hawat.const.MODEL_USER)

    @property
    def dbchlogmodel(self):
        return self.get_model(hawat.const.MODEL_ITEM_CHANGELOG)

    @classmethod
    def authorize_item_action(cls, **kwargs):
        """
        Perform access authorization for current user to particular item.
        """
        # Each user must be able to manage his/her API keys.
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(kwargs["item"].id),
        )
        return hawat.acl.PERMISSION_POWER.can() or permission_me.can()

    @staticmethod
    def get_message_success(**kwargs):
        return gettext(
            "API key for user account <strong>%(item_id)s</strong> was successfully deleted.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @staticmethod
    def get_message_failure(**kwargs):
        return gettext(
            "Unable to delete API key for user account <strong>%(item_id)s</strong>.",
            item_id=markupsafe.escape(str(kwargs["item"])),
        )

    @classmethod
    def change_item(cls, **kwargs):
        kwargs["item"].apikey = None


# -------------------------------------------------------------------------------


class APIAuthBlueprint(HawatBlueprint):
    """Pluggable module - API key authentication service (*auth_api*)."""

    @classmethod
    def get_module_title(cls):
        return lazy_gettext("API key authentication service")

    def register_app(self, app):
        login_manager = app.get_resource(hawat.const.RESOURCE_LOGIN_MANAGER)
        user_model = app.get_model(hawat.const.MODEL_USER)

        @login_manager.request_loader
        def load_user_from_request(request):  # pylint: disable=locally-disabled,unused-variable
            """
            Custom login callback for login via request object.

            https://flask-login.readthedocs.io/en/latest/#custom-login-using-request-loader
            """

            # Attempt to extract token from Authorization header. Following formats
            # may be used:
            #   Authorization: abcd1234
            #   Authorization: key abcd1234
            #   Authorization: token abcd1234
            api_key = request.headers.get("Authorization")
            if api_key:
                vals = api_key.split()
                if len(vals) == 1:
                    api_key = vals[0]
                elif len(vals) == 2 and vals[0] in ("token", "key"):
                    api_key = vals[1]
                else:
                    api_key = None
            # API key may also be received via POST method, parameters 'api_key'
            # or 'api_token'. The GET method is forbidden due to the lack
            # of security, there is a possiblity for it to be stored in various
            # insecure places like web server logs.
            if not api_key:
                api_key = request.form.get("api_key")
            if not api_key:
                api_key = request.form.get("api_token")

            # Now login the user with provided API key.
            if api_key:
                dbsess = hawat.db.db_session()
                try:
                    user = dbsess.query(user_model).filter(user_model.apikey == api_key).one()
                    if user:
                        if user.enabled:
                            flask.current_app.logger.info(
                                f"User '{user.login}' used API key to access the resource '{request.url}'."
                            )
                            return user
                        flask.current_app.logger.info(
                            f"The API key for user '{user.login}' was rejected, the account is disabled."
                        )
                except:  # pylint: disable=locally-disabled,bare-except
                    pass

            # Return ``None`` if API key method did not login the user.
            return None


# -------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface for :py:mod:`hawat.Hawat` and factory function. This function
    must return a valid instance of :py:class:`hawat.app.HawatBlueprint` or
    :py:class:`flask.Blueprint`.
    """

    hbp = APIAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder="templates",
        url_prefix=f"/{BLUEPRINT_NAME}",
    )

    hbp.register_view_class(GenerateKeyView, "/<int:item_id>/key-generate")
    hbp.register_view_class(DeleteKeyView, "/<int:item_id>/key-delete")

    return hbp
