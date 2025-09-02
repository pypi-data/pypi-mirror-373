# -*- coding: utf-8 -*-

# Copyright (c) 2014 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin messages.
"""

import contextlib
import re

from PyQt6.QtCore import QCoreApplication

from .Annotations.translations import (
    _annotationsMessages,
    _annotationsMessagesSampleArgs,
)
from .Async.translations import _asyncMessages, _asyncMessageSampleArgs
from .Complexity.translations import _complexityMessages, _complexityMessagesSampleArgs
from .DocStyle.translations import _docStyleMessages, _docStyleMessagesSampleArgs
from .Imports.translations import _importsMessages, _importsMessagesSampleArgs
from .Logging.translations import _loggingMessages, _loggingMessagesSampleArgs
from .Miscellaneous.translations import (
    _miscellaneousMessages,
    _miscellaneousMessagesSampleArgs,
)
from .NameOrder.translations import _nameOrderMessages, _nameOrderMessagesSampleArgs
from .Naming.translations import _namingStyleMessages
from .PathLib.translations import _pathlibMessages
from .Pydantic.translations import _pydanticMessages
from .Security.translations import _securityMessages, _securityMessagesSampleArgs
from .Simplify.translations import _simplifyMessages, _simplifyMessagesSampleArgs
from .Unused.translations import _unusedMessages, _unusedMessagesSampleArgs

##################################################################
## pycodestyle error messages
##################################################################

_pycodestyleErrorMessages = {
    "E-101": QCoreApplication.translate(
        "pycodestyle", "indentation contains mixed spaces and tabs"
    ),
    "E-111": QCoreApplication.translate(
        "pycodestyle", "indentation is not a multiple of four"
    ),
    "E-112": QCoreApplication.translate("pycodestyle", "expected an indented block"),
    "E-113": QCoreApplication.translate("pycodestyle", "unexpected indentation"),
    "E-114": QCoreApplication.translate(
        "pycodestyle", "indentation is not a multiple of four (comment)"
    ),
    "E-115": QCoreApplication.translate(
        "pycodestyle", "expected an indented block (comment)"
    ),
    "E-116": QCoreApplication.translate(
        "pycodestyle", "unexpected indentation (comment)"
    ),
    "E-117": QCoreApplication.translate("pycodestyle", "over-indented"),
    "E-121": QCoreApplication.translate(
        "pycodestyle", "continuation line indentation is not a multiple of four"
    ),
    "E-122": QCoreApplication.translate(
        "pycodestyle", "continuation line missing indentation or outdented"
    ),
    "E-123": QCoreApplication.translate(
        "pycodestyle",
        "closing bracket does not match indentation of opening bracket's line",
    ),
    "E-124": QCoreApplication.translate(
        "pycodestyle", "closing bracket does not match visual indentation"
    ),
    "E-125": QCoreApplication.translate(
        "pycodestyle", "continuation line with same indent as next logical line"
    ),
    "E-126": QCoreApplication.translate(
        "pycodestyle", "continuation line over-indented for hanging indent"
    ),
    "E-127": QCoreApplication.translate(
        "pycodestyle", "continuation line over-indented for visual indent"
    ),
    "E-128": QCoreApplication.translate(
        "pycodestyle", "continuation line under-indented for visual indent"
    ),
    "E-129": QCoreApplication.translate(
        "pycodestyle", "visually indented line with same indent as next logical line"
    ),
    "E-131": QCoreApplication.translate(
        "pycodestyle", "continuation line unaligned for hanging indent"
    ),
    "E-133": QCoreApplication.translate(
        "pycodestyle", "closing bracket is missing indentation"
    ),
    "E-201": QCoreApplication.translate("pycodestyle", "whitespace after '{0}'"),
    "E-202": QCoreApplication.translate("pycodestyle", "whitespace before '{0}'"),
    "E-203": QCoreApplication.translate("pycodestyle", "whitespace before '{0}'"),
    "E-204": QCoreApplication.translate(
        "pycodestyle", "whitespace after decorator '@'"
    ),
    "E-211": QCoreApplication.translate("pycodestyle", "whitespace before '{0}'"),
    "E-221": QCoreApplication.translate(
        "pycodestyle", "multiple spaces before operator"
    ),
    "E-222": QCoreApplication.translate(
        "pycodestyle", "multiple spaces after operator"
    ),
    "E-223": QCoreApplication.translate("pycodestyle", "tab before operator"),
    "E-224": QCoreApplication.translate("pycodestyle", "tab after operator"),
    "E-225": QCoreApplication.translate(
        "pycodestyle", "missing whitespace around operator"
    ),
    "E-226": QCoreApplication.translate(
        "pycodestyle", "missing whitespace around arithmetic operator"
    ),
    "E-227": QCoreApplication.translate(
        "pycodestyle", "missing whitespace around bitwise or shift operator"
    ),
    "E-228": QCoreApplication.translate(
        "pycodestyle", "missing whitespace around modulo operator"
    ),
    "E-231": QCoreApplication.translate(
        "pycodestyle", "missing whitespace after '{0}'"
    ),
    "E-241": QCoreApplication.translate("pycodestyle", "multiple spaces after '{0}'"),
    "E-242": QCoreApplication.translate("pycodestyle", "tab after '{0}'"),
    "E-251": QCoreApplication.translate(
        "pycodestyle", "unexpected spaces around keyword / parameter equals"
    ),
    "E-252": QCoreApplication.translate(
        "pycodestyle", "missing whitespace around parameter equals"
    ),
    "E-261": QCoreApplication.translate(
        "pycodestyle", "at least two spaces before inline comment"
    ),
    "E-262": QCoreApplication.translate(
        "pycodestyle", "inline comment should start with '# '"
    ),
    "E-265": QCoreApplication.translate(
        "pycodestyle", "block comment should start with '# '"
    ),
    "E-266": QCoreApplication.translate(
        "pycodestyle", "too many leading '#' for block comment"
    ),
    "E-271": QCoreApplication.translate("pycodestyle", "multiple spaces after keyword"),
    "E-272": QCoreApplication.translate(
        "pycodestyle", "multiple spaces before keyword"
    ),
    "E-273": QCoreApplication.translate("pycodestyle", "tab after keyword"),
    "E-274": QCoreApplication.translate("pycodestyle", "tab before keyword"),
    "E-275": QCoreApplication.translate(
        "pycodestyle", "missing whitespace after keyword"
    ),
    "E-301": QCoreApplication.translate(
        "pycodestyle", "expected {0} blank lines, found {1}"
    ),
    "E-302": QCoreApplication.translate(
        "pycodestyle", "expected {0} blank lines, found {1}"
    ),
    "E-303": QCoreApplication.translate(
        "pycodestyle", "too many blank lines ({0}), expected {1}"
    ),
    "E-304": QCoreApplication.translate(
        "pycodestyle", "blank lines found after function decorator"
    ),
    "E-305": QCoreApplication.translate(
        "pycodestyle",
        "expected {0} blank lines after class or function definition, found {1}",
    ),
    "E-306": QCoreApplication.translate(
        "pycodestyle", "expected {0} blank lines before a nested definition, found {1}"
    ),
    "E-307": QCoreApplication.translate(
        "pycodestyle",
        "too many blank lines ({0}) before a nested definition, expected {1}",
    ),
    "E-308": QCoreApplication.translate("pycodestyle", "too many blank lines ({0})"),
    "E-401": QCoreApplication.translate("pycodestyle", "multiple imports on one line"),
    "E-402": QCoreApplication.translate(
        "pycodestyle", "module level import not at top of file"
    ),
    "E-501": QCoreApplication.translate(
        "pycodestyle", "line too long ({0} > {1} characters)"
    ),
    "E-502": QCoreApplication.translate(
        "pycodestyle", "the backslash is redundant between brackets"
    ),
    "E-701": QCoreApplication.translate(
        "pycodestyle", "multiple statements on one line (colon)"
    ),
    "E-702": QCoreApplication.translate(
        "pycodestyle", "multiple statements on one line (semicolon)"
    ),
    "E-703": QCoreApplication.translate(
        "pycodestyle", "statement ends with a semicolon"
    ),
    "E-704": QCoreApplication.translate(
        "pycodestyle", "multiple statements on one line (def)"
    ),
    "E-711": QCoreApplication.translate(
        "pycodestyle", "comparison to {0} should be {1}"
    ),
    "E-712": QCoreApplication.translate(
        "pycodestyle", "comparison to {0} should be {1}"
    ),
    "E-713": QCoreApplication.translate(
        "pycodestyle", "test for membership should be 'not in'"
    ),
    "E-714": QCoreApplication.translate(
        "pycodestyle", "test for object identity should be 'is not'"
    ),
    "E-721": QCoreApplication.translate(
        "pycodestyle",
        "do not compare types, for exact checks use 'is' / 'is not', "
        "for instance checks use 'isinstance()'",
    ),
    "E-722": QCoreApplication.translate("pycodestyle", "do not use bare except"),
    "E-731": QCoreApplication.translate(
        "pycodestyle", "do not assign a lambda expression, use a def"
    ),
    "E-741": QCoreApplication.translate("pycodestyle", "ambiguous variable name '{0}'"),
    "E-742": QCoreApplication.translate(
        "pycodestyle", "ambiguous class definition '{0}'"
    ),
    "E-743": QCoreApplication.translate(
        "pycodestyle", "ambiguous function definition '{0}'"
    ),
    "E-901": QCoreApplication.translate("pycodestyle", "{0}: {1}"),
    "E-902": QCoreApplication.translate("pycodestyle", "{0}"),
}

##################################################################
## pycodestyle warning messages
##################################################################

_pycodestyleWarningMessages = {
    "W-191": QCoreApplication.translate("pycodestyle", "indentation contains tabs"),
    "W-291": QCoreApplication.translate("pycodestyle", "trailing whitespace"),
    "W-292": QCoreApplication.translate("pycodestyle", "no newline at end of file"),
    "W-293": QCoreApplication.translate(
        "pycodestyle", "blank line contains whitespace"
    ),
    "W-391": QCoreApplication.translate("pycodestyle", "blank line at end of file"),
    "W-503": QCoreApplication.translate(
        "pycodestyle", "line break before binary operator"
    ),
    "W-504": QCoreApplication.translate(
        "pycodestyle", "line break after binary operator"
    ),
    "W-505": QCoreApplication.translate(
        "pycodestyle", "doc line too long ({0} > {1} characters)"
    ),
    "W-605": QCoreApplication.translate(
        "pycodestyle", "invalid escape sequence '\\{0}'"
    ),
    "W-606": QCoreApplication.translate(
        "pycodestyle",
        "'async' and 'await' are reserved keywords starting with Python 3.7",
    ),
}

##################################################################
## CodeStyleFixer messages
##################################################################

_fixMessages = {
    "FIX-D111": QCoreApplication.translate(
        "CodeStyleFixer", "Triple single quotes converted to triple double quotes."
    ),
    "FIX-D112": QCoreApplication.translate(
        "CodeStyleFixer", 'Introductory quotes corrected to be {0}"""'
    ),
    "FIX-D121": QCoreApplication.translate(
        "CodeStyleFixer", "Single line docstring put on one line."
    ),
    "FIX-D131": QCoreApplication.translate(
        "CodeStyleFixer", "Period added to summary line."
    ),
    "FIX-D141": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line before function/method docstring removed."
    ),
    "FIX-D142": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line inserted before class docstring."
    ),
    "FIX-D143": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line inserted after class docstring."
    ),
    "FIX-D144": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line inserted after docstring summary."
    ),
    "FIX-D145": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line inserted after last paragraph of docstring."
    ),
    "FIX-D221": QCoreApplication.translate(
        "CodeStyleFixer", "Leading quotes put on separate line."
    ),
    "FIX-D222": QCoreApplication.translate(
        "CodeStyleFixer", "Trailing quotes put on separate line."
    ),
    "FIX-D242": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line before class docstring removed."
    ),
    "FIX-D244": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line before function/method docstring removed."
    ),
    "FIX-D243": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line after class docstring removed."
    ),
    "FIX-D245": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line after function/method docstring removed."
    ),
    "FIX-D247": QCoreApplication.translate(
        "CodeStyleFixer", "Blank line after last paragraph removed."
    ),
    "FIX-E101": QCoreApplication.translate(
        "CodeStyleFixer", "Tab converted to 4 spaces."
    ),
    "FIX-E111": QCoreApplication.translate(
        "CodeStyleFixer", "Indentation adjusted to be a multiple of four."
    ),
    "FIX-E121": QCoreApplication.translate(
        "CodeStyleFixer", "Indentation of continuation line corrected."
    ),
    "FIX-E124": QCoreApplication.translate(
        "CodeStyleFixer", "Indentation of closing bracket corrected."
    ),
    "FIX-E122": QCoreApplication.translate(
        "CodeStyleFixer", "Missing indentation of continuation line corrected."
    ),
    "FIX-E123": QCoreApplication.translate(
        "CodeStyleFixer", "Closing bracket aligned to opening bracket."
    ),
    "FIX-E125": QCoreApplication.translate(
        "CodeStyleFixer", "Indentation level changed."
    ),
    "FIX-E126": QCoreApplication.translate(
        "CodeStyleFixer", "Indentation level of hanging indentation changed."
    ),
    "FIX-E127": QCoreApplication.translate(
        "CodeStyleFixer", "Visual indentation corrected."
    ),
    "FIX-E201": QCoreApplication.translate(
        "CodeStyleFixer", "Extraneous whitespace removed."
    ),
    "FIX-E225": QCoreApplication.translate(
        "CodeStyleFixer", "Missing whitespace added."
    ),
    "FIX-E221": QCoreApplication.translate(
        "CodeStyleFixer", "Extraneous whitespace removed."
    ),
    "FIX-E231": QCoreApplication.translate(
        "CodeStyleFixer", "Missing whitespace added."
    ),
    "FIX-E251": QCoreApplication.translate(
        "CodeStyleFixer", "Extraneous whitespace removed."
    ),
    "FIX-E261": QCoreApplication.translate(
        "CodeStyleFixer", "Whitespace around comment sign corrected."
    ),
    "FIX-E302+": lambda n=1: QCoreApplication.translate(
        "CodeStyleFixer", "%n blank line(s) inserted.", "", n
    ),
    "FIX-E302-": lambda n=1: QCoreApplication.translate(
        "CodeStyleFixer", "%n superfluous lines removed", "", n
    ),
    "FIX-E303": QCoreApplication.translate(
        "CodeStyleFixer", "Superfluous blank lines removed."
    ),
    "FIX-E304": QCoreApplication.translate(
        "CodeStyleFixer", "Superfluous blank lines after function decorator removed."
    ),
    "FIX-E401": QCoreApplication.translate(
        "CodeStyleFixer", "Imports were put on separate lines."
    ),
    "FIX-E-501": QCoreApplication.translate(
        "CodeStyleFixer", "Long lines have been shortened."
    ),
    "FIX-E502": QCoreApplication.translate(
        "CodeStyleFixer", "Redundant backslash in brackets removed."
    ),
    "FIX-E701": QCoreApplication.translate(
        "CodeStyleFixer", "Compound statement corrected."
    ),
    "FIX-E702": QCoreApplication.translate(
        "CodeStyleFixer", "Compound statement corrected."
    ),
    "FIX-E711": QCoreApplication.translate(
        "CodeStyleFixer", "Comparison to None/True/False corrected."
    ),
    "FIX-N804": QCoreApplication.translate("CodeStyleFixer", "'{0}' argument added."),
    "FIX-N806": QCoreApplication.translate("CodeStyleFixer", "'{0}' argument removed."),
    "FIX-W291": QCoreApplication.translate(
        "CodeStyleFixer", "Whitespace stripped from end of line."
    ),
    "FIX-W292": QCoreApplication.translate(
        "CodeStyleFixer", "newline added to end of file."
    ),
    "FIX-W391": QCoreApplication.translate(
        "CodeStyleFixer", "Superfluous trailing blank lines removed from end of file."
    ),
    "FIX-W603": QCoreApplication.translate("CodeStyleFixer", "'<>' replaced by '!='."),
    "FIX-WRITE_ERROR": QCoreApplication.translate(
        "CodeStyleFixer", "Could not save the file! Skipping it. Reason: {0}"
    ),
}

_pycodestyleErrorMessagesSampleArgs = {
    "E-201": ["([{"],
    "E-202": ["}])"],
    "E-203": [",;:"],
    "E-211": ["(["],
    "E-231": [",;:"],
    "E-241": [",;:"],
    "E-242": [",;:"],
    "E-301": [1, 0],
    "E-302": [2, 1],
    "E-303": [3, 2],
    "E-305": [2, 1],
    "E-306": [1, 0],
    "E-307": [3, 1],
    "E-308": [3],
    "E-501": [95, 88],
    "E-711": ["None", "'if cond is None:'"],
    "E-712": ["True", "'if cond is True:' or 'if cond:'"],
    "E-741": ["l"],
    "E-742": ["l"],
    "E-743": ["l"],
    "E-901": ["SyntaxError", "Invalid Syntax"],
    "E-902": ["OSError"],
}

_pycodestyleWarningMessagesSampleArgs = {
    "W-505": [80, 72],
    "W-605": ["A"],
}

_fixMessagesSampleArgs = {
    "FIX-WRITE_ERROR": ["OSError"],
}

messageCatalogs = {
    "A": _annotationsMessages,
    "ASY": _asyncMessages,
    "C": _complexityMessages,
    "D": _docStyleMessages,
    "E": _pycodestyleErrorMessages,
    "I": _importsMessages,
    "L": _loggingMessages,
    "M": _miscellaneousMessages,
    "N": _namingStyleMessages,
    "NO": _nameOrderMessages,
    "P": _pathlibMessages,
    "PYD": _pydanticMessages,
    "S": _securityMessages,
    "U": _unusedMessages,
    "W": _pycodestyleWarningMessages,
    "Y": _simplifyMessages,
    "FIX": _fixMessages,
}

messageSampleArgsCatalog = {
    "A": _annotationsMessagesSampleArgs,
    "ASY": _asyncMessageSampleArgs,
    "C": _complexityMessagesSampleArgs,
    "D": _docStyleMessagesSampleArgs,
    "E": _pycodestyleErrorMessagesSampleArgs,
    "I": _importsMessagesSampleArgs,
    "L": _loggingMessagesSampleArgs,
    "M": _miscellaneousMessagesSampleArgs,
    "NO": _nameOrderMessagesSampleArgs,
    "S": _securityMessagesSampleArgs,
    "U": _unusedMessagesSampleArgs,
    "W": _pycodestyleWarningMessagesSampleArgs,
    "Y": _simplifyMessagesSampleArgs,
    "FIX": _fixMessagesSampleArgs,
}

messageCategoryRe = re.compile(r"([A-Z]{1,3}).+")
# message category is max. 3 characters


def getTranslatedMessage(messageCode, messageArgs, example=False):
    """
    Module function to get a translated and formatted message for a
    given message ID.

    @param messageCode the message code
    @type str
    @param messageArgs list of arguments or a single integer value to format
        the message
    @type list or int
    @param example flag indicating a translated message filled with example
        data is requested (messageArgs is ignored if given)
    @type bool
    @return translated and formatted message
    @rtype str
    """
    match = messageCategoryRe.match(messageCode)
    if match:
        # the message code is OK
        messageCategory = match.group(1)

        if example:
            try:
                argsCatalog = messageSampleArgsCatalog[messageCategory]
                try:
                    args = argsCatalog[messageCode]
                except KeyError:
                    args = None
            except KeyError:
                args = None
        else:
            args = messageArgs

        with contextlib.suppress(KeyError):
            catalog = messageCatalogs[messageCategory]
            with contextlib.suppress(KeyError):
                message = catalog[messageCode]
                if args is None:
                    return message
                elif isinstance(args, int):
                    # Retranslate with correct plural form
                    return message(args)
                else:
                    return message.format(*args)

    if example:
        return None
    else:
        return QCoreApplication.translate(
            "CodeStyleChecker", "No message defined for code '{0}'."
        ).format(messageCode)


def getMessageCodes():
    """
    Module function to get a list of known message codes.

    @return list of known message codes
    @rtype set of str
    """
    knownCodes = []
    for catalog in messageCatalogs.values():
        knownCodes += list(catalog)
    return {c.split(".", 1)[0] for c in knownCodes}


#
# eflag: noqa = M201
