# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for prohibited imports.
"""

#
# This is a modified version of the one found in the bandit package.
#
# Original Copyright 2016 Hewlett-Packard Development Company, L.P.
#
# SPDX-License-Identifier: Apache-2.0
#

_prohibitedImports = {
    "S-401": (["telnetlib"], "H"),
    "S-402": (["ftplib"], "H"),
    "S-403": (["pickle", "cPickle", "dill", "shelve"], "L"),
    "S-404": (["subprocess"], "L"),
    "S-405": (["xml.etree.cElementTree", "xml.etree.ElementTree"], "L"),
    "S-406": (["xml.sax"], "L"),
    "S-407": (["xml.dom.expatbuilder"], "L"),
    "S-408": (["xml.dom.minidom"], "L"),
    "S-409": (["xml.dom.pulldom"], "L"),
    "S-411": (["xmlrpc"], "H"),
    "S-412": (
        [
            "wsgiref.handlers.CGIHandler",
            "twisted.web.twcgi.CGIScript",
            "twisted.web.twcgi.CGIDirectory",
        ],
        "H",
    ),
    "S-413": (
        [
            "Crypto.Cipher",
            "Crypto.Hash",
            "Crypto.IO",
            "Crypto.Protocol",
            "Crypto.PublicKey",
            "Crypto.Random",
            "Crypto.Signature",
            "Crypto.Util",
        ],
        "H",
    ),
    "S-414": (["pyghmi"], "H"),
}


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Import": [
            (checkProhibitedImports, tuple(_prohibitedImports)),
        ],
        "ImportFrom": [
            (checkProhibitedImports, tuple(_prohibitedImports)),
        ],
        "Call": [
            (checkProhibitedImports, tuple(_prohibitedImports)),
        ],
    }


def checkProhibitedImports(reportError, context, _config):
    """
    Function to check for prohibited imports.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param _config dictionary with configuration data (unused)
    @type dict
    """
    nodeType = context.node.__class__.__name__

    if nodeType.startswith("Import"):
        prefix = ""
        if nodeType == "ImportFrom" and context.node.module is not None:
            prefix = context.node.module + "."

        for code in _prohibitedImports:
            qualnames, severity = _prohibitedImports[code]
            for name in context.node.names:
                for qualname in qualnames:
                    if (prefix + name.name).startswith(qualname):
                        reportError(
                            context.node.lineno - 1,
                            context.node.col_offset,
                            code,
                            severity,
                            "H",
                            name.name,
                        )
