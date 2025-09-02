# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check the use of sys.version and sys.version_info.
"""

import ast

import AstUtilities


class SysVersionVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check the use of sys.version and
    sys.version_info.

    Note: This class is modeled after flake8-2020 v1.8.1.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.violations = []
        self.__fromImports = {}

    def visit_ImportFrom(self, node):
        """
        Public method to handle a from ... import ... statement.

        @param node reference to the node to be processed
        @type ast.ImportFrom
        """
        for alias in node.names:
            if node.module is not None and not alias.asname:
                self.__fromImports[alias.name] = node.module

        self.generic_visit(node)

    def __isSys(self, attr, node):
        """
        Private method to check for a reference to sys attribute.

        @param attr attribute name
        @type str
        @param node reference to the node to be checked
        @type ast.Node
        @return flag indicating a match
        @rtype bool
        """
        match = False
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "sys"
            and node.attr == attr
        ) or (
            isinstance(node, ast.Name)
            and node.id == attr
            and self.__fromImports.get(node.id) == "sys"
        ):
            match = True

        return match

    def __isSysVersionUpperSlice(self, node, n):
        """
        Private method to check the upper slice of sys.version.

        @param node reference to the node to be checked
        @type ast.Node
        @param n slice value to check against
        @type int
        @return flag indicating a match
        @rtype bool
        """
        return (
            self.__isSys("version", node.value)
            and isinstance(node.slice, ast.Slice)
            and node.slice.lower is None
            and AstUtilities.isNumber(node.slice.upper)
            and AstUtilities.getValue(node.slice.upper) == n
            and node.slice.step is None
        )

    def visit_Subscript(self, node):
        """
        Public method to handle a subscript.

        @param node reference to the node to be processed
        @type ast.Subscript
        """
        if self.__isSysVersionUpperSlice(node, 1):
            self.violations.append((node.value, "M-423"))
        elif self.__isSysVersionUpperSlice(node, 3):
            self.violations.append((node.value, "M-401"))
        elif (
            self.__isSys("version", node.value)
            and isinstance(node.slice, ast.Index)
            and AstUtilities.isNumber(node.slice.value)
            and AstUtilities.getValue(node.slice.value) == 2
        ):
            self.violations.append((node.value, "M-402"))
        elif (
            self.__isSys("version", node.value)
            and isinstance(node.slice, ast.Index)
            and AstUtilities.isNumber(node.slice.value)
            and AstUtilities.getValue(node.slice.value) == 0
        ):
            self.violations.append((node.value, "M-421"))

        self.generic_visit(node)

    def visit_Compare(self, node):
        """
        Public method to handle a comparison.

        @param node reference to the node to be processed
        @type ast.Compare
        """
        if (
            isinstance(node.left, ast.Subscript)
            and self.__isSys("version_info", node.left.value)
            and isinstance(node.left.slice, ast.Index)
            and AstUtilities.isNumber(node.left.slice.value)
            and AstUtilities.getValue(node.left.slice.value) == 0
            and len(node.ops) == 1
            and isinstance(node.ops[0], ast.Eq)
            and AstUtilities.isNumber(node.comparators[0])
            and AstUtilities.getValue(node.comparators[0]) == 3
        ):
            self.violations.append((node.left, "M-411"))
        elif (
            self.__isSys("version", node.left)
            and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE))
            and AstUtilities.isString(node.comparators[0])
        ):
            if len(AstUtilities.getValue(node.comparators[0])) == 1:
                errorCode = "M-422"
            else:
                errorCode = "M-403"
            self.violations.append((node.left, errorCode))
        elif (
            isinstance(node.left, ast.Subscript)
            and self.__isSys("version_info", node.left.value)
            and isinstance(node.left.slice, ast.Index)
            and AstUtilities.isNumber(node.left.slice.value)
            and AstUtilities.getValue(node.left.slice.value) == 1
            and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE))
            and AstUtilities.isNumber(node.comparators[0])
        ):
            self.violations.append((node, "M-413"))
        elif (
            isinstance(node.left, ast.Attribute)
            and self.__isSys("version_info", node.left.value)
            and node.left.attr == "minor"
            and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE))
            and AstUtilities.isNumber(node.comparators[0])
        ):
            self.violations.append((node, "M-414"))

        self.generic_visit(node)

    def visit_Attribute(self, node):
        """
        Public method to handle an attribute.

        @param node reference to the node to be processed
        @type ast.Attribute
        """
        if (
            isinstance(node.value, ast.Name)
            and node.value.id == "six"
            and node.attr == "PY3"
        ):
            self.violations.append((node, "M-412"))

        self.generic_visit(node)

    def visit_Name(self, node):
        """
        Public method to handle an name.

        @param node reference to the node to be processed
        @type ast.Name
        """
        if node.id == "PY3" and self.__fromImports.get(node.id) == "six":
            self.violations.append((node, "M-412"))

        self.generic_visit(node)
