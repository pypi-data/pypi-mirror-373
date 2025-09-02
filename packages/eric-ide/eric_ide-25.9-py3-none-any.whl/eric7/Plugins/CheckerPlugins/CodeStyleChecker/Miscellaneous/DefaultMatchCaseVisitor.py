# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check default match cases.
"""

import ast


class DefaultMatchCaseVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check default match cases.

    Note: This class is modeled after flake8-spm v0.0.1.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.violations = []

    def visit_Match(self, node):
        """
        Public method to handle Match nodes.

        @param node reference to the node to be processed
        @type ast.Match
        """
        for badNode, issueCode in self.__badNodes(node):
            self.violations.append((badNode, issueCode))

        self.generic_visit(node)

    def __badNodes(self, node):
        """
        Private method to yield bad match nodes.

        @param node reference to the node to be processed
        @type ast.Match
        @yield tuple containing a reference to bad match case node and the corresponding
            issue code
        @ytype tyuple of (ast.AST, str)
        """
        for case in node.cases:
            if self.__emptyMatchDefault(case):
                if self.__lastStatementDoesNotRaise(case):
                    yield self.__findBadNode(case), "M-901"
                elif self.__returnPrecedesExceptionRaising(case):
                    yield self.__findBadNode(case), "M-902"

    def __emptyMatchDefault(self, case):
        """
        Private method to check for an empty default match case.

        @param case reference to the node to be processed
        @type ast.match_case
        @return flag indicating an empty default match case
        @rtype bool
        """
        pattern = case.pattern
        return isinstance(pattern, ast.MatchAs) and (
            pattern.pattern is None
            or (
                isinstance(pattern.pattern, ast.MatchAs)
                and pattern.pattern.pattern is None
            )
        )

    def __lastStatementDoesNotRaise(self, case):
        """
        Private method to check that the last case statement does not raise an
        exception.

        @param case reference to the node to be processed
        @type ast.match_case
        @return flag indicating that the last case statement does not raise an
            exception
        @rtype bool
        """
        return not isinstance(case.body[-1], ast.Raise)

    def __returnPrecedesExceptionRaising(self, case):
        """
        Private method to check that no return precedes an exception raising.

        @param case reference to the node to be processed
        @type ast.match_case
        @return flag indicating that a return precedes an exception raising
        @rtype bool
        """
        returnIndex = -1
        raiseIndex = -1
        for index, body in enumerate(case.body):
            if isinstance(body, ast.Return):
                returnIndex = index
            elif isinstance(body, ast.Raise):
                raiseIndex = index
        return returnIndex >= 0 and returnIndex < raiseIndex

    def __findBadNode(self, case) -> ast.AST:
        """
        Private method returning a reference to the bad node of a case node.

        @param case reference to the node to be processed
        @type ast.match_case
        @return reference to the bad node
        @rtype ast.AST
        """
        for body in case.body:
            # Handle special case when return precedes exception raising.
            # In this case the bad node is that with the return statement.
            if isinstance(body, ast.Return):
                return body

        return case.body[-1]
