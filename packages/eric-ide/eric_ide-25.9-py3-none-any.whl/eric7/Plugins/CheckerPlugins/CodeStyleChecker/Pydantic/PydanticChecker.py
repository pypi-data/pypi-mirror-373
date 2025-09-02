# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for pydantic related issues.
"""

from CodeStyleTopicChecker import CodeStyleTopicChecker


class PydanticChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for pydantic related issues.
    """

    Codes = [
        "PYD-001",
        "PYD-002",
        "PYD-003",
        "PYD-004",
        "PYD-005",
        "PYD-006",
        "PYD-010",
    ]
    Category = "PYD"

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
            PydanticChecker.Category,
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
                self.__checkPydantic,
                (
                    "PYD-001",
                    "PYD-002",
                    "PYD-003",
                    "PYD-004",
                    "PYD-005",
                    "PYD-006",
                    "PYD-010",
                ),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkPydantic(self):
        """
        Private method to check pydantic related topics.
        """
        from .PydanticVisitor import PydanticVisitor

        visitor = PydanticVisitor(errorCallback=self.addErrorFromNode)
        visitor.visit(self.tree)
