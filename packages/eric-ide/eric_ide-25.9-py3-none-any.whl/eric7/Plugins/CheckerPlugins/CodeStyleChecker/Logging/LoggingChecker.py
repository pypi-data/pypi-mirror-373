# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for logging related issues.
"""

from CodeStyleTopicChecker import CodeStyleTopicChecker


class LoggingChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for logging related issues.
    """

    Codes = [
        ## Logging
        "L-101",
        "L-102",
        "L-103",
        "L-104",
        "L-105",
        "L-106",
        "L-107",
        "L-108",
        "L-109",
        "L-110",
        "L-111",
        "L-112",
        "L-113",
        "L-114",
        "L-115",
    ]
    Category = "L"

    def __init__(self, source, filename, tree, select, ignore, expected, repeat, args):
        """
        Constructor

        @param source source code to be checked
        @type list of str
        @param filename name of the source file
        @type str
        @param tree AST tree of the source code
        @type ast.Module
        @param select list of selected codes
        @type list of str
        @param ignore list of codes to be ignored
        @type list of str
        @param expected list of expected codes
        @type list of str
        @param repeat flag indicating to report each occurrence of a code
        @type bool
        @param args dictionary of arguments for the various checks
        @type dict
        """
        super().__init__(
            LoggingChecker.Category,
            source,
            filename,
            tree,
            select,
            ignore,
            expected,
            repeat,
            args,
        )

        checkersWithCodes = [
            (
                self.__checkLogging,
                (
                    "L-101",
                    "L-102",
                    "L-103",
                    "L-104",
                    "L-105",
                    "L-106",
                    "L-107",
                    "L-108",
                    "L-109",
                    "L-110",
                    "L-111",
                    "L-112",
                    "L-113",
                    "L-114",
                    "L-115",
                ),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkLogging(self):
        """
        Private method to check logging statements.
        """
        from .LoggingVisitor import LoggingVisitor

        visitor = LoggingVisitor(errorCallback=self.addErrorFromNode)
        visitor.visit(self.tree)
