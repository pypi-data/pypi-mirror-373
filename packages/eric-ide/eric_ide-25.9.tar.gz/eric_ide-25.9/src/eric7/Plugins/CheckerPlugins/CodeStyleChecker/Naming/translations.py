# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(naming part).
"""

from PyQt6.QtCore import QCoreApplication

_namingStyleMessages = {
    "N-801": QCoreApplication.translate(
        "NamingStyleChecker", "class names should use CapWords convention"
    ),
    "N-802": QCoreApplication.translate(
        "NamingStyleChecker", "function name should be lowercase"
    ),
    "N-803": QCoreApplication.translate(
        "NamingStyleChecker", "argument name should be lowercase"
    ),
    "N-804": QCoreApplication.translate(
        "NamingStyleChecker", "first argument of a class method should be named 'cls'"
    ),
    "N-805": QCoreApplication.translate(
        "NamingStyleChecker", "first argument of a method should be named 'self'"
    ),
    "N-806": QCoreApplication.translate(
        "NamingStyleChecker",
        "first argument of a static method should not be named 'self' or 'cls",
    ),
    "N-807": QCoreApplication.translate(
        "NamingStyleChecker", "module names should be lowercase"
    ),
    "N-808": QCoreApplication.translate(
        "NamingStyleChecker", "package names should be lowercase"
    ),
    "N-809": QCoreApplication.translate(
        "NamingStyleChecker", "function name should not start and end with '__'"
    ),
    "N-811": QCoreApplication.translate(
        "NamingStyleChecker", "constant imported as non constant"
    ),
    "N-812": QCoreApplication.translate(
        "NamingStyleChecker", "lowercase imported as non lowercase"
    ),
    "N-813": QCoreApplication.translate(
        "NamingStyleChecker", "camelcase imported as lowercase"
    ),
    "N-814": QCoreApplication.translate(
        "NamingStyleChecker", "camelcase imported as constant"
    ),
    "N-815": QCoreApplication.translate(
        "NamingStyleChecker", "camelcase imported as acronym"
    ),
    "N-818": QCoreApplication.translate(
        "NamingStyleChecker", "exception name should be named with an 'Error' suffix"
    ),
    "N-821": QCoreApplication.translate(
        "NamingStyleChecker", "variable in function should be lowercase"
    ),
    "N-822": QCoreApplication.translate(
        "NamingStyleChecker", "variable in class scope should not be mixed case"
    ),
    "N-823": QCoreApplication.translate(
        "NamingStyleChecker", "variable in global scope should not be mixed case"
    ),
    "N-831": QCoreApplication.translate(
        "NamingStyleChecker", "names 'l', 'O' and 'I' should be avoided"
    ),
}
