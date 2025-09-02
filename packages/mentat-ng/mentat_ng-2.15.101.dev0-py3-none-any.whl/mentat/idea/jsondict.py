#!/usr/bin/env python3
# -------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
# -------------------------------------------------------------------------------


"""
This module provides class for object representation and conversion
of `IDEA <https://idea.cesnet.cz/en/index>`__  messages into JSON structures
containing only primitive datat types (``int``, ``str``, ``bool``).

This module is expected to work only with messages based on or compatible with the
:py:class:`mentat.idea.internal.Idea` class, data conversions are very narrow
regarding required input data types and will complain.

This module contains following message class:

* :py:class:`mentat.idea.json.Idea`

    Forward conversion into JSON data format.

Example usage:

.. code-block:: python

    >>> import mentat.idea.internal
    >>> import mentat.idea.json

    # IDEA messages ussually come from regular dicts or JSON
    >>> idea_raw = {...}

    # Just pass the dict as parameter to constructor
    >>> idea_msg = mentat.idea.internal.Idea(idea_raw)

    # When you want to convert IDEA message back into JSON primitive:
    >>> idea_json = mentat.idea.json.Idea(idea_msg)
"""

__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import idea.base
import idea.lite
from idea.base import unicode

import typedcols

import mentat.idea.internal

# -------------------------------------------------------------------------------
# MONGODB CUSTOM DATATYPES (BOTH CONVERSION DIRECTIONS)
# -------------------------------------------------------------------------------


def Timestamp(val):  # pylint: disable=locally-disabled,invalid-name
    """
    Conversion of IDEA Timestamp datatype into appropriate string representation.
    """
    return idea.lite.Idea.json_default(val)


def Duration(val):  # pylint: disable=locally-disabled,invalid-name
    """
    Conversion of IDEA Timestamp datatype into appropriate string representation.
    """
    return idea.lite.Idea.json_default(val)


def Net4(val):  # pylint: disable=locally-disabled,invalid-name
    """
    Conversion of IDEA Timestamp datatype into appropriate string representation.
    """
    return idea.lite.Idea.json_default(val)


def Net6(val):  # pylint: disable=locally-disabled,invalid-name
    """
    Conversion of IDEA Timestamp datatype into appropriate string representation.
    """
    return idea.lite.Idea.json_default(val)


# -------------------------------------------------------------------------------

#
# Define type 'flavour' for Idea class.
#
json_idea_types = {  # pylint: disable=locally-disabled,invalid-name
    "Boolean": bool,
    "Integer": int,
    "String": unicode,
    "Binary": str,
    "ConfidenceFloat": float,
    "Version": idea.lite.Version,
    "MediaType": idea.lite.MediaType,
    "Charset": idea.lite.Charset,
    "Encoding": idea.lite.Encoding,
    "Handle": idea.lite.Handle,
    "ID": idea.lite.ID,
    "Timestamp": Timestamp,
    "Duration": Duration,
    "URI": idea.lite.URI,
    "Net4": Net4,
    "Net6": Net6,
    "Port": idea.lite.Port,
    "NSID": idea.lite.NSID,
    "MAC": idea.lite.MAC,
    "Netname": idea.lite.Netname,
    "Hash": idea.lite.Hash,
    "EventTag": idea.lite.EventTag,
    "ProtocolName": idea.lite.ProtocolName,
    "SourceTargetTag": idea.lite.SourceTargetTag,
    "NodeTag": idea.lite.NodeTag,
    "AttachmentTag": idea.lite.AttachmentTag,
}


def simplify(obj):
    """
    Simplification method from TypedList to list and from TypedDict to dict.

    This simple wrapper just returns the internal ``.data`` attribute after the
    successfull conversion instead of the object itself.
    """
    return lambda x: obj(x).data


#
# Use the simplification wrapper for all IDEA list types.
#

json_idea_lists = {}  # pylint: disable=locally-disabled,invalid-name
for k, v in idea.base.list_types(json_idea_types).items():
    json_idea_lists[k] = simplify(v)


#
# Apply type 'flavour' subdictionary structures.
#


class SourceTargetDict(typedcols.TypedDict):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Typed dictionary representing *Source* and *Target* substructures in IDEA message
    structure.
    """

    allow_unknown = True
    typedef = idea.base.source_target_dict_typedef(json_idea_types, json_idea_lists)


class AttachDict(typedcols.TypedDict):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Typed dictionary representing *Attach* substructure in IDEA message structure.
    """

    allow_unknown = True
    typedef = idea.base.attach_dict_typedef(json_idea_types, json_idea_lists)


class NodeDict(typedcols.TypedDict):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Typed dictionary representing *Node* substructure in IDEA message structure.
    """

    allow_unknown = True
    typedef = idea.base.node_dict_typedef(json_idea_types, json_idea_lists)


class MentatDict(typedcols.TypedDict):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Typed dictionary representing *_Mentat* substructure in IDEA message structure.
    """

    allow_unknown = True
    typedef = mentat.idea.internal.mentat_dict_typedef(
        json_idea_types,
        json_idea_lists,
        simplify(typedcols.typed_list("InspectionErrorsList", str)),
        simplify(typedcols.typed_list("ResolvedAbusesList", str)),
    )


#
# Addon for patching mentat.idea.json.Idea class.
#
# Inject specific data types into mentat.idea.internal addon typedef.
#
json_idea_addon = mentat.idea.internal.internal_base_addon_typedef(  # pylint: disable=locally-disabled,invalid-name
    json_idea_types,
    json_idea_lists,
    simplify(MentatDict),
)


class Idea(idea.base.IdeaBase):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    This class implements datatype conversions to format appropriate for
    raw JSON representation of IDEA messages.

    Despite the fact it is based on ``idea.base.IdeaBase`` class, it is
    designed to process IDEA messages based on :py:class:`mentat.idea.internal.Idea`
    class.
    """

    allow_unknown = True
    typedef = idea.base.idea_typedef(
        json_idea_types,
        json_idea_lists,
        idea.lite.idea_defaults,
        simplify(typedcols.typed_list("SourceList", simplify(SourceTargetDict))),
        simplify(typedcols.typed_list("TargetList", simplify(SourceTargetDict))),
        simplify(typedcols.typed_list("AttachList", simplify(AttachDict))),
        simplify(typedcols.typed_list("NodeList", simplify(NodeDict))),
        json_idea_addon,
    )
