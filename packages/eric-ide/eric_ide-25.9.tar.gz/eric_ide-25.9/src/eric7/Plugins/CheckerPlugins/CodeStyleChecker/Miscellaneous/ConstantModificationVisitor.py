# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check for modifications of constants.
"""

import ast

#######################################################################
## adapted from: flake8-constants v0.0.3
##
## Original: Copyright (c) 2024 Enea Kllomollari
#######################################################################


class ConstantModificationVisitor:
    """
    Class implementing a node visitor to check for modifications of constants.
    """

    DEFAULT_NON_MODIFYING_METHODS = {  # noqa: M-916
        "get",
        "keys",
        "values",
        "items",
        "copy",
        "deepcopy",
        "encode",
        "decode",
        "strip",
        "__getitem__",
        "__len__",
        "__iter__",
        "__contains__",
    }

    def __init__(self):
        """
        Constructor
        """
        self.violations = []

        self.__constants = {"": set()}  # Global scope
        self.__scopeStack = [""]  # Start in global scope
        self.__nonModifyingMethods = (
            ConstantModificationVisitor.DEFAULT_NON_MODIFYING_METHODS.copy()
        )

    def visit(self, node):
        """
        Public method to traverse the node tree.

        @param node reference to the ast node to traverse
        @type ast.AST
        """
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.__scopeStack.append(node.name)
            self.__constants.setdefault(self.__currentScope(), set())

            for item in node.body:
                self.visit(item)

            self.__scopeStack.pop()
            return

        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            self.__checkAssignment(node)
        elif isinstance(node, ast.AugAssign):
            self.__checkAugAssignment(node)
        elif isinstance(node, ast.Call):
            self.__checkCall(node)

        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def __currentScope(self):
        """
        Private method to return the name of the current scope.

        @return name of the current scope
        @rtype str
        """
        return ".".join(self.__scopeStack)

    def __currentScopeMsg(self):
        """
        Private method to return the name of the current scope for the error message.

        @return current scope for the error message
        @rtype str
        """
        if len(self.__scopeStack) > 1:
            return ".".join(self.__scopeStack)[1:]
        else:
            return "global"

    def __checkAssignment(self, node):
        """
        Private method to check assignment statements.

        @param node reference to the node to be checked
        @type ast.Assign or ast.AnnAssign
        """
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name) and target.id.isupper():
                currentScope = self.__currentScope()
                if target.id in self.__constants[currentScope]:
                    self.violations.append(
                        (node, "M-911", target.id, self.__currentScopeMsg())
                    )
                else:
                    self.__constants[currentScope].add(target.id)
                    # Check if the constant is a mutable type
                    if isinstance(node, (ast.Assign, ast.AnnAssign)):
                        value = node.value
                    else:
                        continue

                    if isinstance(value, (ast.List, ast.Dict, ast.Set)):
                        self.violations.append((node, "M-916", target.id))

            elif (
                isinstance(target, ast.Attribute)
                and target.attr.isupper()
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                classScope = ".".join(self.__scopeStack[:-1])
                if (
                    classScope in self.__constants
                    and target.attr in self.__constants[classScope]
                ):
                    self.violations.append((node, "M-912", target.attr))
                else:
                    self.__constants[classScope].add(target.attr)

    def __checkAugAssignment(self, node):
        """
        Private method to check augmented assignment statements.

        @param node reference to the node to be checked
        @type ast.AugAssign
        """
        if isinstance(node.target, ast.Name) and node.target.id.isupper():
            self.violations.append(
                (node, "M-913", node.target.id, self.__currentScopeMsg())
            )
        elif (
            isinstance(node.target, ast.Attribute)
            and node.target.attr.isupper()
            and isinstance(node.target.value, ast.Name)
            and node.target.value.id == "self"
        ):
            classScope = ".".join(self.__scopeStack[:-1])
            if (
                classScope in self.__constants
                and node.target.attr in self.__constants[classScope]
            ):
                self.violations.append((node, "M-914", node.target.attr))

    def __checkCall(self, node):
        """
        Private method to check function call statements.

        @param node reference to the node to be checked
        @type ast.Call
        """
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id.isupper()
            and node.func.attr not in self.__nonModifyingMethods
        ):
            self.violations.append(
                (node, "M-915", node.func.value.id, self.__currentScopeMsg())
            )
