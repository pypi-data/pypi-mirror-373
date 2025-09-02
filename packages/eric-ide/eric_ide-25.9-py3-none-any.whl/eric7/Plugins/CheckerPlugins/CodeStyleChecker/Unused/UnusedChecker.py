# -*- coding: utf-8 -*-

# Copyright (c) 2023 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for unused arguments, variables, ... .
"""

import ast
import collections

import AstUtilities

from CodeStyleTopicChecker import CodeStyleTopicChecker


class UnusedChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for unused arguments, variables, ... .
    """

    Codes = [
        ## Unused Arguments
        "U-100",
        "U-101",
        ## Unused Globals
        "U-200",
    ]
    Category = "U"

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
            UnusedChecker.Category,
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
            (self.__checkUnusedArguments, ("U-100", "U-101")),
            (self.__checkUnusedGlobals, ("U-200",)),
        ]
        self._initializeCheckers(checkersWithCodes)

    #######################################################################
    ## Unused Arguments
    ##
    ## adapted from: flake8-unused-arguments v0.0.13
    #######################################################################

    def __checkUnusedArguments(self):
        """
        Private method to check function and method definitions for unused arguments.
        """
        finder = FunctionFinder(self.args["IgnoreNestedFunctions"])
        finder.visit(self.tree)

        for functionNode in finder.functionNodes():
            decoratorNames = set(self.__getDecoratorNames(functionNode))

            # ignore overload functions, it's not a surprise when they're empty
            if self.args["IgnoreOverload"] and "overload" in decoratorNames:
                continue

            # ignore overridden functions
            if self.args["IgnoreOverride"] and "override" in decoratorNames:
                continue

            # ignore abstractmethods, it's not a surprise when they're empty
            if self.args["IgnoreAbstract"] and "abstractmethod" in decoratorNames:
                continue

            # ignore Qt slot methods
            if self.args["IgnoreSlotMethods"] and (
                "pyqtSlot" in decoratorNames or "Slot" in decoratorNames
            ):
                continue

            if self.args["IgnoreEventHandlerMethods"] and self.__isEventHandlerMethod(
                functionNode
            ):
                continue

            # ignore stub functions
            if self.args["IgnoreStubs"] and self.__isStubFunction(functionNode):
                continue

            # ignore lambdas
            if self.args["IgnoreLambdas"] and isinstance(functionNode, ast.Lambda):
                continue

            # ignore __double_underscore_methods__()
            if self.args["IgnoreDunderMethods"] and self.__isDunderMethod(functionNode):
                continue

            for i, argument in self.__getUnusedArguments(functionNode):
                name = argument.arg
                if self.args["IgnoreVariadicNames"]:
                    if (
                        functionNode.args.vararg
                        and functionNode.args.vararg.arg == name
                    ):
                        continue
                    if functionNode.args.kwarg and functionNode.args.kwarg.arg == name:
                        continue

                # ignore self or whatever the first argument is for a classmethod
                if i == 0 and (
                    name in ("self", "cls") or "classmethod" in decoratorNames
                ):
                    continue

                lineNumber = argument.lineno
                offset = argument.col_offset

                errorCode = "U-101" if name.startswith("_") else "U-100"
                self.addError(lineNumber, offset, errorCode, name)

    def __getDecoratorNames(self, functionNode):
        """
        Private method to yield the decorator names of the function.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @yield decorator name
        @ytype str
        """
        if isinstance(functionNode, ast.Lambda):
            return

        for decorator in functionNode.decorator_list:
            if isinstance(decorator, ast.Name):
                yield decorator.id
            elif isinstance(decorator, ast.Attribute):
                yield decorator.attr
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    yield decorator.func.id
                else:
                    yield decorator.func.attr

    def __isStubFunction(self, functionNode):
        """
        Private method to check, if the given function node defines a stub function.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @return flag indicating a stub function
        @rtype bool
        """
        if isinstance(functionNode, ast.Lambda):
            return AstUtilities.isEllipsis(functionNode.body)

        statement = functionNode.body[0]
        if isinstance(statement, ast.Expr) and AstUtilities.isString(statement.value):
            if len(functionNode.body) > 1:
                # first statement is a docstring, let's skip it
                statement = functionNode.body[1]
            else:
                # it's a function with only a docstring, that's a stub
                return True

        if isinstance(statement, ast.Pass):
            return True
        if isinstance(statement, ast.Expr) and AstUtilities.isEllipsis(statement.value):
            return True

        if isinstance(statement, ast.Raise):
            # like 'raise NotImplementedError()'
            if (
                isinstance(statement.exc, ast.Call)
                and hasattr(statement.exc.func, "id")
                and statement.exc.func.id == "NotImplementedError"
            ):
                return True

            # like 'raise NotImplementedError'
            elif (
                isinstance(statement.exc, ast.Name)
                and hasattr(statement.exc, "id")
                and statement.exc.id == "NotImplementedError"
            ):
                return True

        return False

    def __isDunderMethod(self, functionNode):
        """
        Private method to check, if the function node defines a special function.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @return flag indicating a special function
        @rtype bool
        """
        if isinstance(functionNode, ast.Lambda):
            return False

        if not hasattr(functionNode, "name"):
            return False

        name = functionNode.name
        return len(name) > 4 and name.startswith("__") and name.endswith("__")

    def __isEventHandlerMethod(self, functionNode):
        """
        Private method to check, if the function node defines a Qt event handler.

        Qt event handler methods are assumed to end with 'Event' or have the name
        'event' or 'eventFilter'. Only standard methodes (i.e. ast.FunctionDef)
        are assumed to be potential event handlers.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @return flag indicating a Qt event handler method
        @rtype bool
        """
        if isinstance(functionNode, (ast.Lambda, ast.AsyncFunctionDef)):
            return False

        if not hasattr(functionNode, "name"):
            return False

        name = functionNode.name
        return name.endswith("Event") or name in ("event", "eventFilter")

    def __getUnusedArguments(self, functionNode):
        """
        Private method to get a list of unused arguments of the given function.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @return list of tuples of the argument position and the argument
        @rtype list of tuples of (int, ast.arg)
        """
        arguments = list(enumerate(self.__getArguments(functionNode)))

        class NameFinder(ast.NodeVisitor):
            """
            Class to find the used argument names.
            """

            def visit_Name(self, name):
                """
                Public method to check a Name node.

                @param name reference to the name node to be checked
                @type ast.Name
                """
                nonlocal arguments

                if isinstance(name.ctx, ast.Store):
                    return

                arguments = [
                    (argIndex, arg) for argIndex, arg in arguments if arg.arg != name.id
                ]

        NameFinder().visit(functionNode)
        return arguments

    def __getArguments(self, functionNode):
        """
        Private method to get all argument names of the given function.

        @param functionNode reference to the node defining the function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        @return list of argument names
        @rtype list of ast.arg
        """
        args = functionNode.args

        orderedArguments = []

        # plain old args
        orderedArguments.extend(args.args)

        # *arg name
        if args.vararg is not None:
            orderedArguments.append(args.vararg)

        # *, key, word, only, args
        orderedArguments.extend(args.kwonlyargs)

        # **kwarg name
        if args.kwarg is not None:
            orderedArguments.append(args.kwarg)

        return orderedArguments

    #######################################################################
    ## Unused Globals
    ##
    ## adapted from: flake8-unused-globals v0.1.10
    #######################################################################

    def __checkUnusedGlobals(self):
        """
        Private method to check for unused global variables.
        """
        errors = {}
        loadCounter = GlobalVariableLoadCounter()
        loadCounter.visit(self.tree)

        globalVariables = self.__extractGlobalVariables()

        for varId, loads in loadCounter.getLoads():
            if varId in globalVariables and loads == 0:
                storeInfo = loadCounter.getStoreInfo(varId)
                errorInfo = (storeInfo.lineno, storeInfo.offset, "U-200", varId)
                errors[varId] = errorInfo

        for node in self.tree.body[::-1]:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in errors:
                        errors.pop(target.id)
            elif (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id in errors
            ):
                errors.pop(node.target.id)
            else:
                break

        if self.args["IgnoreDunderGlobals"]:
            # eliminate some special cases
            for name in list(errors):
                if name.startswith("__") and name.endswith("__"):
                    errors.pop(name)

        for varId in errors:
            self.addError(*errors[varId])

    def __extractGlobalVariables(self):
        """
        Private method to get the names of all global variables.

        @return set containing the defined global variable names
        @rtype set of str
        """
        variables = set()

        for assignment in self.tree.body:
            if isinstance(assignment, ast.Assign):
                for target in assignment.targets:
                    if isinstance(target, ast.Name):
                        variables.add(target.id)
            elif isinstance(assignment, ast.AnnAssign) and isinstance(
                assignment.target, ast.Name
            ):
                variables.add(assignment.target.id)

        return variables


#######################################################################
## Class used by 'Unused Arguments'
##
## adapted from: flake8-unused-arguments v0.0.13
#######################################################################


class FunctionFinder(ast.NodeVisitor):
    """
    Class to find all defined functions and methods.
    """

    def __init__(self, onlyTopLevel=False):
        """
        Constructor

        @param onlyTopLevel flag indicating to search for top level functions only
            (defaults to False)
        @type bool (optional)
        """
        super().__init__()

        self.__functions = []
        self.__onlyTopLevel = onlyTopLevel

    def functionNodes(self):
        """
        Public method to get the list of detected functions and lambdas.

        @return list of detected functions and lambdas
        @rtype list of ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        """
        return self.__functions

    def __visitFunctionTypes(self, functionNode):
        """
        Private method to handle an AST node defining a function or lambda.

        @param functionNode reference to the node defining a function or lambda
        @type ast.AsyncFunctionDef, ast.FunctionDef or ast.Lambda
        """
        self.__functions.append(functionNode)
        if not self.__onlyTopLevel:
            if isinstance(functionNode, ast.Lambda):
                self.visit(functionNode.body)
            else:
                for obj in functionNode.body:
                    self.visit(obj)

    visit_AsyncFunctionDef = visit_FunctionDef = visit_Lambda = __visitFunctionTypes


#######################################################################
## Class used by 'Unused Globals'
##
## adapted from: flake8-unused-globals v0.1.9
#######################################################################


GlobalVariableStoreInfo = collections.namedtuple(
    "GlobalVariableStoreInfo", ["lineno", "offset"]
)


class GlobalVariableLoadCounter(ast.NodeVisitor):
    """
    Class to find all defined global variables and count their usages.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.__loads = {}
        self.__storeInfo = {}

    def visit_Name(self, nameNode):
        """
        Public method to record the definition and use of a global variable.

        @param nameNode reference to the name node to be processed
        @type ast.Name
        """
        if isinstance(nameNode.ctx, ast.Load) and nameNode.id in self.__loads:
            self.__loads[nameNode.id] += 1
        elif (
            isinstance(nameNode.ctx, ast.Store) and nameNode.id not in self.__storeInfo
        ):
            self.__loads[nameNode.id] = 0
            self.__storeInfo[nameNode.id] = GlobalVariableStoreInfo(
                lineno=nameNode.lineno, offset=nameNode.col_offset
            )

    def getLoads(self):
        """
        Public method to get an iterator of the detected variable loads.

        @return DESCRIPTION
        @rtype TYPE
        """
        return self.__loads.items()

    def getStoreInfo(self, variableId):
        """
        Public method to get the store info data of a given variable ID.

        @param variableId variable ID to retrieve the store info for
        @type str
        @return named tuple containing the line number and column offset
        @rtype GlobalVariableStoreInfo
        """
        try:
            return self.__storeInfo[variableId]
        except KeyError:
            return None
