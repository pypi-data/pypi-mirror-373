# -*- coding: utf-8 -*-

# Copyright (c) 2021 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for import statements.
"""

import ast
import copy
import re

from CodeStyleTopicChecker import CodeStyleTopicChecker


class ImportsChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for import statements.
    """

    Codes = [
        ## Local imports
        "I-101",
        "I-102",
        "I-103",
        ## Various other import related
        "I-901",
        "I-902",
        "I-903",
        "I-904",
    ]
    Category = "I"

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
            ImportsChecker.Category,
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
            (self.__checkLocalImports, ("I-101", "I-102", "I-103")),
            (self.__tidyImports, ("I-901", "I-902", "I-903", "I-904")),
        ]
        self._initializeCheckers(checkersWithCodes)

    #######################################################################
    ## Local imports
    ##
    ## adapted from: flake8-local-import v1.0.6
    #######################################################################

    def __checkLocalImports(self):
        """
        Private method to check local imports.
        """
        from .LocalImportVisitor import LocalImportVisitor

        visitor = LocalImportVisitor(self.args, self)
        visitor.visit(copy.deepcopy(self.tree))
        for violation in visitor.violations:
            self.addErrorFromNode(violation[0], violation[1])

    #######################################################################
    ## Tidy imports
    ##
    ## adapted from: flake8-tidy-imports v4.11.0
    #######################################################################

    def __tidyImports(self):
        """
        Private method to check various other import related topics.
        """
        self.__banRelativeImports = self.args.get("BanRelativeImports", "")
        self.__bannedModules = []
        self.__bannedStructuredPatterns = []
        self.__bannedUnstructuredPatterns = []
        for module in self.args.get("BannedModules", []):
            module = module.strip()
            if "*" in module[:-1] or module == "*":
                # unstructured
                self.__bannedUnstructuredPatterns.append(
                    self.__compileUnstructuredGlob(module)
                )
            elif module.endswith(".*"):
                # structured
                self.__bannedStructuredPatterns.append(module)
                # Also check for exact matches without the wildcard
                # e.g. "foo.*" matches "foo"
                prefix = module[:-2]
                if prefix not in self.__bannedModules:
                    self.__bannedModules.append(prefix)
            else:
                self.__bannedModules.append(module)

        # Sort the structured patterns so we match the specifc ones first.
        self.__bannedStructuredPatterns.sort(key=lambda x: len(x[0]), reverse=True)

        ruleMethods = []
        if not self._ignoreCode("I-901"):
            ruleMethods.append(self.__checkUnnecessaryAlias)
        if not self._ignoreCode("I-902") and bool(self.__bannedModules):
            ruleMethods.append(self.__checkBannedImport)
        if (
            not self._ignoreCode("I-903") and self.__banRelativeImports == "parents"
        ) or (not self._ignoreCode("I-904") and self.__banRelativeImports == "true"):
            ruleMethods.append(self.__checkBannedRelativeImports)

        for node in ast.walk(self.tree):
            for method in ruleMethods:
                method(node)

    def __compileUnstructuredGlob(self, module):
        """
        Private method to convert a pattern to a regex such that ".*" matches zero or
        more modules.

        @param module module pattern to be converted
        @type str
        @return compiled regex
        @rtype re.regex object
        """
        parts = module.split(".")
        transformedParts = [
            "(\\..*)?" if p == "*" else "\\." + re.escape(p) for p in parts
        ]
        if parts[0] == "*":
            transformedParts[0] = ".*"
        else:
            transformedParts[0] = re.escape(parts[0])
        return re.compile("".join(transformedParts) + "\\Z")

    def __checkUnnecessaryAlias(self, node):
        """
        Private method to check unnecessary import aliases.

        @param node reference to the node to be checked
        @type ast.AST
        """
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "." not in alias.name:
                    fromName = None
                    importedName = alias.name
                else:
                    fromName, importedName = alias.name.rsplit(".", 1)

                if importedName == alias.asname:
                    if fromName:
                        rewritten = f"from {fromName} import {importedName}"
                    else:
                        rewritten = f"import {importedName}"

                    self.addErrorFromNode(node, "I-901", rewritten)

        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == alias.asname:
                    rewritten = f"from {node.module} import {alias.name}"

                    self.addErrorFromNode(node, "I-901", rewritten)

    def __isModuleBanned(self, moduleName):
        """
        Private method to check, if the given module name banned.

        @param moduleName module name to be checked
        @type str
        @return flag indicating a banned module
        @rtype bool
        """
        if moduleName in self.__bannedModules:
            return True

        # Check unustructed wildcards
        if any(
            bannedPattern.match(moduleName)
            for bannedPattern in self.__bannedUnstructuredPatterns
        ):
            return True

        # Check structured wildcards
        if any(
            moduleName.startswith(bannedPrefix[:-1])
            for bannedPrefix in self.__bannedStructuredPatterns
        ):
            return True

        return False

    def __checkBannedImport(self, node):
        """
        Private method to check import of banned modules.

        @param node reference to the node to be checked
        @type ast.AST
        """
        if (
            not bool(self.__bannedModules)
            and not bool(self.__bannedUnstructuredPatterns)
            and not bool(self.__bannedStructuredPatterns)
        ):
            # nothing to check
            return

        if isinstance(node, ast.Import):
            moduleNames = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            nodeModule = node.module or ""
            moduleNames = [nodeModule]
            for alias in node.names:
                moduleNames.append("{0}.{1}".format(nodeModule, alias.name))
        else:
            return

        # Sort from most to least specific paths.
        moduleNames.sort(key=len, reverse=True)

        warned = set()

        for moduleName in moduleNames:
            if self.__isModuleBanned(moduleName):
                if any(mod.startswith(moduleName) for mod in warned):
                    # Do not show an error for this line if we already showed
                    # a more specific error.
                    continue
                else:
                    warned.add(moduleName)
                self.addErrorFromNode(node, "I-902", moduleName)

    def __checkBannedRelativeImports(self, node):
        """
        Private method to check if relative imports are banned.

        @param node reference to the node to be checked
        @type ast.AST
        """
        if not self.__banRelativeImports:
            # nothing to check
            return

        elif self.__banRelativeImports == "parents":
            minNodeLevel = 1
            msgCode = "I-903"
        else:
            minNodeLevel = 0
            msgCode = "I-904"

        if isinstance(node, ast.ImportFrom) and node.level > minNodeLevel:
            self.addErrorFromNode(node, msgCode)
