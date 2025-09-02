# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check for pydantic related issues.
"""

#######################################################################
## PydanticVisitor
##
## adapted from: flake8-pydantic v0.4.0
##
## Original: Copyright (c) 2023 Victorien
#######################################################################

import ast

from collections import deque

from .PydanticUtils import (
    extractAnnotations,
    isDataclass,
    isFunction,
    isName,
    isPydanticModel,
)


class PydanticVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check for pydantic related issues.
    """

    def __init__(self, errorCallback):
        """
        Constructor

        @param errorCallback callback function to register an issue
        @type func
        """
        super().__init__()

        self.__error = errorCallback

        self.__classStack = deque()

    def __enterClass(self, node):
        """
        Private method to record class type when entering a class definition.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        if isPydanticModel(node):
            self.__classStack.append("pydantic_model")
        elif isDataclass(node):
            self.__classStack.append("dataclass")
        else:
            self.__classStack.append("other_class")

    def __leaveClass(self):
        """
        Private method to remove the data recorded by the __enterClass method.
        """
        self.__classStack.pop()

    @property
    def __currentClass(self):
        """
        Private method returning the current class type as recorded by the __enterClass
        method.

        @return current class type (one of 'pydantic_model', 'dataclass' or
            'other_class')
        @rtype str
        """
        if not self.__classStack:
            return None

        return self.__classStack[-1]

    def __checkForPyd001(self, node: ast.AnnAssign) -> None:
        """
        Private method to check positional argument for Field default argument.

        @param node reference to the node to be processed
        @type ast.AnnAssign
        """
        if (
            self.__currentClass in {"pydantic_model", "dataclass"}
            and isinstance(node.value, ast.Call)
            and isFunction(node.value, "Field")
            and len(node.value.args) >= 1
        ):
            self.__error(node, "PYD-001")

    def __checkForPyd002(self, node):
        """
        Private method to check non-annotated attribute inside Pydantic model.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        if self.__currentClass == "pydantic_model":
            invalidAssignments = [
                assign
                for assign in node.body
                if isinstance(assign, ast.Assign)
                if isinstance(assign.targets[0], ast.Name)
                if not assign.targets[0].id.startswith("_")
                if assign.targets[0].id != "model_config"
            ]
            for assignment in invalidAssignments:
                self.__error(assignment, "PYD-002")

    def __checkForPyd003(self, node):
        """
        Private method to check unecessary Field call to specify a default value.

        @param node reference to the node to be processed
        @type ast.AnnAssign
        """
        if (
            self.__currentClass in {"pydantic_model", "dataclass"}
            and isinstance(node.value, ast.Call)
            and isFunction(node.value, "Field")
            and len(node.value.keywords) == 1
            and node.value.keywords[0].arg == "default"
        ):
            self.__error(node, "PYD-003")

    def __checkForPyd004(self, node):
        """
        Private method to check for a default argument specified in annotated.

        @param node reference to the node to be processed
        @type ast.AnnAssign
        """
        if (
            self.__currentClass in {"pydantic_model", "dataclass"}
            and isinstance(node.annotation, ast.Subscript)
            and isName(node.annotation.value, "Annotated")
            and isinstance(node.annotation.slice, ast.Tuple)
        ):
            fieldCall = next(
                (
                    elt
                    for elt in node.annotation.slice.elts
                    if isinstance(elt, ast.Call)
                    and isFunction(elt, "Field")
                    and any(k.arg == "default" for k in elt.keywords)
                ),
                None,
            )
            if fieldCall is not None:
                self.__error(node, "PYD-004")

    def __checkForPyd005(self, node):
        """
        Private method to check for a field name overriding the annotation.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        if self.__currentClass in {"pydantic_model", "dataclass"}:
            previousTargets = set()

            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(
                    stmt.target, ast.Name
                ):
                    previousTargets.add(stmt.target.id)
                    if previousTargets & extractAnnotations(stmt.annotation):
                        self.__error(stmt, "PYD-005")

    def __checkForPyd006(self, node):
        """
        Private method to check for duplicate field names.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        if self.__currentClass in {"pydantic_model", "dataclass"}:
            previousTargets = set()

            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(
                    stmt.target, ast.Name
                ):
                    if stmt.target.id in previousTargets:
                        self.__error(stmt, "PYD-006")

                    previousTargets.add(stmt.target.id)

    def __checkForPyd010(self, node: ast.ClassDef) -> None:
        """
        Private method to check for the use of `__pydantic_config__`.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        if self.__currentClass == "other_class":
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.AnnAssign)
                    and isinstance(stmt.target, ast.Name)
                    and stmt.target.id == "__pydantic_config__"
                ):
                    ##~ __pydantic_config__: ... = ...
                    self.__error(stmt, "PYD-010")

                if isinstance(stmt, ast.Assign) and any(
                    t.id == "__pydantic_config__"
                    for t in stmt.targets
                    if isinstance(t, ast.Name)
                ):
                    ##~ __pydantic_config__ = ...
                    self.__error(stmt, "PYD-010")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Public method to process class definitions.

        @param node reference to the node to be processed.
        @type ast.ClassDef
        """
        self.__enterClass(node)

        self.__checkForPyd002(node)
        self.__checkForPyd005(node)
        self.__checkForPyd006(node)
        self.__checkForPyd010(node)

        self.generic_visit(node)

        self.__leaveClass()

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """
        Public method to process annotated assignment.

        @param node reference to the node to be processed.
        @type ast.AnnAssign
        """
        self.__checkForPyd001(node)
        self.__checkForPyd003(node)
        self.__checkForPyd004(node)

        self.generic_visit(node)
