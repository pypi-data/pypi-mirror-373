# -*- coding: utf-8 -*-

# Copyright (c) 2021 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the checker for functions that can be replaced by use of
the pathlib module.
"""

#####################################################################################
## adapted from: flake8-use-pathlib v0.3.0                                         ##
##                                                                                 ##
## Original: Copyright (c) 2021 Rodolphe Pelloux-Prayer                            ##
#####################################################################################

import ast
import contextlib

from CodeStyleTopicChecker import CodeStyleTopicChecker


class PathlibChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for functions that can be replaced by use of
    the pathlib module.
    """

    Codes = [
        ## Replacements for the os module functions
        "P-101",
        "P-102",
        "P-103",
        "P-104",
        "P-105",
        "P-106",
        "P-107",
        "P-108",
        "P-109",
        "P-110",
        "P-111",
        "P-112",
        "P-113",
        "P-114",
        ## Replacements for the os.path module functions
        "P-201",
        "P-202",
        "P-203",
        "P-204",
        "P-205",
        "P-206",
        "P-207",
        "P-208",
        "P-209",
        "P-210",
        "P-211",
        "P-212",
        "P-213",
        ## Replacements for some Python standard library functions
        "P-301",
        ## Replacements for py.path.local
        "P-401",
    ]
    Category = "P"

    # map functions to be replaced to error codes
    Function2Code = {
        "os.chmod": "P-101",
        "os.mkdir": "P-102",
        "os.makedirs": "P-103",
        "os.rename": "P-104",
        "os.replace": "P-105",
        "os.rmdir": "P-106",
        "os.remove": "P-107",
        "os.unlink": "P-108",
        "os.getcwd": "P-109",
        "os.readlink": "P-110",
        "os.stat": "P-111",
        "os.listdir": "P-112",
        "os.link": "P-113",
        "os.symlink": "P-114",
        "os.path.abspath": "P-201",
        "os.path.exists": "P-202",
        "os.path.expanduser": "P-203",
        "os.path.isdir": "P-204",
        "os.path.isfile": "P-205",
        "os.path.islink": "P-206",
        "os.path.isabs": "P-207",
        "os.path.join": "P-208",
        "os.path.basename": "P-209",
        "os.path.dirname": "P-210",
        "os.path.samefile": "P-211",
        "os.path.splitext": "P-212",
        "os.path.relpath": "P-213",
        "open": "P-301",
        "py.path.local": "P-401",
    }

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
            PathlibChecker.Category,
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
                self.__checkPathlibReplacement,
                (
                    "P-101",
                    "P-102",
                    "P-103",
                    "P-104",
                    "P-105",
                    "P-106",
                    "P-107",
                    "P-108",
                    "P-109",
                    "P-110",
                    "P-111",
                    "P-112",
                    "P-113",
                    "P-114",
                    "P-201",
                    "P-202",
                    "P-203",
                    "P-204",
                    "P-205",
                    "P-206",
                    "P-207",
                    "P-208",
                    "P-209",
                    "P-210",
                    "P-211",
                    "P-212",
                    "P-213",
                    "P-301",
                    "P-401",
                ),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

    def __checkPathlibReplacement(self):
        """
        Private method to check for pathlib replacements.
        """
        visitor = PathlibVisitor(self.__checkForReplacement)
        visitor.visit(self.tree)

    def __checkForReplacement(self, node, name):
        """
        Private method to check the given node for the need for a
        replacement.

        @param node reference to the AST node to check
        @type ast.AST
        @param name resolved name of the node
        @type str
        """
        with contextlib.suppress(KeyError):
            errorCode = self.Function2Code[name]
            self.addErrorFromNode(node, errorCode)


class PathlibVisitor(ast.NodeVisitor):
    """
    Class to traverse the AST node tree and check for potential issues.
    """

    def __init__(self, checkCallback):
        """
        Constructor

        @param checkCallback callback function taking a reference to the
            AST node and the resolved name
        @type func
        """
        super().__init__()

        self.__checkCallback = checkCallback
        self.__importAlias = {}

    def visit_ImportFrom(self, node):
        """
        Public method handle the ImportFrom AST node.

        @param node reference to the ImportFrom AST node
        @type ast.ImportFrom
        """
        for imp in node.names:
            if imp.asname:
                self.__importAlias[imp.asname] = f"{node.module}.{imp.name}"
            else:
                self.__importAlias[imp.name] = f"{node.module}.{imp.name}"

    def visit_Import(self, node):
        """
        Public method to handle the Import AST node.

        @param node reference to the Import AST node
        @type ast.Import
        """
        for imp in node.names:
            if imp.asname:
                self.__importAlias[imp.asname] = imp.name

    def visit_Call(self, node):
        """
        Public method to handle the Call AST node.

        @param node reference to the Call AST node
        @type ast.Call
        """
        nameResolver = NameResolver(self.__importAlias)
        nameResolver.visit(node.func)

        self.__checkCallback(node, nameResolver.name())

        self.generic_visit(node)


class NameResolver(ast.NodeVisitor):
    """
    Class to resolve a Name or Attribute node.
    """

    def __init__(self, importAlias):
        """
        Constructor

        @param importAlias reference to the import aliases dictionary
        @type dict
        """
        self.__importAlias = importAlias
        self.__names = []

    def name(self):
        """
        Public method to resolve the name.

        @return resolved name
        @rtype str
        """
        with contextlib.suppress(KeyError, IndexError):
            attr = self.__importAlias[self.__names[-1]]
            self.__names[-1] = attr
            # do nothing if there is no such name or the names list is empty

        return ".".join(reversed(self.__names))

    def visit_Name(self, node):
        """
        Public method to handle the Name AST node.

        @param node reference to the Name AST node
        @type ast.Name
        """
        self.__names.append(node.id)

    def visit_Attribute(self, node):
        """
        Public method to handle the Attribute AST node.

        @param node reference to the Attribute AST node
        @type ast.Attribute
        """
        try:
            self.__names.append(node.attr)
            self.__names.append(node.value.id)
        except AttributeError:
            self.generic_visit(node)
