# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for "async" related issues.
"""

import copy

from CodeStyleTopicChecker import CodeStyleTopicChecker


class AsyncChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for "async" related issues.
    """

    Codes = [
        "ASY-100",
        "ASY-101",
        "ASY-102",
        "ASY-103",
        "ASY-104",
        "ASY-105",
    ]
    Category = "ASY"

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
            AsyncChecker.Category,
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
                self.__checkSyncUses,
                ("ASY-100", "ASY-101", "ASY-102", "ASY-103", "ASY-104", "ASY-105"),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkSyncUses(self):
        """
        Private method to check for use of synchroneous functions in async methods.
        """
        from .AsyncVisitor import AsyncVisitor

        visitor = AsyncVisitor(self.args, self)
        visitor.visit(copy.deepcopy(self.tree))
        for violation in visitor.violations:
            self.addErrorFromNode(violation[0], violation[1])
