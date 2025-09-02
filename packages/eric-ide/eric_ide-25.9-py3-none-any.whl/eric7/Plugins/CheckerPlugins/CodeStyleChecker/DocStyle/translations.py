# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(code documentation part).
"""

from PyQt6.QtCore import QCoreApplication

_docStyleMessages = {
    "D-101": QCoreApplication.translate(
        "DocStyleChecker", "module is missing a docstring"
    ),
    "D-102": QCoreApplication.translate(
        "DocStyleChecker", "public function/method is missing a docstring"
    ),
    "D-103": QCoreApplication.translate(
        "DocStyleChecker", "private function/method may be missing a docstring"
    ),
    "D-104": QCoreApplication.translate(
        "DocStyleChecker", "public class is missing a docstring"
    ),
    "D-105": QCoreApplication.translate(
        "DocStyleChecker", "private class may be missing a docstring"
    ),
    "D-111": QCoreApplication.translate(
        "DocStyleChecker", 'docstring not surrounded by """'
    ),
    "D-112": QCoreApplication.translate(
        "DocStyleChecker", 'docstring containing \\ not surrounded by r"""'
    ),
    "D-121": QCoreApplication.translate(
        "DocStyleChecker", "one-liner docstring on multiple lines"
    ),
    "D-122": QCoreApplication.translate(
        "DocStyleChecker", "docstring has wrong indentation"
    ),
    "D-130": QCoreApplication.translate(
        "DocStyleChecker", "docstring does not contain a summary"
    ),
    "D-131": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not end with a period"
    ),
    "D-132": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary is not in imperative mood (Does instead of Do)",
    ),
    "D-133": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring summary looks like a function's/method's signature",
    ),
    "D-134": QCoreApplication.translate(
        "DocStyleChecker", "docstring does not mention the return value type"
    ),
    "D-141": QCoreApplication.translate(
        "DocStyleChecker", "function/method docstring is separated by a blank line"
    ),
    "D-142": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is not preceded by a blank line"
    ),
    "D-143": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is not followed by a blank line"
    ),
    "D-144": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary is not followed by a blank line"
    ),
    "D-145": QCoreApplication.translate(
        "DocStyleChecker", "last paragraph of docstring is not followed by a blank line"
    ),
    "D-201": QCoreApplication.translate(
        "DocStyleChecker", "module docstring is still a default string"
    ),
    "D-202.1": QCoreApplication.translate(
        "DocStyleChecker", "function docstring is still a default string"
    ),
    "D-202.2": QCoreApplication.translate(
        "DocStyleChecker", "function docstring still contains some placeholders"
    ),
    "D-203": QCoreApplication.translate(
        "DocStyleChecker", "private function/method is missing a docstring"
    ),
    "D-205": QCoreApplication.translate(
        "DocStyleChecker", "private class is missing a docstring"
    ),
    "D-206": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is still a default string"
    ),
    "D-221": QCoreApplication.translate(
        "DocStyleChecker", "leading quotes of docstring not on separate line"
    ),
    "D-222": QCoreApplication.translate(
        "DocStyleChecker", "trailing quotes of docstring not on separate line"
    ),
    "D-231": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not end with a period"
    ),
    "D-232": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary does not start with '{0}'"
    ),
    "D-234r": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @return line but function/method"
        " returns something",
    ),
    "D-235r": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @return line but function/method doesn't"
        " return anything",
    ),
    "D-234y": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @yield line but function/method"
        " yields something",
    ),
    "D-235y": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @yield line but function/method doesn't"
        " yield anything",
    ),
    "D-236": QCoreApplication.translate(
        "DocStyleChecker", "docstring does not contain enough @param/@keyparam lines"
    ),
    "D-237": QCoreApplication.translate(
        "DocStyleChecker", "docstring contains too many @param/@keyparam lines"
    ),
    "D-238": QCoreApplication.translate(
        "DocStyleChecker",
        "keyword only arguments must be documented with @keyparam lines",
    ),
    "D-239": QCoreApplication.translate(
        "DocStyleChecker",
        "order of @param/@keyparam lines does"
        " not match the function/method signature",
    ),
    "D-242": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is preceded by a blank line"
    ),
    "D-243": QCoreApplication.translate(
        "DocStyleChecker", "class docstring is followed by a blank line"
    ),
    "D-244": QCoreApplication.translate(
        "DocStyleChecker", "function/method docstring is preceded by a blank line"
    ),
    "D-245": QCoreApplication.translate(
        "DocStyleChecker", "function/method docstring is followed by a blank line"
    ),
    "D-246": QCoreApplication.translate(
        "DocStyleChecker", "docstring summary is not followed by a blank line"
    ),
    "D-247": QCoreApplication.translate(
        "DocStyleChecker", "last paragraph of docstring is followed by a blank line"
    ),
    "D-250": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @exception line but function/method"
        " raises an exception",
    ),
    "D-251": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @exception line but function/method doesn't"
        " raise an exception",
    ),
    "D-252": QCoreApplication.translate(
        "DocStyleChecker", "raised exception '{0}' is not documented in docstring"
    ),
    "D-253": QCoreApplication.translate(
        "DocStyleChecker", "documented exception '{0}' is not raised"
    ),
    "D-260": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring does not contain a @signal line but class defines signals",
    ),
    "D-261": QCoreApplication.translate(
        "DocStyleChecker",
        "docstring contains a @signal line but class doesn't define signals",
    ),
    "D-262": QCoreApplication.translate(
        "DocStyleChecker", "defined signal '{0}' is not documented in docstring"
    ),
    "D-263": QCoreApplication.translate(
        "DocStyleChecker", "documented signal '{0}' is not defined"
    ),
    "D-270": QCoreApplication.translate(
        "DocStyleChecker", "'{0}' line should be followed by an '{1}' line"
    ),
    "D-271": QCoreApplication.translate(
        "DocStyleChecker", "'{0}' line should not be preceded by an empty line"
    ),
    "D-272": QCoreApplication.translate(
        "DocStyleChecker", "don't use '{0}' but '{1}' instead"
    ),
    "D-273": QCoreApplication.translate(
        "DocStyleChecker", "'{0}' line has wrong indentation"
    ),
}

_docStyleMessagesSampleArgs = {
    "D-232": ["public"],
    "D-252": ["RuntimeError"],
    "D-253": ["RuntimeError"],
    "D-262": ["buttonClicked"],
    "D-263": ["buttonClicked"],
    "D-270": ["@param", "@type"],
    "D-271": ["@type"],
    "D-272": ["@ptype", "@type"],
    "D-273": ["@type"],
}
