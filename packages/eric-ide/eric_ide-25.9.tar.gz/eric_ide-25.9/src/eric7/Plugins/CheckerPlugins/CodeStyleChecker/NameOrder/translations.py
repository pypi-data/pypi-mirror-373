# -*- coding: utf-8 -*-

# Copyright (c) 2021 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin
(name ordering part).
"""

from PyQt6.QtCore import QCoreApplication

_nameOrderMessages = {
    "NO-101": QCoreApplication.translate(
        "NameOrderChecker",
        "Import statements are in the wrong order. '{0}' should be before '{1}'",
    ),
    "NO-102": QCoreApplication.translate(
        "NameOrderChecker", "Imported names are in the wrong order. Should be '{0}'"
    ),
    "NO-103": QCoreApplication.translate(
        "NameOrderChecker",
        "Import statements should be combined. '{0}' should be combined with '{1}'",
    ),
    "NO-104": QCoreApplication.translate(
        "NameOrderChecker",
        "The names in __all__ are in the wrong order. The order should be '{0}'",
    ),
    "NO-105": QCoreApplication.translate(
        "NameOrderChecker",
        "The names in the exception handler list are in the wrong order. The order"
        " should be '{0}'",
    ),
}

_nameOrderMessagesSampleArgs = {
    "NO-101": ["import bar", "import foo"],
    "NO-102": ["bar, baz, foo"],
    "NO-103": ["from foo import bar", "from foo import baz"],
    "NO-104": ["bar, baz, foo"],
    "NO-105": ["BarError, BazError, FooError"],
}
