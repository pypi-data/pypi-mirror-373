# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for code complexity.
"""

import ast

from CodeStyleTopicChecker import CodeStyleTopicChecker

from .mccabe import PathGraphingAstVisitor


class ComplexityChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for code complexity.
    """

    Codes = [
        "C-101",
        "C-111",
        "C-112",
    ]
    Category = "C"

    def __init__(self, source, filename, tree, select, ignore, args):
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
        @param args dictionary of arguments for the miscellaneous checks
        @type dict
        """
        super().__init__(
            ComplexityChecker.Category,
            source,
            filename,
            tree,
            select,
            ignore,
            [],
            True,
            args,
        )

        self.__defaultArgs = {
            "McCabeComplexity": 10,
            "LineComplexity": 15,
            "LineComplexityScore": 10,
        }

        checkersWithCodes = [
            (self.__checkMcCabeComplexity, ("C-101",)),
            (self.__checkLineComplexity, ("C-111", "C-112")),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkMcCabeComplexity(self):
        """
        Private method to check the McCabe code complexity.
        """
        try:
            # create the AST again because it is modified by the checker
            tree = compile(
                "".join(self.source), self.filename, "exec", ast.PyCF_ONLY_AST
            )
        except (SyntaxError, TypeError):
            # compile errors are already reported by the run() method
            return

        maxComplexity = self.args.get(
            "McCabeComplexity", self.__defaultArgs["McCabeComplexity"]
        )

        visitor = PathGraphingAstVisitor()
        visitor.preorder(tree, visitor)
        for graph in visitor.graphs.values():
            if graph.complexity() > maxComplexity:
                self.addError(
                    graph.lineno + 1, 0, "C-101", graph.entity, graph.complexity()
                )

    def __checkLineComplexity(self):
        """
        Private method to check the complexity of a single line of code and
        the median line complexity of the source code.

        Complexity is defined as the number of AST nodes produced by a line
        of code.
        """
        maxLineComplexity = self.args.get(
            "LineComplexity", self.__defaultArgs["LineComplexity"]
        )
        maxLineComplexityScore = self.args.get(
            "LineComplexityScore", self.__defaultArgs["LineComplexityScore"]
        )

        visitor = LineComplexityVisitor()
        visitor.visit(self.tree)

        sortedItems = visitor.sortedList()
        score = visitor.score()

        for line, complexity in sortedItems:
            if complexity > maxLineComplexity:
                self.addError(line + 1, 0, "C-111", complexity)

        if score > maxLineComplexityScore:
            self.addError(1, 0, "C-112", score)


class LineComplexityVisitor(ast.NodeVisitor):
    """
    Class calculating the number of AST nodes per line of code
    and the median nodes/line score.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__count = {}

    def visit(self, node):
        """
        Public method to recursively visit all the nodes and add up the
        instructions.

        @param node reference to the node
        @type ast.AST
        """
        if hasattr(node, "lineno"):
            self.__count[node.lineno] = self.__count.get(node.lineno, 0) + 1

        self.generic_visit(node)

    def sortedList(self):
        """
        Public method to get a sorted list of (line, nodes) tuples.

        @return sorted list of (line, nodes) tuples
        @rtype list of tuple of (int,int)
        """
        lst = [(line, self.__count[line]) for line in sorted(self.__count)]
        return lst

    def score(self):
        """
        Public method to calculate the median.

        @return median line complexity value
        @rtype float
        """
        sortedList = sorted(self.__count.values())
        listLength = len(sortedList)
        medianIndex = (listLength - 1) // 2

        if listLength == 0:
            return 0.0
        elif listLength % 2:
            return float(sortedList[medianIndex])
        else:
            return (sortedList[medianIndex] + sortedList[medianIndex + 1]) / 2.0
