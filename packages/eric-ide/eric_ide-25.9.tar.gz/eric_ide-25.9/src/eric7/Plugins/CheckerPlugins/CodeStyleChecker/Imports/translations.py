# -*- coding: utf-8 -*-

# Copyright (c) 2021 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin messages
(import statements part).
"""

from PyQt6.QtCore import QCoreApplication

_importsMessages = {
    "I-101": QCoreApplication.translate(
        "ImportsChecker", "local import must be at the beginning of the method body"
    ),
    "I-102": QCoreApplication.translate(
        "ImportsChecker",
        "packages from external modules should not be imported locally",
    ),
    "I-103": QCoreApplication.translate(
        "ImportsChecker",
        "packages from standard modules should not be imported locally",
    ),
    "I-901": QCoreApplication.translate(
        "ImportsChecker", "unnecessary import alias - rewrite as '{0}'"
    ),
    "I-902": QCoreApplication.translate("ImportsChecker", "banned import '{0}' used"),
    "I-903": QCoreApplication.translate(
        "ImportsChecker", "relative imports from parent modules are banned"
    ),
    "I-904": QCoreApplication.translate(
        "ImportsChecker", "relative imports are banned"
    ),
}

_importsMessagesSampleArgs = {
    "I-901": ["from foo import bar"],
    "I-902": ["foo"],
}
