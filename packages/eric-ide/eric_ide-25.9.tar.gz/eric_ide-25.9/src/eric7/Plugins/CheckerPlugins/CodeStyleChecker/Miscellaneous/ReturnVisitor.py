# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check return statements.
"""

import ast

from collections import defaultdict

import AstUtilities


class ReturnVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check return statements.

    Note 1: This class is modeled after flake8-return v1.2.0 checker without
    checking for superfluous return.
    Note 2: This class is a combination of the main visitor class and the various
    mixin classes of of the above checker.
    """

    Assigns = "assigns"
    Loops = "loops"
    Refs = "refs"
    Returns = "returns"
    Tries = "tries"

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.violations = []

        self.__stack = []

    @property
    def assigns(self):
        """
        Public method to get the Assign nodes.

        @return dictionary containing the node name as key and line number
            as value
        @rtype dict
        """
        return self.__stack[-1][ReturnVisitor.Assigns]

    @property
    def refs(self):
        """
        Public method to get the References nodes.

        @return dictionary containing the node name as key and line number
            as value
        @rtype dict
        """
        return self.__stack[-1][ReturnVisitor.Refs]

    @property
    def tries(self):
        """
        Public method to get the Try nodes.

        @return dictionary containing the node name as key and line number
            as value
        @rtype dict
        """
        return self.__stack[-1][ReturnVisitor.Tries]

    @property
    def loops(self):
        """
        Public method to get the Loop nodes.

        @return dictionary containing the node name as key and line number
            as value
        @rtype dict
        """
        return self.__stack[-1][ReturnVisitor.Loops]

    @property
    def returns(self):
        """
        Public method to get the Return nodes.

        @return dictionary containing the node name as key and line number
            as value
        @rtype dict
        """
        return self.__stack[-1][ReturnVisitor.Returns]

    def visit_For(self, node):
        """
        Public method to handle a for loop.

        @param node reference to the for node to handle
        @type ast.For
        """
        self.__visitLoop(node)

    def visit_AsyncFor(self, node):
        """
        Public method to handle an async for loop.

        @param node reference to the async for node to handle
        @type ast.AsyncFor
        """
        self.__visitLoop(node)

    def visit_While(self, node):
        """
        Public method to handle a while loop.

        @param node reference to the while node to handle
        @type ast.While
        """
        self.__visitLoop(node)

    def __visitLoop(self, node):
        """
        Private method to handle loop nodes.

        @param node reference to the loop node to handle
        @type ast.For, ast.AsyncFor or ast.While
        """
        if self.__stack and hasattr(node, "end_lineno") and node.end_lineno is not None:
            self.loops[node.lineno] = node.end_lineno

        self.generic_visit(node)

    def __visitWithStack(self, node):
        """
        Private method to traverse a given function node using a stack.

        @param node AST node to be traversed
        @type ast.FunctionDef or ast.AsyncFunctionDef
        """
        self.__stack.append(
            {
                ReturnVisitor.Assigns: defaultdict(list),
                ReturnVisitor.Refs: defaultdict(list),
                ReturnVisitor.Loops: defaultdict(int),
                ReturnVisitor.Tries: defaultdict(int),
                ReturnVisitor.Returns: [],
            }
        )

        self.generic_visit(node)
        self.__checkFunction(node)
        self.__stack.pop()

    def visit_FunctionDef(self, node):
        """
        Public method to handle a function definition.

        @param node reference to the node to handle
        @type ast.FunctionDef
        """
        self.__visitWithStack(node)

    def visit_AsyncFunctionDef(self, node):
        """
        Public method to handle a function definition.

        @param node reference to the node to handle
        @type ast.AsyncFunctionDef
        """
        self.__visitWithStack(node)

    def visit_Return(self, node):
        """
        Public method to handle a return node.

        @param node reference to the node to handle
        @type ast.Return
        """
        self.returns.append(node)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """
        Public method to handle an assign node.

        @param node reference to the node to handle
        @type ast.Assign
        """
        if not self.__stack:
            return

        if isinstance(node.value, ast.Name):
            self.refs[node.value.id].append(node.value.lineno)

        self.generic_visit(node.value)

        target = node.targets[0]
        if isinstance(target, ast.Tuple) and not isinstance(node.value, ast.Tuple):
            # skip unpacking assign
            return

        self.__visitAssignTarget(target)

    def visit_Name(self, node):
        """
        Public method to handle a name node.

        @param node reference to the node to handle
        @type ast.Name
        """
        if self.__stack:
            self.refs[node.id].append(node.lineno)

    def visit_Try(self, node):
        """
        Public method to handle a try/except node.

        @param node reference to the node to handle
        @type ast.Try
        """
        if self.__stack and hasattr(node, "end_lineno") and node.end_lineno is not None:
            self.tries[node.lineno] = node.end_lineno

        self.generic_visit(node)

    def __visitAssignTarget(self, node):
        """
        Private method to handle an assign target node.

        @param node reference to the node to handle
        @type ast.AST
        """
        if isinstance(node, ast.Tuple):
            for elt in node.elts:
                self.__visitAssignTarget(elt)
            return

        if isinstance(node, ast.Name):
            self.assigns[node.id].append(node.lineno)
            return

        self.generic_visit(node)

    def __checkFunction(self, node):
        """
        Private method to check a function definition node.

        @param node reference to the node to check
        @type ast.AsyncFunctionDef or ast.FunctionDef
        """
        if not self.returns or not node.body:
            return

        if len(node.body) == 1 and isinstance(node.body[-1], ast.Return):
            # skip functions that consist of `return None` only
            return

        if not self.__resultExists():
            self.__checkUnnecessaryReturnNone()
            return

        self.__checkImplicitReturnValue()
        self.__checkImplicitReturn(node.body[-1])

        for n in self.returns:
            if n.value:
                self.__checkUnnecessaryAssign(n.value)

    def __isNone(self, node):
        """
        Private method to check, if a node value is None.

        @param node reference to the node to check
        @type ast.AST
        @return flag indicating the node contains a None value
        @rtype bool
        """
        return AstUtilities.isNameConstant(node) and AstUtilities.getValue(node) is None

    def __isFalse(self, node):
        """
        Private method to check, if a node value is False.

        @param node reference to the node to check
        @type ast.AST
        @return flag indicating the node contains a False value
        @rtype bool
        """
        return (
            AstUtilities.isNameConstant(node) and AstUtilities.getValue(node) is False
        )

    def __resultExists(self):
        """
        Private method to check the existance of a return result.

        @return flag indicating the existence of a return result
        @rtype bool
        """
        for node in self.returns:
            value = node.value
            if value and not self.__isNone(value):
                return True

        return False

    def __checkImplicitReturnValue(self):
        """
        Private method to check for implicit return values.
        """
        for node in self.returns:
            if not node.value:
                self.violations.append((node, "M-832"))

    def __checkUnnecessaryReturnNone(self):
        """
        Private method to check for an unnecessary 'return None' statement.
        """
        for node in self.returns:
            if self.__isNone(node.value):
                self.violations.append((node, "M-831"))

    def __checkImplicitReturn(self, node):
        """
        Private method to check for an implicit return statement.

        @param node reference to the node to check
        @type ast.AST
        """
        if isinstance(node, ast.If):
            if not node.body or not node.orelse:
                self.violations.append((node, "M-833"))
                return

            self.__checkImplicitReturn(node.body[-1])
            self.__checkImplicitReturn(node.orelse[-1])
            return

        if isinstance(node, (ast.For, ast.AsyncFor)) and node.orelse:
            self.__checkImplicitReturn(node.orelse[-1])
            return

        if isinstance(node, (ast.With, ast.AsyncWith, ast.For)):
            self.__checkImplicitReturn(node.body[-1])
            return

        if isinstance(node, ast.Assert) and self.__isFalse(node.test):
            return

        try:
            okNodes = (ast.Return, ast.Raise, ast.While, ast.Try)
        except AttributeError:
            okNodes = (ast.Return, ast.Raise, ast.While)
        if not isinstance(node, okNodes):
            self.violations.append((node, "M-833"))

    def __checkUnnecessaryAssign(self, node):
        """
        Private method to check for an unnecessary assign statement.

        @param node reference to the node to check
        @type ast.AST
        """
        if not isinstance(node, ast.Name):
            return

        varname = node.id
        returnLineno = node.lineno

        if varname not in self.assigns:
            return

        if varname not in self.refs:
            self.violations.append((node, "M-834"))
            return

        if self.__hasRefsBeforeNextAssign(varname, returnLineno):
            return

        if self.__hasRefsOrAssignsWithinTryOrLoop(varname):
            return

        self.violations.append((node, "M-834"))

    def __hasRefsOrAssignsWithinTryOrLoop(self, varname: str) -> bool:
        """
        Private method to check for references or assignments in exception handlers
        or loops.

        @param varname name of the variable to check for
        @type str
        @return flag indicating a reference or assignment
        @rtype bool
        """
        for item in [*self.refs[varname], *self.assigns[varname]]:
            for tryStart, tryEnd in self.tries.items():
                if tryStart < item <= tryEnd:
                    return True

            for loopStart, loopEnd in self.loops.items():
                if loopStart < item <= loopEnd:
                    return True

        return False

    def __hasRefsBeforeNextAssign(self, varname, returnLineno):
        """
        Private method to check for references before a following assign
        statement.

        @param varname variable name to check for
        @type str
        @param returnLineno line number of the return statement
        @type int
        @return flag indicating the existence of references
        @rtype bool
        """
        beforeAssign = 0
        afterAssign = None

        for lineno in sorted(self.assigns[varname]):
            if lineno > returnLineno:
                afterAssign = lineno
                break

            if lineno <= returnLineno:
                beforeAssign = lineno

        for lineno in self.refs[varname]:
            if lineno == returnLineno:
                continue

            if afterAssign:
                if beforeAssign < lineno <= afterAssign:
                    return True

            elif beforeAssign < lineno:
                return True

        return False
