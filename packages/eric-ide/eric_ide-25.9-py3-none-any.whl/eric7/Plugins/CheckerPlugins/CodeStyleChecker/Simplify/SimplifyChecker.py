# -*- coding: utf-8 -*-

# Copyright (c) 2021 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the checker for simplifying Python code.
"""

import ast

from CodeStyleTopicChecker import CodeStyleTopicChecker

from .SimplifyNodeVisitor import SimplifyNodeVisitor


class SimplifyChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for to help simplifying Python code.
    """

    Codes = [
        # Python-specifics
        "Y-101",
        "Y-102",
        "Y-103",
        "Y-104",
        "Y-105",
        "Y-106",
        "Y-107",
        "Y-108",
        "Y-109",
        "Y-110",
        "Y-111",
        "Y-112",
        "Y-113",
        "Y-114",
        "Y-115",
        "Y-116",
        "Y-117",
        "Y-118",
        "Y-119",
        "Y-120",
        "Y-121",
        "Y-122",
        "Y-123",
        # Python-specifics not part of flake8-simplify
        "Y-181",
        "Y-182",
        # Comparations
        "Y-201",
        "Y-202",
        "Y-203",
        "Y-204",
        "Y-205",
        "Y-206",
        "Y-207",
        "Y-208",
        "Y-211",
        "Y-212",
        "Y-213",
        "Y-221",
        "Y-222",
        "Y-223",
        "Y-224",
        # Opinionated
        "Y-301",
        # General Code Style
        "Y-401",
        "Y-402",
        # f-Strings
        "Y-411",
        # Additional Checks
        "Y-901",
        "Y-904",
        "Y-905",
        "Y-906",
        "Y-907",
        "Y-909",
        "Y-910",
        "Y-911",
    ]
    Category = "Y"

    def __init__(self, source, filename, tree, selected, ignored, expected, repeat):
        """
        Constructor

        @param source source code to be checked
        @type list of str
        @param filename name of the source file
        @type str
        @param tree AST tree of the source code
        @type ast.Module
        @param selected list of selected codes
        @type list of str
        @param ignored list of codes to be ignored
        @type list of str
        @param expected list of expected codes
        @type list of str
        @param repeat flag indicating to report each occurrence of a code
        @type bool
        """
        super().__init__(
            SimplifyChecker.Category,
            source,
            filename,
            tree,
            selected,
            ignored,
            expected,
            repeat,
            [],
        )

        checkersWithCodes = [
            (
                self.__checkCodeSimplifications,
                (
                    "Y-101",
                    "Y-102",
                    "Y-103",
                    "Y-104",
                    "Y-105",
                    "Y-106",
                    "Y-107",
                    "Y-108",
                    "Y-109",
                    "Y-110",
                    "Y-111",
                    "Y-112",
                    "Y-113",
                    "Y-114",
                    "Y-115",
                    "Y-116",
                    "Y-117",
                    "Y-118",
                    "Y-119",
                    "Y-120",
                    "Y-121",
                    "Y-122",
                    "Y-123",
                    "Y-181",
                    "Y-182",
                    "Y-201",
                    "Y-202",
                    "Y-203",
                    "Y-204",
                    "Y-205",
                    "Y-206",
                    "Y-207",
                    "Y-208",
                    "Y-211",
                    "Y-212",
                    "Y-213",
                    "Y-221",
                    "Y-222",
                    "Y-223",
                    "Y-224",
                    "Y-301",
                    "Y-401",
                    "Y-402",
                    "Y-411",
                    "Y-901",
                    "Y-904",
                    "Y-905",
                    "Y-906",
                    "Y-907",
                    "Y-909",
                    "Y-910",
                    "Y-911",
                ),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkCodeSimplifications(self):
        """
        Private method to check for code simplifications.
        """
        # Add parent information
        self.__addMeta(self.tree)

        visitor = SimplifyNodeVisitor(self.addErrorFromNode)
        visitor.visit(self.tree)

    def __addMeta(self, root, level=0):
        """
        Private method to amend the nodes of the given AST tree with backward and
        forward references.

        @param root reference to the root node of the tree
        @type ast.AST
        @param level nesting level (defaults to 0)
        @type int (optional)
        """
        previousSibling = None
        for node in ast.iter_child_nodes(root):
            if level == 0:
                node.parent = root
            node.previous_sibling = previousSibling
            node.next_sibling = None
            if previousSibling:
                node.previous_sibling.next_sibling = node
            previousSibling = node
            for child in ast.iter_child_nodes(node):
                child.parent = node
            self.__addMeta(node, level=level + 1)
