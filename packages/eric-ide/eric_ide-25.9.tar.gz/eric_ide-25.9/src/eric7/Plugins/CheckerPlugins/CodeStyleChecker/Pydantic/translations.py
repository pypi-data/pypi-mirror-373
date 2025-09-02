# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing message translations for the code style plugin messages
(pydantic part).
"""

from PyQt6.QtCore import QCoreApplication

_pydanticMessages = {
    ## pydantic
    "PYD-001": QCoreApplication.translate(
        "PydanticChecker",
        "positional argument for Field default argument",
    ),
    "PYD-002": QCoreApplication.translate(
        "PydanticChecker",
        "non-annotated attribute inside Pydantic model",
    ),
    "PYD-003": QCoreApplication.translate(
        "PydanticChecker",
        "unecessary Field call to specify a default value",
    ),
    "PYD-004": QCoreApplication.translate(
        "PydanticChecker",
        "default argument specified in annotated",
    ),
    "PYD-005": QCoreApplication.translate(
        "PydanticChecker",
        "field name overrides annotation",
    ),
    "PYD-006": QCoreApplication.translate(
        "PydanticChecker",
        "duplicate field name",
    ),
    "PYD-010": QCoreApplication.translate(
        "PydanticChecker",
        "usage of __pydantic_config__; consider using the `with_config` decorator",
    ),
}
