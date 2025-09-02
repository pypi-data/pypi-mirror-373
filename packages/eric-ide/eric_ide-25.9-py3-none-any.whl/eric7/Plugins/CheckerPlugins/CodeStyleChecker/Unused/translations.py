# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin (unused part).
"""

from PyQt6.QtCore import QCoreApplication

_unusedMessages = {
    ## Unused Arguments
    "U-100": QCoreApplication.translate("UnusedChecker", "Unused argument '{0}'"),
    "U-101": QCoreApplication.translate("UnusedChecker", "Unused argument '{0}'"),
    ## Unused Globals
    "U-200": QCoreApplication.translate(
        "UnusedChecker", "Unused global variable '{0}'"
    ),
}

_unusedMessagesSampleArgs = {
    ## Unused Arguments
    "U-100": ["foo_arg"],
    "U-101": ["_bar_arg"],
    ## Unused Globals
    "U-200": ["FOO"],
}
