# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for prohibited methods and functions.
"""

#
# This is a modified version of the one found in the bandit package.
#
# Original Copyright 2016 Hewlett-Packard Development Company, L.P.
#
# SPDX-License-Identifier: Apache-2.0
#

import ast
import fnmatch

import AstUtilities

_prohibitedCalls = {
    "S-301": (
        [
            "pickle.loads",
            "pickle.load",
            "pickle.Unpickler",
            "dill.loads",
            "dill.load",
            "dill.Unpickler",
            "shelve.open",
            "shelve.DbfilenameShelf",
            "jsonpickle.decode",
            "jsonpickle.unpickler.decode",
            "jsonpickle.unpickler.Unpickler",
            "pandas.read_pickle",
        ],
        "M",
    ),
    "S-302": (["marshal.load", "marshal.loads"], "M"),
    "S-303": (
        [
            "Crypto.Hash.MD2.new",
            "Crypto.Hash.MD4.new",
            "Crypto.Hash.MD5.new",
            "Crypto.Hash.SHA.new",
            "Cryptodome.Hash.MD2.new",
            "Cryptodome.Hash.MD4.new",
            "Cryptodome.Hash.MD5.new",
            "Cryptodome.Hash.SHA.new",
            "cryptography.hazmat.primitives.hashes.MD5",
            "cryptography.hazmat.primitives.hashes.SHA1",
        ],
        "M",
    ),
    "S-304": (
        [
            "Crypto.Cipher.ARC2.new",
            "Crypto.Cipher.ARC4.new",
            "Crypto.Cipher.Blowfish.new",
            "Crypto.Cipher.DES.new",
            "Crypto.Cipher.XOR.new",
            "Cryptodome.Cipher.ARC2.new",
            "Cryptodome.Cipher.ARC4.new",
            "Cryptodome.Cipher.Blowfish.new",
            "Cryptodome.Cipher.DES.new",
            "Cryptodome.Cipher.XOR.new",
            "cryptography.hazmat.primitives.ciphers.algorithms.ARC4",
            "cryptography.hazmat.primitives.ciphers.algorithms.Blowfish",
            "cryptography.hazmat.primitives.ciphers.algorithms.CAST5",
            "cryptography.hazmat.primitives.ciphers.algorithms.IDEA",
            "cryptography.hazmat.primitives.ciphers.algorithms.SEED",
            "cryptography.hazmat.primitives.ciphers.algorithms.TripleDES",
        ],
        "H",
    ),
    "S-305": (["cryptography.hazmat.primitives.ciphers.modes.ECB"], "M"),
    "S-306": (["tempfile.mktemp"], "M"),
    "S-307": (["eval"], "M"),
    "S-308": (["django.utils.safestring.mark_safe"], "M"),
    "S-310": (
        [
            "urllib.request.urlopen",
            "urllib.request.urlretrieve",
            "urllib.request.URLopener",
            "urllib.request.FancyURLopener",
            "six.moves.urllib.request.urlopen",
            "six.moves.urllib.request.urlretrieve",
            "six.moves.urllib.request.URLopener",
            "six.moves.urllib.request.FancyURLopener",
        ],
        "",
    ),
    "S-311": (
        [
            "random.Random",
            "random.random",
            "random.randrange",
            "random.randint",
            "random.choice",
            "random.choices",
            "random.uniform",
            "random.triangular",
            "random.randbytes",
            "random.sample",
            "random.randrange",
            "random.getrandbits",
        ],
        "L",
    ),
    "S-312": (["telnetlib.Telnet"], "H"),
    "S-313": (
        [
            "xml.etree.cElementTree.parse",
            "xml.etree.cElementTree.iterparse",
            "xml.etree.cElementTree.fromstring",
            "xml.etree.cElementTree.XMLParser",
        ],
        "M",
    ),
    "S-314": (
        [
            "xml.etree.ElementTree.parse",
            "xml.etree.ElementTree.iterparse",
            "xml.etree.ElementTree.fromstring",
            "xml.etree.ElementTree.XMLParser",
        ],
        "M",
    ),
    "S-315": (["xml.sax.expatreader.create_parser"], "M"),
    "S-316": (
        ["xml.dom.expatbuilder.parse", "xml.dom.expatbuilder.parseString"],
        "M",
    ),
    "S-317": (["xml.sax.parse", "xml.sax.parseString", "xml.sax.make_parser"], "M"),
    "S-318": (["xml.dom.minidom.parse", "xml.dom.minidom.parseString"], "M"),
    "S-319": (["xml.dom.pulldom.parse", "xml.dom.pulldom.parseString"], "M"),
    "S-321": (["ftplib.FTP"], "H"),
    "S-323": (["ssl._create_unverified_context"], "M"),
}


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Call": [
            (checkProhibitedCalls, tuple(_prohibitedCalls)),
        ],
    }


def checkProhibitedCalls(reportError, context, _config):
    """
    Function to check for prohibited method calls.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param _config dictionary with configuration data (unused)
    @type dict
    """
    nodeType = context.node.__class__.__name__

    if nodeType == "Call":
        func = context.node.func
        if isinstance(func, ast.Name) and func.id == "__import__":
            if len(context.node.args):
                if AstUtilities.isString(context.node.args[0]):
                    name = context.node.args[0].value
                else:
                    name = "UNKNOWN"
            else:
                name = ""  # handle '__import__()'
        else:
            name = context.callFunctionNameQual
            # In the case the Call is an importlib.import, treat the first
            # argument name as an actual import module name.
            # Will produce None if argument is not a literal or identifier.
            if name in ["importlib.import_module", "importlib.__import__"]:
                name = context.callArgs[0]

        for code in _prohibitedCalls:
            qualnames, severity = _prohibitedCalls[code]
            for qualname in qualnames:
                if name and fnmatch.fnmatch(name, qualname):
                    reportError(
                        context.node.lineno - 1,
                        context.node.col_offset,
                        code,
                        severity,
                        "H",
                        name,
                    )
