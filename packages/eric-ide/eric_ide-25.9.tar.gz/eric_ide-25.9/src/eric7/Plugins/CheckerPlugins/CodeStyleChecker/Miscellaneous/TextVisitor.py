# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor for bytes and str instances.
"""

import ast

import AstUtilities


class TextVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor for bytes and str instances.

    It tries to detect docstrings as string of the first expression of each
    module, class or function.
    """

    # modeled after the string format flake8 extension

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.nodes = []
        self.calls = {}

    def __addNode(self, node):
        """
        Private method to add a node to our list of nodes.

        @param node reference to the node to add
        @type ast.AST
        """
        if not hasattr(node, "is_docstring"):
            node.is_docstring = False
        self.nodes.append(node)

    def visit_Constant(self, node):
        """
        Public method to handle constant nodes.

        @param node reference to the bytes node
        @type ast.Constant
        """
        if AstUtilities.isBaseString(node):
            self.__addNode(node)
        else:
            super().generic_visit(node)

    def __visitDefinition(self, node):
        """
        Private method handling class and function definitions.

        @param node reference to the node to handle
        @type ast.FunctionDef, ast.AsyncFunctionDef or ast.ClassDef
        """
        # Manually traverse class or function definition
        # * Handle decorators normally
        # * Use special check for body content
        # * Don't handle the rest (e.g. bases)
        for decorator in node.decorator_list:
            self.visit(decorator)
        self.__visitBody(node)

    def __visitBody(self, node):
        """
        Private method to traverse the body of the node manually.

        If the first node is an expression which contains a string or bytes it
        marks that as a docstring.

        @param node reference to the node to traverse
        @type ast.AST
        """
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and AstUtilities.isBaseString(node.body[0].value)
        ):
            node.body[0].value.is_docstring = True

        for subnode in node.body:
            self.visit(subnode)

    def visit_Module(self, node):
        """
        Public method to handle a module.

        @param node reference to the node to handle
        @type ast.Module
        """
        self.__visitBody(node)

    def visit_ClassDef(self, node):
        """
        Public method to handle a class definition.

        @param node reference to the node to handle
        @type ast.ClassDef
        """
        # Skipped nodes: ('name', 'bases', 'keywords', 'starargs', 'kwargs')
        self.__visitDefinition(node)

    def visit_FunctionDef(self, node):
        """
        Public method to handle a function definition.

        @param node reference to the node to handle
        @type ast.FunctionDef
        """
        # Skipped nodes: ('name', 'args', 'returns')
        self.__visitDefinition(node)

    def visit_AsyncFunctionDef(self, node):
        """
        Public method to handle an asynchronous function definition.

        @param node reference to the node to handle
        @type ast.AsyncFunctionDef
        """
        # Skipped nodes: ('name', 'args', 'returns')
        self.__visitDefinition(node)

    def visit_Call(self, node):
        """
        Public method to handle a function call.

        @param node reference to the node to handle
        @type ast.Call
        """
        if isinstance(node.func, ast.Attribute) and node.func.attr == "format":
            if AstUtilities.isBaseString(node.func.value):
                self.calls[node.func.value] = (node, False)
            elif (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id == "str"
                and node.args
                and AstUtilities.isBaseString(node.args[0])
            ):
                self.calls[node.args[0]] = (node, True)
        super().generic_visit(node)
