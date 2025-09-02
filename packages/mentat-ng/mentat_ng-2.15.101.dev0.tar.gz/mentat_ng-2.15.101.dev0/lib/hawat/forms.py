#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module contains usefull form related classes for *Hawat* application views.
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"

import datetime
import urllib.parse
from collections.abc import Iterable
from typing import Optional

import flask
import flask_wtf
import pytz
import wtforms
from flask_babel import gettext, lazy_gettext
from markupsafe import Markup, escape

import ipranges
from ransack import Parser, RansackError
from ransack.exceptions import PositionInfoMixin

import hawat.const
import hawat.db
from mentat.const import REPORTING_FILTER_BASIC


def default_dt_with_delta(delta=7):
    """
    Create default timestamp for datetime form values with given time delta in days
    and ceil the result to whole hours.
    """
    return (
        datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        - datetime.timedelta(days=delta)
        + datetime.timedelta(hours=1)
    )


def default_dt():
    """
    Create default timestamp for datetime form values with given time delta in days
    and ceil the result to whole hours.
    """
    return datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)


def str_to_bool(value):
    """
    Convert given string value to boolean.
    """
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    raise ValueError(f"Invalid string value {value!s} to be converted to boolean")


def str_to_bool_with_none(value):
    """
    Convert given string value to boolean or ``None``.
    """
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    if str(value).lower() == "none":
        return None
    if str(value).lower() == "":
        return ""
    raise ValueError(f"Invalid string value {value!s} to be converted to boolean")


def str_to_int_with_none(value):
    """
    Convert given string value to boolean or ``None``.
    """
    if str(value).lower() == "none":
        return None
    try:
        return int(value)
    except Exception as exc:
        raise ValueError(f"Invalid string value {value!s} to be converted to integer") from exc


# -------------------------------------------------------------------------------


def _is_safe_url(target):
    """
    Check, if the URL is safe enough to be redirected to.
    """
    if "\n" in target or "\r" in target or "\\" in target:
        return False

    ref_url = urllib.parse.urlparse(flask.request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(flask.request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def _is_same_path(first, second):
    """
    Check, if both URL point to same path.
    """
    first_url = urllib.parse.urlparse(first)
    second_url = urllib.parse.urlparse(second)
    return first_url.path == second_url.path


def get_redirect_target(target_url=None, default_url=None, exclude_url=None):
    """
    Get redirection target, either from GET request variable, or from referrer header.
    """
    options = (
        target_url,
        flask.request.form.get("next"),
        flask.request.args.get("next"),
        flask.request.referrer,
        default_url,
        flask.url_for(flask.current_app.config["ENDPOINT_HOME"]),
    )
    for target in options:
        if not target:
            continue
        if _is_same_path(target, flask.request.base_url):
            continue
        if exclude_url and _is_same_path(target, exclude_url):
            continue
        if _is_safe_url(target):
            return target
    raise RuntimeError("Unable to choose apropriate redirection target.")


# -------------------------------------------------------------------------------


def check_login(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating user account logins (usernames).
    """
    if hawat.const.CRE_LOGIN.match(field.data):
        return
    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid login name.',
            val=str(field.data),
        )
    )


def check_email(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating user emails or account logins (usernames).
    """
    if hawat.const.CRE_EMAIL.match(field.data):
        return
    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid e-mail address.',
            val=str(field.data),
        )
    )


def check_unique_login(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating of uniqueness of user login.
    """
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    user = hawat.db.db_session().query(user_model).filter_by(login=field.data).first()
    if user is not None:
        raise wtforms.validators.ValidationError(
            gettext(
                'Please use different login, the "%(val)s" is already taken.',
                val=str(field.data),
            )
        )


def check_group_name(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating group name.
    """
    if hawat.const.CRE_GROUP_NAME.match(field.data):
        return
    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid group name.',
            val=str(field.data),
        )
    )


def check_unique_group(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating of uniqueness of group name.
    """
    group_model = flask.current_app.get_model(hawat.const.MODEL_GROUP)
    group = hawat.db.db_session().query(group_model).filter_by(name=field.data).first()
    if group is not None:
        raise wtforms.validators.ValidationError(
            gettext(
                'Please use different group name, the "%(val)s" is already taken.',
                val=str(field.data),
            )
        )


def check_unique_event_class(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating of uniqueness of event class name.
    """
    event_class_model = flask.current_app.get_model(hawat.const.MODEL_EVENT_CLASS)
    event_class = hawat.db.db_session().query(event_class_model).filter_by(name=field.data).first()
    if event_class is not None:
        raise wtforms.validators.ValidationError(
            gettext(
                'Please use different event class name, the "%(val)s" is already taken.',
                val=str(field.data),
            )
        )


def check_email_list(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating list of strings.
    """
    for data in field.data:
        if hawat.const.CRE_EMAIL.match(data):
            continue
        raise wtforms.validators.ValidationError(
            gettext(
                'The "%(val)s" value does not look like valid e-mail address.',
                val=str(data),
            )
        )


def check_ip_record(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating IP addresses.
    """
    # Valid value is a single IPv(4|6) address:
    for tconv in ipranges.IP4, ipranges.IP6:
        try:
            tconv(field.data)
            return
        except ValueError:
            pass

    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid IPv4/IPv6 address.',
            val=str(field.data),
        )
    )


def check_ip4_record(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating IP4 addresses.
    """
    # Valid value is a single IP4 address:
    for tconv in (ipranges.IP4,):
        try:
            tconv(field.data)
            return
        except ValueError:
            pass

    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid IPv4 address.',
            val=str(field.data),
        )
    )


def check_ip6_record(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating IP6 addresses.
    """
    # Valid value is a single IP6 address:
    for tconv in (ipranges.IP6,):
        try:
            tconv(field.data)
            return
        except ValueError:
            pass

    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid IPv6 address.',
            val=str(field.data),
        )
    )


def check_network_record(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating network records.
    """
    # Valid value is an IPv(4|6) address/range/network:
    try:
        ipranges.from_str(field.data)
        return
    except ValueError:
        pass

    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid IPv4/IPv6 address/range/network.',
            val=str(field.data),
        )
    )


def check_network_record_list(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating list of network records.
    """
    for value in field.data:
        try:
            ipranges.from_str(value)
        except ValueError as exc:
            raise wtforms.validators.ValidationError(
                gettext(
                    'The "%(val)s" value does not look like valid IPv4/IPv6 address/range/network.',
                    val=str(value),
                )
            ) from exc


def check_port_list(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating list of ports.
    """
    for data in field.data:
        try:
            if int(data) < 0 or int(data) > 65535:
                raise wtforms.validators.ValidationError(
                    gettext(
                        'The "%(val)s" value does not look like valid port number.',
                        val=str(data),
                    )
                )
        except ValueError as exc:
            raise wtforms.validators.ValidationError(
                gettext(
                    'The "%(val)s" value does not look like valid port number.',
                    val=str(data),
                )
            ) from exc


def check_int_list(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating list of positive integers.
    """
    for data in field.data:
        try:
            if int(data) < 0:
                raise wtforms.validators.ValidationError(
                    gettext(
                        'The "%(val)s" value does not look like valid positive integer.',
                        val=str(data),
                    )
                )
        except ValueError as exc:
            raise wtforms.validators.ValidationError(
                gettext(
                    'The "%(val)s" value does not look like valid positive integer.',
                    val=str(data),
                )
            ) from exc


def check_null_character(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating string fields which should not contain 0x00.
    """
    if "\x00" in field.data:
        raise wtforms.validators.StopValidation(
            gettext(
                'The "%(val)s" value cannot contain NUL (0x00) characters.',
                val=str(field.data),
            )
        )


def check_filter(_form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating ransack filter.

    If the form contains field 'type' with value 'basic', the validation is not
    performed.
    """
    if "type" in _form and _form.type.data == REPORTING_FILTER_BASIC:
        return

    parser = Parser()
    try:
        parser.parse(field.data)
    except RansackError as err:
        base_message = str(err)
        full_message = gettext('Filtering rule parse error: "%(error)s"', error=base_message)

        if isinstance(err, PositionInfoMixin):
            meta_html = Markup(
                f'<span class="monaco-error-marker" '
                f'data-line="{err.line}" '
                f'data-column="{err.column}" '
                f'data-end-line="{err.end_line or err.line}" '
                f'data-end-column="{err.end_column or (err.column + 1)}" '
                f'data-message="{escape(base_message)}"></span>'
            )
            full_message += meta_html

        raise wtforms.validators.ValidationError(full_message) from err


def get_available_groups():
    """
    Query the database for list of all available groups.
    """
    group_model = flask.current_app.get_model(hawat.const.MODEL_GROUP)
    return hawat.db.db_query(group_model).order_by(group_model.name).all()


def get_available_users():
    """
    Query the database for list of users.
    """
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    return hawat.db.db_query(user_model).order_by(user_model.fullname).all()


def get_available_group_sources():
    """
    Query the database for list of network record sources.
    """
    group_model = flask.current_app.get_model(hawat.const.MODEL_GROUP)
    result = hawat.db.db_query(group_model).distinct(group_model.source).order_by(group_model.source).all()
    return [x.source for x in result]


def get_event_classes():
    """
    Returns a list of all event classes.
    """
    event_class_model = flask.current_app.get_model(hawat.const.MODEL_EVENT_CLASS)
    return hawat.db.db_query(event_class_model).all()


def coerce_model(x, model, attribute):
    """
    Coerce the input into an instance of the specified model.

    This function ensures that the selected value is properly converted into an
    instance of the specified model. It handles cases where the input is already
    an instance of the model, or a string representing the name of the instance.

    Parameters:
        x (Union[str, model]): The input value to be coerced. This can be
                               a string representing the name or an instance of the model.
        model (type): The model class to coerce the input into.

    Returns:
        Union[model, str, None]: The corresponding model instance if the input is valid,
                                 the input string if the instance is not found,
                                 or None if the input is neither a valid name nor an
                                 instance of the model.
    """
    if isinstance(x, model):
        return x
    if isinstance(x, str):
        # Special case to search <<system>> user.
        if x == "__SYSTEM__":
            return x

        # For strings returns either None, model instance, or string itself.
        # The last option is needed to inform users about which choices are invalid.
        if x == "":
            return None
        instance = hawat.db.db_query(model).filter(getattr(model, attribute) == x).first()
        return instance if instance else x
    return None


def coerce_group(x):
    """
    Coerce the input into a GroupModel instance.
    """
    group_model = flask.current_app.get_model(hawat.const.MODEL_GROUP)
    return coerce_model(x, group_model, "name")


def coerce_user(x):
    """
    Coerce the input into a UserModel instance.
    """
    user_model = flask.current_app.get_model(hawat.const.MODEL_USER)
    return coerce_model(x, user_model, "login")


def filter_none_from_list(objects):
    """
    Remove None values from a list.

    Parameters:
        objects (list): The list of objects to be filtered.

    Returns:
        list: A list with all None values removed.
    """
    return [obj for obj in objects if obj is not None]


def filter_no_group_from_list(objects):
    """
    Remove __NO_GROUP__ values from a list. __NO_GROUP__ is used
    in registration forms to force user to explicitly say they
    don't want to join any group.

    Parameters:
        objects (list): The list of objects to be filtered.

    Returns:
        list: A list with all __NO_GROUP__ values removed.
    """
    return [obj for obj in objects if obj != "__NO_GROUP__"]


def format_select_option_label_user(user):
    """
    Format option for selection of user accounts.
    """
    return f"{user.fullname} ({user.login})"


class TimedeltaRangeValidator:
    """
    Custom validator for checking that the value of a timedelta field is within a specified
    timedelta range.
    """

    def __init__(
        self,
        min_: Optional[datetime.timedelta] = None,
        max_: Optional[datetime.timedelta] = None,
    ):
        if min_ is None and max_ is None:
            raise ValueError("At least one of min_ or max_ must be specified.")
        self.min = min_
        self.max = max_

    def __call__(self, _form: wtforms.Form, field: "TimedeltaField") -> None:
        if field.data is None:
            return

        if self.min is not None and field.data < self.min:
            raise wtforms.validators.ValidationError(
                gettext(
                    'The "%(val)s" value is below the minimum allowed value.',
                    val=str(field.data),
                )
            )
        if self.max is not None and field.data > self.max:
            raise wtforms.validators.ValidationError(
                gettext(
                    'The "%(val)s" value is above the maximum allowed value.',
                    val=str(field.data),
                )
            )


def validate_datetime_order(prefix="dt"):
    """
    Validates that a 'from' datetime field is earlier than or equal to a corresponding 'to' datetime field.

    Parameters:
        prefix (str): The prefix for the datetime fields. Defaults to "dt".
                      For example, if prefix="dt", the fields checked are:
                      - dt_from
                      - dt_to
                      If prefix="valid", the fields checked are:
                      - valid_from
                      - valid_to
    """

    def _validator(form, field):
        # Construct field names dynamically based on the prefix
        t_from = getattr(form, f"{prefix}_from").data
        t_to = getattr(form, f"{prefix}_to").data

        # Set error message based on the prefix
        if prefix == "valid":
            msg = "'Valid from' cannot be later than 'Valid to'."
        elif prefix == "st":
            msg = "'Storage time from' cannot be later than 'Storage time to'."
        else:
            msg = "'time from' cannot be later than 'time to'"

        # Perform the validation check
        if t_from and t_to and t_from > t_to:
            raise wtforms.validators.ValidationError(gettext(msg))

    return _validator


# -------------------------------------------------------------------------------


class CommaListField(wtforms.Field):
    """
    Custom widget representing list of strings as comma separated list.
    """

    widget = wtforms.widgets.TextInput()

    def _value(self):
        if self.data:
            return ", ".join(self.data)
        return ""

    def process_formdata(self, valuelist):
        self.data = []  # pylint: disable=locally-disabled,attribute-defined-outside-init
        if valuelist:
            for val in valuelist[0].split(","):
                if val.strip() == "":
                    continue
                self.data.append(val.strip())
            self.data = list(self._remove_duplicates(self.data))  # pylint: disable=locally-disabled,attribute-defined-outside-init

    @classmethod
    def _remove_duplicates(cls, seq):
        """
        Remove duplicates in a case insensitive, but case preserving manner.
        """
        tmpd = {}
        for item in seq:
            if item.lower() not in tmpd:
                tmpd[item.lower()] = True
                yield item


class DateTimeLocalField(wtforms.DateTimeField):
    """
    DateTimeField that assumes input is in app-configured timezone and converts
    to UTC for further processing/storage.
    """

    def process_data(self, value):
        """
        Process the Python data applied to this field and store the result.
        This will be called during form construction by the form's `kwargs` or
        `obj` argument.
        :param value: The python object containing the value to process.
        """
        localtz = pytz.timezone(flask.session["timezone"])
        if value:
            try:
                dt_utc = pytz.utc.localize(value, is_dst=None)
                self.data = dt_utc.astimezone(localtz)  # pylint: disable=locally-disabled,attribute-defined-outside-init
            except (
                pytz.exceptions.AmbiguousTimeError,
                pytz.exceptions.NonExistentTimeError,
            ):
                self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init
        else:
            self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.
        This will be called during form construction with data supplied
        through the `formdata` argument.
        :param valuelist: A list of strings to process.
        """
        localtz = pytz.timezone(flask.session["timezone"])
        if valuelist:
            date_str = " ".join(valuelist)
            try:
                dt_naive = datetime.datetime.strptime(date_str, self.format)
                dt_local = localtz.localize(dt_naive, is_dst=None)
                self.data = dt_local.astimezone(pytz.utc)  # pylint: disable=locally-disabled,attribute-defined-outside-init
            except (
                pytz.exceptions.AmbiguousTimeError,
                pytz.exceptions.NonExistentTimeError,
                ValueError,
            ) as exc:
                self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init
                raise ValueError(self.gettext("Not a valid datetime value")) from exc


class SmartDateTimeField(wtforms.Field):
    """
    DateTimeField that assumes input is in app-configured timezone and converts
    to UTC for further processing/storage. This widget allows multiple datetime
    representations on input and is smart to recognize ISO formatted timestamp in
    UTC on input, which greatly simplifies generating URLs from within the
    application.
    """

    widget = wtforms.widgets.TextInput()

    def __init__(self, label=None, validators=None, formats=None, **kwargs):
        super().__init__(label, validators, **kwargs)
        if formats is None:
            self.formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M",
            ]
        else:
            self.formats = formats
        self.format = self.formats[0]

    def _value(self):
        """
        This method is called when rendering the widget to determine the value to
        display to the user within the widget.
        """
        if self.data:
            localtz = pytz.timezone(flask.session["timezone"])
            return localtz.normalize(self.data.replace(tzinfo=pytz.UTC).astimezone(localtz)).strftime(self.format)
        return ""

    def process_data(self, value):
        """
        Process the Python data applied to this field and store the result.
        This will be called during form construction by the form's `kwargs` or
        `obj` argument.
        :param value: The python object containing the value to process.
        """
        self.data = value or None  # pylint: disable=locally-disabled,attribute-defined-outside-init

    def process_formdata(self, valuelist):
        """
        Process data received over the wire from a form.
        This will be called during form construction with data supplied
        through the `formdata` argument.
        :param valuelist: A list of strings to process.
        """
        localtz = pytz.timezone(flask.session["timezone"])
        if valuelist:
            date_str = " ".join(valuelist)
            # Try all explicitly defined valid datetime formats.
            for fmt in self.formats:
                try:
                    dt_naive = datetime.datetime.strptime(date_str, fmt)
                    dt_local = localtz.localize(dt_naive, is_dst=None)
                    self.data = dt_local.astimezone(pytz.utc).replace(tzinfo=None)  # pylint: disable=locally-disabled,attribute-defined-outside-init
                    self.format = fmt
                    print(
                        f"Received datetime value in format {fmt}, naive: {dt_naive.isoformat()}, local: {dt_local.isoformat()}, utc: {self.data.isoformat()}"
                    )
                except ValueError:
                    self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init
                except pytz.exceptions.AmbiguousTimeError:
                    self.data = (
                        localtz.localize(datetime.datetime.strptime(date_str, fmt), is_dst=False)
                        .astimezone(pytz.utc)
                        .replace(tzinfo=None)
                    )  # pylint: disable=locally-disabled,attribute-defined-outside-init
                    break
                except pytz.exceptions.NonExistentTimeError:
                    self.data = (
                        localtz.localize(datetime.datetime.strptime(date_str, fmt), is_dst=True)
                        .astimezone(pytz.utc)
                        .replace(tzinfo=None)
                    )  # pylint: disable=locally-disabled,attribute-defined-outside-init
                    break
                else:
                    break
            # In case of failure try ISO format (YYYY-MM-DDTHH:MM:SS+ZZ:ZZ).
            if self.data is None:
                try:
                    dt = datetime.datetime.fromisoformat(date_str)
                    if dt.tzinfo is None:
                        raise ValueError("In case of ISO timestamp, timezone must be specified.")
                    self.data = dt.astimezone(pytz.utc).replace(tzinfo=None)  # pylint: disable=locally-disabled,attribute-defined-outside-init
                    print(f"Received ISO datetime value, original: {dt.isoformat()}, utc: {self.data.isoformat()}")
                except ValueError:
                    self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init
            if self.data is None:
                raise ValueError(self.gettext("Value did not match any of datetime formats."))


class TimedeltaField(wtforms.Field):
    """
    Field for entering time deltas in seconds.
    """

    data: Optional[datetime.timedelta]
    widget = wtforms.widgets.NumberInput(min=0)

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                seconds = int(valuelist[0])
                if seconds < 0:
                    raise ValueError("Value must be a positive integer")
                self.data = datetime.timedelta(seconds=seconds)
            except ValueError as e:
                self.data = None
                raise wtforms.ValidationError(
                    "Invalid input: please enter a positive integer representing seconds."
                ) from e

    def _value(self):
        # Convert the timedelta to seconds for display in the form
        if self.data:
            return str(int(self.data.total_seconds()))
        return ""


class RadioFieldWithNone(wtforms.RadioField):
    """
    RadioField that accepts None as valid choice.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = self.coerce(valuelist[0]) if valuelist[0] != "None" else None  # pylint: disable=locally-disabled,attribute-defined-outside-init
            except ValueError as exc:
                raise ValueError(self.gettext("Invalid Choice: could not coerce")) from exc

    def pre_validate(self, form):
        for val, _ in self.choices:
            if self.data == val:
                break
        else:
            raise wtforms.validators.ValidationError(self.gettext("Not a valid choice"))


class SelectFieldWithNone(wtforms.SelectField):
    """
    SelectField that accepts None as valid choice.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = self.coerce(valuelist[0]) if valuelist[0].lower() != "none" else None  # pylint: disable=locally-disabled,attribute-defined-outside-init
            except ValueError as exc:
                raise ValueError(self.gettext("Invalid Choice: could not coerce")) from exc
        else:
            self.data = None  # pylint: disable=locally-disabled,attribute-defined-outside-init

    def pre_validate(self, form):
        for val, _ in self.choices:
            if self.data == val:
                break
        else:
            raise wtforms.validators.ValidationError(self.gettext("Not a valid choice"))


class HawatBaseForm(flask_wtf.FlaskForm):
    """
    Class representing generic form for hawat application.
    """

    @classmethod
    def get_field_names(cls) -> Iterable[str]:
        """
        Return names of all fields in the form.

        :return: Iterable of all fields in the form.
        """
        return (
            name
            for name in dir(cls)
            if not name.startswith("_")
            and isinstance(getattr(cls, name), (wtforms.fields.core.UnboundField, wtforms.Field))
        )

    @classmethod
    def is_csag_context_excluded(cls, field_name: str) -> bool:
        """
        Check if given form field should be excluded from CSAG context.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field should be excluded, ``False`` otherwise.
        """
        return False

    @classmethod
    def is_csag_context_insignificant(cls, field_name: str) -> bool:  # pylint: disable=locally-disabled,unused-argument
        """
        Check if given form field is insignificant for CSAG context.
        insignificant keys are ignored in relevancy check.

        In general, fields with defined `default` value that does not signify
        an empty value should be considered insignificant.

        (E.g. dt_from and dt_to fields in most search forms.)

        :param str field_name: Name of the form field.
        :return: ``True``, if the field is insignificant, ``False`` otherwise.
        """
        return False

    @classmethod
    def is_multivalue(cls, field_name: str) -> bool:  # pylint: disable=locally-disabled,unused-argument
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        """
        return False

    def must_be_filled(self) -> bool:
        """
        Check, if at least one field in the form must be filled by user.

        :return: ``True``, if the form contains a required field without a default, ``False`` otherwise.
        """
        return any(field.flags.required and not field.default for field in self)


class BaseItemForm(HawatBaseForm):
    """
    Class representing generic item action (create/update/delete) form for hawat
    application.

    This form contains support for redirection back to original page.
    """

    next = wtforms.HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the redirection URL.
        if not self.next.data:
            self.next.data = get_redirect_target() or ""

    @classmethod
    def is_csag_context_excluded(cls, field_name: str) -> bool:
        """
        Check if given form field should be excluded from CSAG context.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field should be excluded, ``False`` otherwise.
        """
        return field_name in ("next",) or super().is_csag_context_excluded(field_name)


class ItemActionConfirmForm(BaseItemForm):
    """
    Class representing generic item action confirmation form for hawat application.

    This form contains nothing else but two buttons, one for confirmation, one for
    canceling the delete action. Actual item identifier is passed as part of the URL.
    """

    submit = wtforms.SubmitField(lazy_gettext("Confirm"))

    @classmethod
    def is_csag_context_excluded(cls, field_name: str) -> bool:
        return field_name in ("submit",) or super().is_csag_context_excluded(field_name)


class BaseSearchForm(HawatBaseForm):
    """
    Class representing generic item search form for hawat application.

    This form contains support for result limiting and paging.
    """

    limit = wtforms.IntegerField(
        lazy_gettext("Pager limit:"),
        validators=[
            wtforms.validators.NumberRange(
                min=1,
                max=100000,
                message=lazy_gettext("Parameter limit must be an integer between 1 and 100000"),
            )
        ],
        default=hawat.const.DEFAULT_PAGER_LIMIT,
    )
    page = wtforms.IntegerField(
        lazy_gettext("Page number:"),
        validators=[
            wtforms.validators.NumberRange(
                min=1,
                max=hawat.const.MAX_NUMBER_OF_PAGES,
                message=lazy_gettext(
                    "Parameter page must be an integer between 1 and %(_max)s",
                    _max=str(hawat.const.MAX_NUMBER_OF_PAGES),
                ),
            )
        ],
        default=1,
    )
    submit = wtforms.SubmitField(lazy_gettext("Search"))

    @classmethod
    def is_csag_context_excluded(cls, field_name: str) -> bool:
        return field_name in (
            "limit",
            "page",
            "submit",
        ) or super().is_csag_context_excluded(field_name)


class EventSearchFormBase(BaseSearchForm):
    """
    Class representing common base of an event search form.
    """

    dt_from = SmartDateTimeField(
        lazy_gettext("Detection time from:"),
        validators=[
            wtforms.validators.Optional(),
            validate_datetime_order(prefix="dt"),
        ],
        description=lazy_gettext(
            "Lower time boundary for event detection time as provided by event detector. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event detectors are usually outside of the control of Mentat system administrators and may sometimes emit events with invalid detection times, for example timestamps in the future."
        ),
        default=lambda: default_dt_with_delta(hawat.const.DEFAULT_RESULT_TIMEDELTA),
    )
    dt_to = SmartDateTimeField(
        lazy_gettext("Detection time to:"),
        validators=[wtforms.validators.Optional()],
        description=lazy_gettext(
            "Upper time boundary for event detection time as provided by event detector. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event detectors are usually outside of the control of Mentat system administrators and may sometimes emit events with invalid detection times, for example timestamps in the future."
        ),
        default=default_dt,
    )
    st_from = SmartDateTimeField(
        lazy_gettext("Storage time from:"),
        validators=[
            wtforms.validators.Optional(),
            validate_datetime_order(prefix="st"),
        ],
        description=lazy_gettext(
            "Lower time boundary for event storage time. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event storage time is provided by Mentat system itself. It is a timestamp of the exact moment the event was stored into the database."
        ),
    )
    st_to = SmartDateTimeField(
        lazy_gettext("Storage time to:"),
        validators=[wtforms.validators.Optional()],
        description=lazy_gettext(
            "Upper time boundary for event storage time. Timestamp is expected to be in the format <code>YYYY-MM-DD hh:mm:ss</code> and in the timezone according to the user`s preferences. Event storage time is provided by Mentat system itself. It is a timestamp of the exact moment the event was stored into the database."
        ),
    )
    source_addrs = CommaListField(
        lazy_gettext("Source addresses:"),
        validators=[
            wtforms.validators.Optional(),
            check_network_record_list,
        ],
        filters=[lambda lst: [source.replace("[.]", ".") for source in lst]],
        widget=wtforms.widgets.TextArea(),
        description=lazy_gettext(
            "Comma separated list of event source IP4/6 addresses, ranges or networks. In this context a source does not necessarily mean a source of the connection, but rather a source of the problem as reported by a detector. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    target_addrs = CommaListField(
        lazy_gettext("Target addresses:"),
        validators=[
            wtforms.validators.Optional(),
            check_network_record_list,
        ],
        filters=[lambda lst: [source.replace("[.]", ".") for source in lst]],
        widget=wtforms.widgets.TextArea(),
        description=lazy_gettext(
            "Comma separated list of event target IP4/6 addresses, ranges or networks. In this context a target does not necessarily mean a target of the connection, but rather a victim of the problem as reported by a detector. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    host_addrs = CommaListField(
        lazy_gettext("Host addresses:"),
        validators=[
            wtforms.validators.Optional(),
            check_network_record_list,
        ],
        filters=[lambda lst: [source.replace("[.]", ".") for source in lst]],
        widget=wtforms.widgets.TextArea(),
        description=lazy_gettext(
            "Comma separated list of event source or target IP4/6 addresses, ranges or networks. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    source_ports = CommaListField(
        lazy_gettext("Source ports:"),
        validators=[wtforms.validators.Optional(), check_port_list],
        description=lazy_gettext(
            "Comma separated list of source ports as integers. In this context a source does not necessarily mean a source of the connection, but rather a source of the problem as reported by a detector. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    target_ports = CommaListField(
        lazy_gettext("Target ports:"),
        validators=[wtforms.validators.Optional(), check_port_list],
        description=lazy_gettext(
            "Comma separated list of target ports as integers. In this context a target does not necessarily mean a target of the connection, but rather a victim of the problem as reported by a detector. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    host_ports = CommaListField(
        lazy_gettext("Host ports:"),
        validators=[wtforms.validators.Optional(), check_port_list],
        description=lazy_gettext(
            "Comma separated list of source or target ports as integers. Any additional whitespace is ignored and may be used for better readability."
        ),
    )
    source_types = wtforms.SelectMultipleField(
        lazy_gettext("Source types:"),
        validators=[wtforms.validators.Optional()],
        choices=[],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of event source type. Each event source may be optionally assigned one or more labels to better categorize type of a source."
        ),
    )
    target_types = wtforms.SelectMultipleField(
        lazy_gettext("Target types:"),
        validators=[wtforms.validators.Optional()],
        choices=[],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of event target type. Each event target may be optionally assigned one or more labels to better categorize type of a target."
        ),
    )
    host_types = wtforms.SelectMultipleField(
        lazy_gettext("Host types:"),
        validators=[wtforms.validators.Optional()],
        choices=[],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of event source or target type. Each event source or target may be optionally assigned one or more labels to better categorize type of a source or target."
        ),
    )
    detectors = wtforms.SelectMultipleField(
        lazy_gettext("Detectors:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext("Name of the detector that detected the event."),
    )
    not_detectors = wtforms.HiddenField(
        lazy_gettext("Negate detector selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    detector_types = wtforms.SelectMultipleField(
        lazy_gettext("Detector types:"),
        validators=[wtforms.validators.Optional()],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of event detector type. Each event detector may be optionally assigned one or more labels to better categorize that detector."
        ),
    )
    not_detector_types = wtforms.HiddenField(
        lazy_gettext("Negate detector_type selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    categories = wtforms.SelectMultipleField(
        lazy_gettext("Categories:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            'Specification of event category. Each event may be optionally assigned one or more labels to better categorize that event, for example as "Recon.Scanning", "Abusive.Spam", "Test" etc.'
        ),
    )
    not_categories = wtforms.HiddenField(
        lazy_gettext("Negate category selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    severities = wtforms.SelectMultipleField(
        lazy_gettext("Source severities:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of source severity. Each event may be optionally assigned one source severity level, which can be then use during incident handling workflows to prioritize events."
        ),
    )
    not_severities = wtforms.HiddenField(
        lazy_gettext("Negate source severity selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    target_severities = wtforms.SelectMultipleField(
        lazy_gettext("Target severities:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of target severity. Each event may be optionally assigned one target severity level, which can be then use during incident handling workflows to prioritize events."
        ),
    )
    not_target_severities = wtforms.HiddenField(
        lazy_gettext("Negate target severity selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    classes = wtforms.SelectMultipleField(
        lazy_gettext("Source classes:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of source class. Each event may be optionally assigned one source class to better describe the event and group all similar events together for better processing. Event classification in internal feature of Mentat system for better event management."
        ),
    )
    not_classes = wtforms.HiddenField(
        lazy_gettext("Negate source class selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    target_classes = wtforms.SelectMultipleField(
        lazy_gettext("Target classes:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of target class. Each event may be optionally assigned one target class to better describe the event and group all similar events together for better processing. Event classification in internal feature of Mentat system for better event management."
        ),
    )
    not_target_classes = wtforms.HiddenField(
        lazy_gettext("Negate target class selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    description = wtforms.StringField(
        lazy_gettext("Description:"),
        validators=[wtforms.validators.Optional(), check_null_character],
        description=lazy_gettext(
            "Specification of event description. Each event may be optionally assigned short descriptive string."
        ),
    )
    protocols = wtforms.SelectMultipleField(
        lazy_gettext("Protocols:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext("Specification of one or more communication protocols involved in the event."),
    )
    not_protocols = wtforms.HiddenField(
        lazy_gettext("Negate protocol selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    groups = wtforms.SelectMultipleField(
        lazy_gettext("Source group:"),
        default=[],
        coerce=coerce_group,
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[filter_none_from_list],
        description=lazy_gettext(
            "Specification of the source group to whose constituency this event belongs based on one of the event source addresses."
        ),
    )
    not_groups = wtforms.HiddenField(
        lazy_gettext("Negate group selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    target_groups = wtforms.SelectMultipleField(
        lazy_gettext("Target group:"),
        default=[],
        coerce=coerce_group,
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[filter_none_from_list],
        description=lazy_gettext(
            "Specification of the target group to whose constituency this event belongs based on one of the event target addresses."
        ),
    )
    not_target_groups = wtforms.HiddenField(
        lazy_gettext("Negate target group selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    inspection_errs = wtforms.SelectMultipleField(
        lazy_gettext("Inspection errors:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext(
            "Specification of possible event errors detected during event inspection by real-time event processing inspection daemon."
        ),
    )
    not_inspection_errs = wtforms.HiddenField(
        lazy_gettext("Negate inspection error selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )
    tlps = wtforms.SelectMultipleField(
        lazy_gettext("TLPs:"),
        validators=[
            wtforms.validators.Optional(),
        ],
        choices=[
            ("__EMPTY__", lazy_gettext("<< without value >>")),
            ("__ANY__", lazy_gettext("<< any value >>")),
        ],
        filters=[lambda x: x or []],
        description=lazy_gettext("Specification of Traffic Light Protocol (TLP) value of the events."),
    )
    not_tlps = wtforms.HiddenField(
        lazy_gettext("Negate TLPs selection:"),
        validators=[
            wtforms.validators.Optional(),
        ],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.source_types.choices = kwargs["choices_source_types"]
        self.target_types.choices = kwargs["choices_target_types"]
        self.host_types.choices = kwargs["choices_host_types"]

        self.detectors.choices[2:] = kwargs["choices_detectors"]
        self.detector_types.choices[2:] = kwargs["choices_detector_types"]
        self.categories.choices[2:] = kwargs["choices_categories"]
        self.severities.choices[2:] = kwargs["choices_severities"]
        self.target_severities.choices[2:] = kwargs["choices_target_severities"]
        self.classes.choices[2:] = kwargs["choices_classes"]
        self.target_classes.choices[2:] = kwargs["choices_target_classes"]
        self.protocols.choices[2:] = kwargs["choices_protocols"]
        self.inspection_errs.choices[2:] = kwargs["choices_inspection_errs"]
        self.tlps.choices[2:] = kwargs["choices_TLPs"]

        groups = get_available_groups()
        self.groups.choices[2:] = [(group, group.name) for group in groups]
        self.target_groups.choices[2:] = [(group, group.name) for group in groups]

    @staticmethod
    def is_multivalue(field_name):
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return field_name in (
            "source_addrs",
            "target_addrs",
            "host_addrs",
            "source_ports",
            "target_ports",
            "host_ports",
            "source_types",
            "target_types",
            "host_types",
            "detectors",
            "detector_types",
            "categories",
            "severities",
            "classes",
            "protocols",
            "groups",
            "inspection_errs",
            "tlps",
        )

    @classmethod
    def is_csag_context_insignificant(cls, field_name):
        return field_name in (
            "dt_from",
            "dt_to",
            "st_from",
            "st_to",
        ) or super().is_csag_context_insignificant(field_name)
