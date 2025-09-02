# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(logging part).
"""

from PyQt6.QtCore import QCoreApplication

_loggingMessages = {
    ## Logging
    "L-101": QCoreApplication.translate(
        "LoggingChecker",
        "use logging.getLogger() to instantiate loggers",
    ),
    "L-102": QCoreApplication.translate(
        "LoggingChecker",
        "use '__name__' with getLogger()",
    ),
    "L-103": QCoreApplication.translate(
        "LoggingChecker",
        "extra key {0} clashes with LogRecord attribute",
    ),
    "L-104": QCoreApplication.translate(
        "LoggingChecker",
        "avoid exception() outside of exception handlers",
    ),
    "L-105": QCoreApplication.translate(
        "LoggingChecker",
        ".exception(...) should be used instead of .error(..., exc_info=True)",
    ),
    "L-106": QCoreApplication.translate(
        "LoggingChecker",
        "redundant exc_info argument for exception() should be removed",
    ),
    "L-107": QCoreApplication.translate(
        "LoggingChecker",
        "use error() instead of exception() with exc_info=False",
    ),
    "L-108": QCoreApplication.translate(
        "LoggingChecker",
        "warn() is deprecated, use warning() instead",
    ),
    "L-109": QCoreApplication.translate(
        "LoggingChecker",
        "WARN is undocumented, use WARNING instead",
    ),
    "L-110": QCoreApplication.translate(
        "LoggingChecker",
        "exception() does not take an exception",
    ),
    "L-111a": QCoreApplication.translate(
        "LoggingChecker",
        "avoid pre-formatting log messages using f-string",
    ),
    "L-111b": QCoreApplication.translate(
        "LoggingChecker",
        "avoid pre-formatting log messages using string.format()",
    ),
    "L-111c": QCoreApplication.translate(
        "LoggingChecker",
        "avoid pre-formatting log messages using '%'",  # noqa: M-601
    ),
    "L-111d": QCoreApplication.translate(
        "LoggingChecker",
        "avoid pre-formatting log messages using '+'",
    ),
    "L-112": QCoreApplication.translate(
        "LoggingChecker",
        "formatting error: {0} {1} placeholder(s) but {2} argument(s)",
    ),
    "L-113a": QCoreApplication.translate(
        "LoggingChecker",
        "formatting error: missing key(s): {0}",
    ),
    "L-113b": QCoreApplication.translate(
        "LoggingChecker",
        "formatting error: unreferenced key(s): {0}",
    ),
    "L-114": QCoreApplication.translate(
        "LoggingChecker",
        "avoid exc_info=True outside of exception handlers",
    ),
    "L-115": QCoreApplication.translate(
        "LoggingChecker",
        "avoid logging calls on the root logger",
    ),
}

_loggingMessagesSampleArgs = {
    ## Logging
    "L-103": ["'pathname'"],
    "L-112": [3, "'%'", 2],  # noqa: M-601
    "L-113a": ["'foo', 'bar'"],
    "L-113b": ["'foo', 'bar'"],
}
