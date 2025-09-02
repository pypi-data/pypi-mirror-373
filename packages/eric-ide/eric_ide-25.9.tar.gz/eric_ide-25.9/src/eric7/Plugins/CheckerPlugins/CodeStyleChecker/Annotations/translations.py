# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(code annotations part).
"""

from PyQt6.QtCore import QCoreApplication

_annotationsMessages = {
    "A-001": QCoreApplication.translate(
        "AnnotationsChecker", "missing type annotation for function argument '{0}'"
    ),
    "A-002": QCoreApplication.translate(
        "AnnotationsChecker", "missing type annotation for '*{0}'"
    ),
    "A-003": QCoreApplication.translate(
        "AnnotationsChecker", "missing type annotation for '**{0}'"
    ),
    "A-101": QCoreApplication.translate(
        "AnnotationsChecker", "missing type annotation for 'self' in method"
    ),
    "A-102": QCoreApplication.translate(
        "AnnotationsChecker", "missing type annotation for 'cls' in classmethod"
    ),
    "A-201": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for public function"
    ),
    "A-202": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for protected function"
    ),
    "A-203": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for private function"
    ),
    "A-204": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for special method"
    ),
    "A-205": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for staticmethod"
    ),
    "A-206": QCoreApplication.translate(
        "AnnotationsChecker", "missing return type annotation for classmethod"
    ),
    "A-401": QCoreApplication.translate(
        "AnnotationsChecker",
        "Dynamically typed expressions (typing.Any) are disallowed",
    ),
    "A-402": QCoreApplication.translate(
        "AnnotationsChecker", "Type comments are disallowed"
    ),
    "A-871": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing 'from __future__ import annotations' but imports: {0}",
    ),
    "A-872": QCoreApplication.translate(
        "AnnotationsChecker", "missing 'from __future__ import annotations'"
    ),
    "A-873": QCoreApplication.translate(
        "AnnotationsChecker",
        "missing 'from __future__ import annotations' but uses simplified type"
        " annotations: {0}",
    ),
    "A-881": QCoreApplication.translate(
        "AnnotationsChecker", "type annotation coverage of {0}% is too low"
    ),
    "A-891": QCoreApplication.translate(
        "AnnotationsChecker", "type annotation is too complex ({0} > {1})"
    ),
    "A-892": QCoreApplication.translate(
        "AnnotationsChecker", "type annotation is too long ({0} > {1})"
    ),
    "A-901": QCoreApplication.translate(
        "AnnotationsChecker",
        "'typing.Union' is deprecated, use '|' instead (see PEP 604)",
    ),
    "A-911": QCoreApplication.translate(
        "AnnotationsChecker",
        "'typing.{0}' is deprecated, use '{1}' instead (see PEP 585)",
    ),
}

_annotationsMessagesSampleArgs = {
    "A-001": ["arg1"],
    "A-002": ["args"],
    "A-003": ["kwargs"],
    "A-871": ["Dict, List"],
    "A-873": ["dict, list"],
    "A-881": [60],
    "A-891": [5, 3],
    "A-892": [10, 7],
    "A-911": ["List", "list"],
}
