# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a visitor to check for various potential issues.
"""

import ast
import builtins
import contextlib
import itertools
import math
import re

from collections import Counter, namedtuple
from dataclasses import dataclass
from keyword import iskeyword

import AstUtilities

#######################################################################
## adapted from: flake8-bugbear v24.12.12
##
## Original: Copyright (c) 2016 Łukasz Langa
#######################################################################

BugbearMutableLiterals = ("Dict", "List", "Set")
BugbearMutableComprehensions = ("ListComp", "DictComp", "SetComp")
BugbearMutableCalls = (
    "Counter",
    "OrderedDict",
    "collections.Counter",
    "collections.OrderedDict",
    "collections.defaultdict",
    "collections.deque",
    "defaultdict",
    "deque",
    "dict",
    "list",
    "set",
)
BugbearImmutableCalls = (
    "tuple",
    "frozenset",
    "types.MappingProxyType",
    "MappingProxyType",
    "re.compile",
    "operator.attrgetter",
    "operator.itemgetter",
    "operator.methodcaller",
    "attrgetter",
    "itemgetter",
    "methodcaller",
)


BugBearContext = namedtuple("BugBearContext", ["node", "stack"])


def composeCallPath(node):
    """
    Generator function to assemble the call path of a given node.

    @param node node to assemble call path for
    @type ast.Node
    @yield call path components
    @ytype str
    """
    if isinstance(node, ast.Attribute):
        yield from composeCallPath(node.value)
        yield node.attr
    elif isinstance(node, ast.Call):
        yield from composeCallPath(node.func)
    elif isinstance(node, ast.Name):
        yield node.id


@dataclass
class M540CaughtException:
    """
    Class to hold the data for a caught exception.
    """

    name: str
    hasNote: bool


class M541UnhandledKeyType:
    """
    Class to hold a dictionary key of a type that we do not check for duplicates.
    """


class M541VariableKeyType:
    """
    Class to hold the name of a variable key type.
    """

    def __init__(self, name):
        """
        Constructor

        @param name name of the variable key type
        @type str
        """
        self.name = name


class BugBearVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check for various topics.
    """

    CONTEXTFUL_NODES = (
        ast.Module,
        ast.ClassDef,
        ast.AsyncFunctionDef,
        ast.FunctionDef,
        ast.Lambda,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
    )

    FUNCTION_NODES = (
        ast.AsyncFunctionDef,
        ast.FunctionDef,
        ast.Lambda,
    )

    NodeWindowSize = 4

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.nodeWindow = []
        self.violations = []
        self.contexts = []

        self.__M523Seen = set()
        self.__M505Imports = set()
        self.__M540CaughtException = None

        self.__inTryStar = ""

    @property
    def nodeStack(self):
        """
        Public method to get a reference to the most recent node stack.

        @return reference to the most recent node stack
        @rtype list
        """
        if len(self.contexts) == 0:
            return []

        context, stack = self.contexts[-1]
        return stack

    def __isIdentifier(self, arg):
        """
        Private method to check if arg is a valid identifier.

        See https://docs.python.org/2/reference/lexical_analysis.html#identifiers

        @param arg reference to an argument node
        @type ast.Node
        @return flag indicating a valid identifier
        @rtype TYPE
        """
        if not AstUtilities.isString(arg):
            return False

        return (
            re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", AstUtilities.getValue(arg))
            is not None
        )

    def toNameStr(self, node):
        """
        Public method to turn Name and Attribute nodes to strings, handling any
        depth of attribute accesses.


        @param node reference to the node
        @type ast.Name or ast.Attribute
        @return string representation
        @rtype str
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            return self.toNameStr(node.func)
        elif isinstance(node, ast.Attribute):
            inner = self.toNameStr(node.value)
            if inner is None:
                return None
            return f"{inner}.{node.attr}"
        else:
            return None

    def __typesafeIssubclass(self, obj, classOrTuple):
        """
        Private method implementing a type safe issubclass() function.

        @param obj reference to the object to be tested
        @type Any
        @param classOrTuple type to check against
        @type type
        @return flag indicating a subclass
        @rtype bool
        """
        try:
            return issubclass(obj, classOrTuple)
        except TypeError:
            # User code specifies a type that is not a type in our current run.
            # Might be their error, might be a difference in our environments.
            # We don't know so we ignore this.
            return False

    def __getAssignedNames(self, loopNode):
        """
        Private method to get the names of a for loop.

        @param loopNode reference to the node to be processed
        @type ast.For
        @yield DESCRIPTION
        @ytype TYPE
        """
        loopTargets = (ast.For, ast.AsyncFor, ast.comprehension)
        for node in self.__childrenInScope(loopNode):
            if isinstance(node, (ast.Assign)):
                for child in node.targets:
                    yield from self.__namesFromAssignments(child)
            if isinstance(node, loopTargets + (ast.AnnAssign, ast.AugAssign)):
                yield from self.__namesFromAssignments(node.target)

    def __namesFromAssignments(self, assignTarget):
        """
        Private method to get names of an assignment.

        @param assignTarget reference to the node to be processed
        @type ast.Node
        @yield name of the assignment
        @ytype str
        """
        if isinstance(assignTarget, ast.Name):
            yield assignTarget.id
        elif isinstance(assignTarget, ast.Starred):
            yield from self.__namesFromAssignments(assignTarget.value)
        elif isinstance(assignTarget, (ast.List, ast.Tuple)):
            for child in assignTarget.elts:
                yield from self.__namesFromAssignments(child)

    def __childrenInScope(self, node):
        """
        Private method to get all child nodes in the given scope.

        @param node reference to the node to be processed
        @type ast.Node
        @yield reference to a child node
        @ytype ast.Node
        """
        yield node
        if not isinstance(node, BugBearVisitor.FUNCTION_NODES):
            for child in ast.iter_child_nodes(node):
                yield from self.__childrenInScope(child)

    def __flattenExcepthandler(self, node):
        """
        Private method to flatten the list of exceptions handled by an except handler.

        @param node reference to the node to be processed
        @type ast.Node
        @yield reference to the exception type node
        @ytype ast.Node
        """
        if not isinstance(node, ast.Tuple):
            yield node
            return

        exprList = node.elts.copy()
        while len(exprList):
            expr = exprList.pop(0)
            if isinstance(expr, ast.Starred) and isinstance(
                expr.value, (ast.List, ast.Tuple)
            ):
                exprList.extend(expr.value.elts)
                continue
            yield expr

    def __checkRedundantExcepthandlers(self, names, node, inTryStar):
        """
        Private method to check for redundant exception types in an exception handler.

        @param names list of exception types to be checked
        @type list of ast.Name
        @param node reference to the exception handler node
        @type ast.ExceptionHandler
        @param inTryStar character indicating an 'except*' handler
        @type str
        @return tuple containing the error data
        @rtype tuple of (ast.Node, str, str, str, str)
        """
        redundantExceptions = {
            "OSError": {
                # All of these are actually aliases of OSError since Python 3.3
                "IOError",
                "EnvironmentError",
                "WindowsError",
                "mmap.error",
                "socket.error",
                "select.error",
            },
            "ValueError": {
                "binascii.Error",
            },
        }

        # See if any of the given exception names could be removed, e.g. from:
        #    (MyError, MyError)  # duplicate names  # noqa: M-891
        #    (MyError, BaseException)  # everything derives from the Base  # noqa: M-891
        #    (Exception, TypeError)  # builtins where one subclasses another
        # noqa: M-891
        #    (IOError, OSError)  # IOError is an alias of OSError since Python3.3
        # noqa: M-891
        # but note that other cases are impractical to handle from the AST.
        # We expect this is mostly useful for users who do not have the
        # builtin exception hierarchy memorised, and include a 'shadowed'
        # subtype without realising that it's redundant.
        good = sorted(set(names), key=names.index)
        if "BaseException" in good:
            good = ["BaseException"]
        # Remove redundant exceptions that the automatic system either handles
        # poorly (usually aliases) or can't be checked (e.g. it's not an
        # built-in exception).
        for primary, equivalents in redundantExceptions.items():
            if primary in good:
                good = [g for g in good if g not in equivalents]

        for name, other in itertools.permutations(tuple(good), 2):
            if (
                self.__typesafeIssubclass(
                    getattr(builtins, name, type), getattr(builtins, other, ())
                )
                and name in good
            ):
                good.remove(name)
        if good != names:
            desc = good[0] if len(good) == 1 else "({0})".format(", ".join(good))
            as_ = " as " + node.name if node.name is not None else ""
            return (node, "M-514", ", ".join(names), as_, desc, inTryStar)

        return None

    def __walkList(self, nodes):
        """
        Private method to walk a given list of nodes.

        @param nodes list of nodes to walk
        @type list of ast.Node
        @yield node references as determined by the ast.walk() function
        @ytype ast.Node
        """
        for node in nodes:
            yield from ast.walk(node)

    def __getNamesFromTuple(self, node):
        """
        Private method to get the names from an ast.Tuple node.

        @param node ast node to be processed
        @type ast.Tuple
        @yield names
        @ytype str
        """
        for dim in node.elts:
            if isinstance(dim, ast.Name):
                yield dim.id
            elif isinstance(dim, ast.Tuple):
                yield from self.__getNamesFromTuple(dim)

    def __getDictCompLoopAndNamedExprVarNames(self, node):
        """
        Private method to get the names of comprehension loop variables.

        @param node ast node to be processed
        @type ast.DictComp
        @yield loop variable names
        @ytype str
        """
        finder = NamedExprFinder()
        for gen in node.generators:
            if isinstance(gen.target, ast.Name):
                yield gen.target.id
            elif isinstance(gen.target, ast.Tuple):
                yield from self.__getNamesFromTuple(gen.target)

            finder.visit(gen.ifs)

        yield from finder.getNames().keys()

    def __inClassInit(self):
        """
        Private method to check, if we are inside an '__init__' method.

        @return flag indicating being within the '__init__' method
        @rtype bool
        """
        return (
            len(self.contexts) >= 2
            and isinstance(self.contexts[-2].node, ast.ClassDef)
            and isinstance(self.contexts[-1].node, ast.FunctionDef)
            and self.contexts[-1].node.name == "__init__"
        )

    def visit_Return(self, node):
        """
        Public method to handle 'Return' nodes.

        @param node reference to the node to be processed
        @type ast.Return
        """
        if self.__inClassInit() and node.value is not None:
            self.violations.append((node, "M-537"))

        self.generic_visit(node)

    def visit_Yield(self, node):
        """
        Public method to handle 'Yield' nodes.

        @param node reference to the node to be processed
        @type ast.Yield
        """
        if self.__inClassInit():
            self.violations.append((node, "M-537"))

        self.generic_visit(node)

    def visit_YieldFrom(self, node) -> None:
        """
        Public method to handle 'YieldFrom' nodes.

        @param node reference to the node to be processed
        @type ast.YieldFrom
        """
        if self.__inClassInit():
            self.violations.append((node, "M-537"))

        self.generic_visit(node)

    def visit(self, node):
        """
        Public method to traverse a given AST node.

        @param node AST node to be traversed
        @type ast.Node
        """
        isContextful = isinstance(node, BugBearVisitor.CONTEXTFUL_NODES)

        if isContextful:
            context = BugBearContext(node, [])
            self.contexts.append(context)

        self.nodeStack.append(node)
        self.nodeWindow.append(node)
        self.nodeWindow = self.nodeWindow[-BugBearVisitor.NodeWindowSize :]

        super().visit(node)

        self.nodeStack.pop()

        if isContextful:
            self.contexts.pop()

        self.__checkForM518(node)

    def visit_ExceptHandler(self, node):
        """
        Public method to handle exception handlers.

        @param node reference to the node to be processed
        @type ast.ExceptHandler
        """
        if node.type is None:
            # bare except is handled by pycodestyle already
            self.generic_visit(node)
            return

        oldM540CaughtException = self.__M540CaughtException
        if node.name is None:
            self.__M540CaughtException = None
        else:
            self.__M540CaughtException = M540CaughtException(node.name, False)

        names = self.__checkForM513_M514_M529_M530(node)

        if "BaseException" in names and not ExceptBaseExceptionVisitor(node).reRaised():
            self.violations.append((node, "M-536"))

        self.generic_visit(node)

        if (
            self.__M540CaughtException is not None
            and self.__M540CaughtException.hasNote
        ):
            self.violations.append((node, "M-540"))
        self.__M540CaughtException = oldM540CaughtException

    def visit_UAdd(self, node):
        """
        Public method to handle unary additions.

        @param node reference to the node to be processed
        @type ast.UAdd
        """
        trailingNodes = list(map(type, self.nodeWindow[-4:]))
        if trailingNodes == [ast.UnaryOp, ast.UAdd, ast.UnaryOp, ast.UAdd]:
            originator = self.nodeWindow[-4]
            self.violations.append((originator, "M-502"))

        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Public method to handle a function call.

        @param node reference to the node to be processed
        @type ast.Call
        """
        isM540AddNote = False

        if isinstance(node.func, ast.Attribute):
            self.__checkForM505(node)
            isM540AddNote = self.__checkForM540AddNote(node.func)
        else:
            with contextlib.suppress(AttributeError, IndexError):
                # bad super() call
                if isinstance(node.func, ast.Name) and node.func.id == "super":
                    args = node.args
                    if (
                        len(args) == 2
                        and isinstance(args[0], ast.Attribute)
                        and isinstance(args[0].value, ast.Name)
                        and args[0].value.id == "self"
                        and args[0].attr == "__class__"
                    ):
                        self.violations.append((node, "M-582"))

                # bad getattr and setattr
                if (
                    node.func.id in ("getattr", "hasattr")
                    and node.args[1].value == "__call__"
                ):
                    self.violations.append((node, "M-504"))
                if (
                    node.func.id == "getattr"
                    and len(node.args) == 2
                    and self.__isIdentifier(node.args[1])
                    and iskeyword(AstUtilities.getValue(node.args[1]))
                ):
                    self.violations.append((node, "M-509"))
                elif (
                    node.func.id == "setattr"
                    and len(node.args) == 3
                    and self.__isIdentifier(node.args[1])
                    and iskeyword(AstUtilities.getValue(node.args[1]))
                ):
                    self.violations.append((node, "M-510"))

        self.__checkForM526(node)

        self.__checkForM528(node)
        self.__checkForM534(node)
        self.__checkForM539(node)

        # no need for copying, if used in nested calls it will be set to None
        currentM540CaughtException = self.__M540CaughtException
        if not isM540AddNote:
            self.__checkForM540Usage(node.args)
            self.__checkForM540Usage(node.keywords)

        self.generic_visit(node)

        if isM540AddNote:
            # Avoid nested calls within the parameter list using the variable itself.
            # e.g. `e.add_note(str(e))`
            self.__M540CaughtException = currentM540CaughtException

    def visit_Module(self, node):
        """
        Public method to handle a module node.

        @param node reference to the node to be processed
        @type ast.Module
        """
        self.generic_visit(node)

    def visit_Assign(self, node):
        """
        Public method to handle assignments.

        @param node reference to the node to be processed
        @type ast.Assign
        """
        self.__checkForM540Usage(node.value)
        if len(node.targets) == 1:
            target = node.targets[0]
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and (target.value.id, target.attr) == ("os", "environ")
            ):
                self.violations.append((node, "M-503"))

        self.generic_visit(node)

    def visit_For(self, node):
        """
        Public method to handle 'for' statements.

        @param node reference to the node to be processed
        @type ast.For
        """
        self.__checkForM507(node)
        self.__checkForM520(node)
        self.__checkForM523(node)
        self.__checkForM531(node)
        self.__checkForM569(node)

        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        """
        Public method to handle 'for' statements.

        @param node reference to the node to be processed
        @type ast.AsyncFor
        """
        self.__checkForM507(node)
        self.__checkForM520(node)
        self.__checkForM523(node)
        self.__checkForM531(node)

        self.generic_visit(node)

    def visit_While(self, node):
        """
        Public method to handle 'while' statements.

        @param node reference to the node to be processed
        @type ast.While
        """
        self.__checkForM523(node)

        self.generic_visit(node)

    def visit_ListComp(self, node):
        """
        Public method to handle list comprehensions.

        @param node reference to the node to be processed
        @type ast.ListComp
        """
        self.__checkForM523(node)

        self.generic_visit(node)

    def visit_SetComp(self, node):
        """
        Public method to handle set comprehensions.

        @param node reference to the node to be processed
        @type ast.SetComp
        """
        self.__checkForM523(node)

        self.generic_visit(node)

    def visit_DictComp(self, node):
        """
        Public method to handle dictionary comprehensions.

        @param node reference to the node to be processed
        @type ast.DictComp
        """
        self.__checkForM523(node)
        self.__checkForM535(node)

        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        """
        Public method to handle generator expressions.

        @param node reference to the node to be processed
        @type ast.GeneratorExp
        """
        self.__checkForM523(node)

        self.generic_visit(node)

    def visit_Assert(self, node):
        """
        Public method to handle 'assert' statements.

        @param node reference to the node to be processed
        @type ast.Assert
        """
        if (
            AstUtilities.isNameConstant(node.test)
            and AstUtilities.getValue(node.test) is False
        ):
            self.violations.append((node, "M-511"))

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
        Public method to handle async function definitions.

        @param node reference to the node to be processed
        @type ast.AsyncFunctionDef
        """
        self.__checkForM506_M508(node)

        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Public method to handle function definitions.

        @param node reference to the node to be processed
        @type ast.FunctionDef
        """
        self.__checkForM506_M508(node)
        self.__checkForM519(node)
        self.__checkForM521(node)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Public method to handle class definitions.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """
        self.__checkForM521(node)
        self.__checkForM524_M527(node)

        self.generic_visit(node)

    def visit_Try(self, node):
        """
        Public method to handle 'try' statements.

        @param node reference to the node to be processed
        @type ast.Try
        """
        self.__checkForM512(node)
        self.__checkForM525(node)

        self.generic_visit(node)

    def visit_TryStar(self, node):
        """
        Public method to handle 'except*' statements.

        @param node reference to the node to be processed
        @type ast.TryStar
        """
        outerTryStar = self.__inTryStar
        self.__inTryStar = "*"
        self.visit_Try(node)
        self.__inTryStar = outerTryStar

    def visit_Compare(self, node):
        """
        Public method to handle comparison statements.

        @param node reference to the node to be processed
        @type ast.Compare
        """
        self.__checkForM515(node)

        self.generic_visit(node)

    def visit_Raise(self, node):
        """
        Public method to handle 'raise' statements.

        @param node reference to the node to be processed
        @type ast.Raise
        """
        if node.exc is None:
            self.__M540CaughtException = None
        else:
            self.__checkForM540Usage(node.exc)
            self.__checkForM540Usage(node.cause)
        self.__checkForM516(node)

        self.generic_visit(node)

    def visit_With(self, node):
        """
        Public method to handle 'with' statements.

        @param node reference to the node to be processed
        @type ast.With
        """
        self.__checkForM517(node)
        self.__checkForM522(node)

        self.generic_visit(node)

    def visit_JoinedStr(self, node):
        """
        Public method to handle f-string arguments.

        @param node reference to the node to be processed
        @type ast.JoinedStr
        """
        for value in node.values:
            if isinstance(value, ast.FormattedValue):
                return

        self.violations.append((node, "M-581"))

    def visit_AnnAssign(self, node):
        """
        Public method to check annotated assign statements.

        @param node reference to the node to be processed
        @type ast.AnnAssign
        """
        self.__checkForM532(node)
        self.__checkForM540Usage(node.value)

        self.generic_visit(node)

    def visit_Import(self, node):
        """
        Public method to check imports.

        @param node reference to the node to be processed
        @type ast.Import
        """
        self.__checkForM505(node)

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """
        Public method to check from imports.

        @param node reference to the node to be processed
        @type ast.Import
        """
        self.visit_Import(node)

    def visit_Set(self, node):
        """
        Public method to check a set.

        @param node reference to the node to be processed
        @type ast.Set
        """
        self.__checkForM533(node)

        self.generic_visit(node)

    def visit_Dict(self, node):
        """
        Public method to check a dictionary.

        @param node reference to the node to be processed
        @type ast.Dict
        """
        self.__checkForM541(node)

        self.generic_visit(node)

    def __checkForM505(self, node):
        """
        Private method to check the use of *strip().

        @param node reference to the node to be processed
        @type ast.Call
        """
        if isinstance(node, ast.Import):
            for name in node.names:
                self.__M505Imports.add(name.asname or name.name)
        elif isinstance(node, ast.ImportFrom):
            for name in node.names:
                self.__M505Imports.add(f"{node.module}.{name.name or name.asname}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr not in ("lstrip", "rstrip", "strip"):
                return  # method name doesn't match

            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in self.__M505Imports
            ):
                return  # method is being run on an imported module

            if len(node.args) != 1 or not AstUtilities.isString(node.args[0]):
                return  # used arguments don't match the builtin strip

            value = AstUtilities.getValue(node.args[0])
            if len(value) == 1:
                return  # stripping just one character

            if len(value) == len(set(value)):
                return  # no characters appear more than once

            self.violations.append((node, "M-505"))

    def __checkForM506_M508(self, node):
        """
        Private method to check the use of mutable literals, comprehensions and calls.

        @param node reference to the node to be processed
        @type ast.AsyncFunctionDef or ast.FunctionDef
        """
        visitor = FunctionDefDefaultsVisitor("M-506", "M-508")
        visitor.visit(node.args.defaults + node.args.kw_defaults)
        self.violations.extend(visitor.errors)

    def __checkForM507(self, node):
        """
        Private method to check for unused loop variables.

        @param node reference to the node to be processed
        @type ast.For or ast.AsyncFor
        """
        targets = NameFinder()
        targets.visit(node.target)
        ctrlNames = set(filter(lambda s: not s.startswith("_"), targets.getNames()))
        body = NameFinder()
        for expr in node.body:
            body.visit(expr)
        usedNames = set(body.getNames())
        for name in sorted(ctrlNames - usedNames):
            n = targets.getNames()[name][0]
            self.violations.append((n, "M-507", name))

    def __checkForM512(self, node):
        """
        Private method to check for return/continue/break inside finally blocks.

        @param node reference to the node to be processed
        @type ast.Try
        """

        def _loop(node, badNodeTypes):
            if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                return

            if isinstance(node, (ast.While, ast.For)):
                badNodeTypes = (ast.Return,)

            elif isinstance(node, badNodeTypes):
                self.violations.append((node, "M-512", self.__inTryStar))

            for child in ast.iter_child_nodes(node):
                _loop(child, badNodeTypes)

        for child in node.finalbody:
            _loop(child, (ast.Return, ast.Continue, ast.Break))

    def __checkForM513_M514_M529_M530(self, node):
        """
        Private method to check various exception handler situations.

        @param node reference to the node to be processed
        @type ast.ExceptHandler
        @return list of exception handler names
        @rtype list of str
        """
        handlers = self.__flattenExcepthandler(node.type)
        names = []
        badHandlers = []
        ignoredHandlers = []

        for handler in handlers:
            if isinstance(handler, (ast.Name, ast.Attribute)):
                name = self.toNameStr(handler)
                if name is None:
                    ignoredHandlers.append(handler)
                else:
                    names.append(name)
            elif isinstance(handler, (ast.Call, ast.Starred)):
                ignoredHandlers.append(handler)
            else:
                badHandlers.append(handler)
        if badHandlers:
            self.violations.append((node, "M-530"))
        if len(names) == 0 and not badHandlers and not ignoredHandlers:
            self.violations.append((node, "M-529", self.__inTryStar))
        elif (
            len(names) == 1
            and not badHandlers
            and not ignoredHandlers
            and isinstance(node.type, ast.Tuple)
        ):
            self.violations.append((node, "M-513", *names, self.__inTryStar))
        else:
            maybeError = self.__checkRedundantExcepthandlers(
                names, node, self.__inTryStar
            )
            if maybeError is not None:
                self.violations.append(maybeError)
        return names

    def __checkForM515(self, node):
        """
        Private method to check for pointless comparisons.

        @param node reference to the node to be processed
        @type ast.Compare
        """
        if isinstance(self.nodeStack[-2], ast.Expr):
            self.violations.append((node, "M-515"))

    def __checkForM516(self, node):
        """
        Private method to check for raising a literal instead of an exception.

        @param node reference to the node to be processed
        @type ast.Raise
        """
        if (
            AstUtilities.isNameConstant(node.exc)
            or AstUtilities.isNumber(node.exc)
            or AstUtilities.isString(node.exc)
        ):
            self.violations.append((node, "M-516"))

    def __checkForM517(self, node):
        """
        Private method to check for use of the evil syntax
        'with assertRaises(Exception): or 'with pytest.raises(Exception):'.

        @param node reference to the node to be processed
        @type ast.With
        """
        item = node.items[0]
        itemContext = item.context_expr
        if (
            hasattr(itemContext, "func")
            and (
                (
                    isinstance(itemContext.func, ast.Attribute)
                    and (
                        itemContext.func.attr == "assertRaises"
                        or (
                            itemContext.func.attr == "raises"
                            and isinstance(itemContext.func.value, ast.Name)
                            and itemContext.func.value.id == "pytest"
                            and "match" not in (kwd.arg for kwd in itemContext.keywords)
                        )
                    )
                )
                or (
                    isinstance(itemContext.func, ast.Name)
                    and itemContext.func.id == "raises"
                    and isinstance(itemContext.func.ctx, ast.Load)
                    and "pytest.raises" in self.__M505Imports
                    and "match" not in (kwd.arg for kwd in itemContext.keywords)
                )
            )
            and len(itemContext.args) == 1
            and isinstance(itemContext.args[0], ast.Name)
            and itemContext.args[0].id in ("Exception", "BaseException")
            and not item.optional_vars
        ):
            self.violations.append((node, "M-517"))

    def __checkForM518(self, node):
        """
        Private method to check for useless expressions.

        @param node reference to the node to be processed
        @type ast.FunctionDef
        """
        if not isinstance(node, ast.Expr):
            return

        if isinstance(
            node.value,
            (ast.List, ast.Set, ast.Dict, ast.Tuple),
        ) or (
            isinstance(node.value, ast.Constant)
            and (
                isinstance(
                    node.value.value,
                    (int, float, complex, bytes, bool),
                )
                or node.value.value is None
            )
        ):
            self.violations.append((node, "M-518", node.value.__class__.__name__))

    def __checkForM519(self, node):
        """
        Private method to check for use of 'functools.lru_cache' or 'functools.cache'.

        @param node reference to the node to be processed
        @type ast.FunctionDef
        """
        caches = {
            "functools.cache",
            "functools.lru_cache",
            "cache",
            "lru_cache",
        }

        if (
            len(node.decorator_list) == 0
            or len(self.contexts) < 2
            or not isinstance(self.contexts[-2].node, ast.ClassDef)
        ):
            return

        # Preserve decorator order so we can get the lineno from the decorator node
        # rather than the function node (this location definition changes in Python 3.8)
        resolvedDecorators = (
            ".".join(composeCallPath(decorator)) for decorator in node.decorator_list
        )
        for idx, decorator in enumerate(resolvedDecorators):
            if decorator in {"classmethod", "staticmethod"}:
                return

            if decorator in caches:
                self.violations.append((node.decorator_list[idx], "M-519"))
                return

    def __checkForM520(self, node):
        """
        Private method to check for a loop that modifies its iterable.

        @param node reference to the node to be processed
        @type ast.For or ast.AsyncFor
        """
        targets = NameFinder()
        targets.visit(node.target)
        ctrlNames = set(targets.getNames())

        iterset = M520NameFinder()
        iterset.visit(node.iter)
        itersetNames = set(iterset.getNames())

        for name in sorted(ctrlNames):
            if name in itersetNames:
                n = targets.getNames()[name][0]
                self.violations.append((n, "M-520"))

    def __checkForM521(self, node):
        """
        Private method to check for use of an f-string as docstring.

        @param node reference to the node to be processed
        @type ast.FunctionDef or ast.ClassDef
        """
        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.JoinedStr)
        ):
            self.violations.append((node.body[0].value, "M-521"))

    def __checkForM522(self, node):
        """
        Private method to check for use of an f-string as docstring.

        @param node reference to the node to be processed
        @type ast.With
        """
        item = node.items[0]
        itemContext = item.context_expr
        if (
            hasattr(itemContext, "func")
            and hasattr(itemContext.func, "value")
            and hasattr(itemContext.func.value, "id")
            and itemContext.func.value.id == "contextlib"
            and hasattr(itemContext.func, "attr")
            and itemContext.func.attr == "suppress"
            and len(itemContext.args) == 0
        ):
            self.violations.append((node, "M-522"))

    def __checkForM523(self, loopNode):
        """
        Private method to check that functions (including lambdas) do not use loop
        variables.

        @param loopNode reference to the node to be processed
        @type ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp,ast.DictComp,
            or ast.GeneratorExp
        """
        safe_functions = []
        suspiciousVariables = []
        for node in ast.walk(loopNode):
            # check if function is immediately consumed to avoid false alarm
            if isinstance(node, ast.Call):
                # check for filter&reduce
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id in ("filter", "reduce", "map")
                ) or (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "reduce"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "functools"
                ):
                    for arg in node.args:
                        if isinstance(arg, BugBearVisitor.FUNCTION_NODES):
                            safe_functions.append(arg)

                # check for key=
                for keyword in node.keywords:
                    if keyword.arg == "key" and isinstance(
                        keyword.value, BugBearVisitor.FUNCTION_NODES
                    ):
                        safe_functions.append(keyword.value)

            # mark `return lambda: x` as safe
            # does not (currently) check inner lambdas in a returned expression
            # e.g. `return (lambda: x, )
            if isinstance(node, ast.Return) and isinstance(
                node.value, BugBearVisitor.FUNCTION_NODES
            ):
                safe_functions.append(node.value)

            # find unsafe functions
            if (
                isinstance(node, BugBearVisitor.FUNCTION_NODES)
                and node not in safe_functions
            ):
                argnames = {
                    arg.arg for arg in ast.walk(node.args) if isinstance(arg, ast.arg)
                }
                if isinstance(node, ast.Lambda):
                    bodyNodes = ast.walk(node.body)
                else:
                    bodyNodes = itertools.chain.from_iterable(map(ast.walk, node.body))
                errors = []
                for name in bodyNodes:
                    if isinstance(name, ast.Name) and name.id not in argnames:
                        if isinstance(name.ctx, ast.Load):
                            errors.append((name.lineno, name.col_offset, name.id, name))
                        elif isinstance(name.ctx, ast.Store):
                            argnames.add(name.id)
                for err in errors:
                    if err[2] not in argnames and err not in self.__M523Seen:
                        self.__M523Seen.add(err)  # dedupe across nested loops
                        suspiciousVariables.append(err)

        if suspiciousVariables:
            reassignedInLoop = set(self.__getAssignedNames(loopNode))

        for err in sorted(suspiciousVariables):
            if reassignedInLoop.issuperset(err[2]):
                self.violations.append((err[3], "M-523", err[2]))

    def __checkForM524_M527(self, node):
        """
        Private method to check for inheritance from abstract classes in abc and lack of
        any methods decorated with abstract*.

        @param node reference to the node to be processed
        @type ast.ClassDef
        """  # __IGNORE_WARNING_D-234r__

        def isAbcClass(value, name="ABC"):
            if isinstance(value, ast.keyword):
                return value.arg == "metaclass" and isAbcClass(value.value, "ABCMeta")

            # class foo(ABC)
            # class foo(abc.ABC)
            return (isinstance(value, ast.Name) and value.id == name) or (
                isinstance(value, ast.Attribute)
                and value.attr == name
                and isinstance(value.value, ast.Name)
                and value.value.id == "abc"
            )

        def isAbstractDecorator(expr):
            return (isinstance(expr, ast.Name) and expr.id[:8] == "abstract") or (
                isinstance(expr, ast.Attribute) and expr.attr[:8] == "abstract"
            )

        def isOverload(expr):
            return (isinstance(expr, ast.Name) and expr.id == "overload") or (
                isinstance(expr, ast.Attribute) and expr.attr == "overload"
            )

        def emptyBody(body):
            def isStrOrEllipsis(node):
                return isinstance(node, ast.Constant) and (
                    node.value is Ellipsis or isinstance(node.value, str)
                )

            # Function body consist solely of `pass`, `...`, and/or (doc)string literals
            return all(
                isinstance(stmt, ast.Pass)
                or (isinstance(stmt, ast.Expr) and isStrOrEllipsis(stmt.value))
                for stmt in body
            )

        # don't check multiple inheritance
        if len(node.bases) + len(node.keywords) > 1:
            return

        # only check abstract classes
        if not any(map(isAbcClass, (*node.bases, *node.keywords))):
            return

        hasMethod = False
        hasAbstractMethod = False

        if not any(map(isAbcClass, (*node.bases, *node.keywords))):
            return

        for stmt in node.body:
            # Ignore abc's that declares a class attribute that must be set
            if isinstance(stmt, ast.AnnAssign) and stmt.value is None:
                hasAbstractMethod = True
                continue

            # only check function defs
            if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            hasMethod = True

            hasAbstractDecorator = any(map(isAbstractDecorator, stmt.decorator_list))

            hasAbstractMethod |= hasAbstractDecorator

            if (
                not hasAbstractDecorator
                and emptyBody(stmt.body)
                and not any(map(isOverload, stmt.decorator_list))
            ):
                self.violations.append((stmt, "M-527", stmt.name))

        if hasMethod and not hasAbstractMethod:
            self.violations.append((node, "M-524", node.name))

    def __checkForM525(self, node):
        """
        Private method to check for exceptions being handled multiple times.

        @param node reference to the node to be processed
        @type ast.Try
        """
        seen = []

        for handler in node.handlers:
            if isinstance(handler.type, (ast.Name, ast.Attribute)):
                name = ".".join(composeCallPath(handler.type))
                seen.append(name)
            elif isinstance(handler.type, ast.Tuple):
                # to avoid checking the same as M514, remove duplicates per except
                uniques = set()
                for entry in handler.type.elts:
                    name = ".".join(composeCallPath(entry))
                    uniques.add(name)
                seen.extend(uniques)

        # sort to have a deterministic output
        duplicates = sorted({x for x in seen if seen.count(x) > 1})
        for duplicate in duplicates:
            self.violations.append((node, "M-525", duplicate, self.__inTryStar))

    def __checkForM526(self, node):
        """
        Private method to check for Star-arg unpacking after keyword argument.

        @param node reference to the node to be processed
        @type ast.Call
        """
        if not node.keywords:
            return

        starreds = [arg for arg in node.args if isinstance(arg, ast.Starred)]
        if not starreds:
            return

        firstKeyword = node.keywords[0].value
        for starred in starreds:
            if (starred.lineno, starred.col_offset) > (
                firstKeyword.lineno,
                firstKeyword.col_offset,
            ):
                self.violations.append((node, "M-526"))

    def __checkForM528(self, node):
        """
        Private method to check for warn without stacklevel.

        @param node reference to the node to be processed
        @type ast.Call
        """
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "warn"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "warnings"
            and not any(kw.arg == "stacklevel" for kw in node.keywords)
            and len(node.args) < 3
            and not any(isinstance(a, ast.Starred) for a in node.args)
            and not any(kw.arg is None for kw in node.keywords)
        ):
            self.violations.append((node, "M-528"))

    def __checkForM531(self, loopNode):
        """
        Private method to check that 'itertools.groupby' isn't iterated over more than
        once.

        A warning is emitted when the generator returned by 'groupby()' is used
        more than once inside a loop body or when it's used in a nested loop.

        @param loopNode reference to the node to be processed
        @type ast.For or ast.AsyncFor
        """
        # for <loop_node.target> in <loop_node.iter>: ...
        if isinstance(loopNode.iter, ast.Call):
            node = loopNode.iter
            if (isinstance(node.func, ast.Name) and node.func.id in ("groupby",)) or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "groupby"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "itertools"
            ):
                # We have an invocation of groupby which is a simple unpacking
                if isinstance(loopNode.target, ast.Tuple) and isinstance(
                    loopNode.target.elts[1], ast.Name
                ):
                    groupName = loopNode.target.elts[1].id
                else:
                    # Ignore any 'groupby()' invocation that isn't unpacked
                    return

                numUsages = 0
                for node in self.__walkList(loopNode.body):
                    # Handled nested loops
                    if isinstance(node, ast.For):
                        for nestedNode in self.__walkList(node.body):
                            if (
                                isinstance(nestedNode, ast.Name)
                                and nestedNode.id == groupName
                            ):
                                self.violations.append((nestedNode, "M-531"))

                    # Handle multiple uses
                    if isinstance(node, ast.Name) and node.id == groupName:
                        numUsages += 1
                        if numUsages > 1:
                            self.violations.append((nestedNode, "M-531"))

    def __checkForM532(self, node):
        """
        Private method to check for possible unintentional typing annotation.

        @param node reference to the node to be processed
        @type ast.AnnAssign
        """
        if (
            node.value is None
            and hasattr(node.target, "value")
            and isinstance(node.target.value, ast.Name)
            and (
                isinstance(node.target, ast.Subscript)
                or (
                    isinstance(node.target, ast.Attribute)
                    and node.target.value.id != "self"
                )
            )
        ):
            self.violations.append((node, "M-532"))

    def __checkForM533(self, node):
        """
        Private method to check a set for duplicate items.

        @param node reference to the node to be processed
        @type ast.Set
        """
        seen = set()
        for elt in node.elts:
            if not isinstance(elt, ast.Constant):
                continue
            if elt.value in seen:
                self.violations.append((node, "M-533", repr(elt.value)))
            else:
                seen.add(elt.value)

    def __checkForM534(self, node):
        """
        Private method to check that re.sub/subn/split arguments flags/count/maxsplit
        are passed as keyword arguments.

        @param node reference to the node to be processed
        @type ast.Call
        """
        if not isinstance(node.func, ast.Attribute):
            return
        func = node.func
        if not isinstance(func.value, ast.Name) or func.value.id != "re":
            return

        def check(numArgs, paramName):
            if len(node.args) > numArgs:
                arg = node.args[numArgs]
                self.violations.append((arg, "M-534", func.attr, paramName))

        if func.attr in ("sub", "subn"):
            check(3, "count")
        elif func.attr == "split":
            check(2, "maxsplit")

    def __checkForM535(self, node):
        """
        Private method to check that a static key isn't used in a dict comprehension.

        Record a warning if a likely unchanging key is used - either a constant,
        or a variable that isn't coming from the generator expression.

        @param node reference to the node to be processed
        @type ast.DictComp
        """
        if isinstance(node.key, ast.Constant):
            self.violations.append((node, "M-535", node.key.value))
        elif isinstance(
            node.key, ast.Name
        ) and node.key.id not in self.__getDictCompLoopAndNamedExprVarNames(node):
            self.violations.append((node, "M-535", node.key.id))

    def __checkForM539(self, node):
        """
        Private method to check for correct ContextVar usage.

        @param node reference to the node to be processed
        @type ast.Call
        """
        if not (
            (isinstance(node.func, ast.Name) and node.func.id == "ContextVar")
            or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "ContextVar"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "contextvars"
            )
        ):
            return

        # ContextVar only takes one kw currently, but better safe than sorry
        for kw in node.keywords:
            if kw.arg == "default":
                break
        else:
            return

        visitor = FunctionDefDefaultsVisitor("M-539", "M-539")
        visitor.visit(kw.value)
        self.violations.extend(visitor.errors)

    def __checkForM540AddNote(self, node):
        """
        Private method to check add_note usage.

        @param node reference to the node to be processed
        @type ast.Attribute
        @return flag
        @rtype bool
        """
        if (
            node.attr == "add_note"
            and isinstance(node.value, ast.Name)
            and self.__M540CaughtException
            and node.value.id == self.__M540CaughtException.name
        ):
            self.__M540CaughtException.hasNote = True
            return True

        return False

    def __checkForM540Usage(self, node):
        """
        Private method to check the usage of exceptions with added note.

        @param node reference to the node to be processed
        @type ast.expr or None
        """  # noqa: D-234y

        def superwalk(node: ast.AST | list[ast.AST]):
            """
            Function to walk an AST node or a list of AST nodes.

            @param node reference to the node or a list of nodes to be processed
            @type ast.AST or list[ast.AST]
            @yield next node to be processed
            @ytype ast.AST
            """
            if isinstance(node, list):
                for n in node:
                    yield from ast.walk(n)
            else:
                yield from ast.walk(node)

        if not self.__M540CaughtException or node is None:
            return

        for n in superwalk(node):
            if isinstance(n, ast.Name) and n.id == self.__M540CaughtException.name:
                self.__M540CaughtException = None
                break

    def __checkForM541(self, node):
        """
        Private method to check for duplicate key value pairs in a dictionary literal.

        @param node reference to the node to be processed
        @type ast.Dict
        """  # noqa: D-234r

        def convertToValue(item):
            """
            Function to extract the value of a given item.

            @param item node to extract value from
            @type ast.Ast
            @return value of the node
            @rtype Any
            """
            if isinstance(item, ast.Constant):
                return item.value
            elif isinstance(item, ast.Tuple):
                return tuple(convertToValue(i) for i in item.elts)
            elif isinstance(item, ast.Name):
                return M541VariableKeyType(item.id)
            else:
                return M541UnhandledKeyType()

        keys = [convertToValue(key) for key in node.keys]
        keyCounts = Counter(keys)
        duplicateKeys = [key for key, count in keyCounts.items() if count > 1]
        for key in duplicateKeys:
            keyIndices = [i for i, iKey in enumerate(keys) if iKey == key]
            seen = set()
            for index in keyIndices:
                value = convertToValue(node.values[index])
                if value in seen:
                    keyNode = node.keys[index]
                    self.violations.append((keyNode, "M-541"))
                seen.add(value)

    def __checkForM569(self, node):
        """
        Private method to check for changes to a loop's mutable iterable.

        @param node loop node to be checked
        @type ast.For
        """
        if isinstance(node.iter, ast.Name):
            name = self.toNameStr(node.iter)
        elif isinstance(node.iter, ast.Attribute):
            name = self.toNameStr(node.iter)
        else:
            return
        checker = M569Checker(name, self)
        checker.visit(node.body)
        for mutation in checker.mutations:
            self.violations.append((mutation, "M-569"))


class M569Checker(ast.NodeVisitor):
    """
    Class traversing a 'for' loop body to check for modifications to a loop's
    mutable iterable.
    """

    # https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types
    MUTATING_FUNCTIONS = (
        "append",
        "sort",
        "reverse",
        "remove",
        "clear",
        "extend",
        "insert",
        "pop",
        "popitem",
    )

    def __init__(self, name, bugbear):
        """
        Constructor

        @param name name of the iterator
        @type str
        @param bugbear reference to the bugbear visitor
        @type BugBearVisitor
        """
        self.__name = name
        self.__bb = bugbear
        self.mutations = []

    def visit_Delete(self, node):
        """
        Public method handling 'Delete' nodes.

        @param node reference to the node to be processed
        @type ast.Delete
        """
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                name = self.__bb.toNameStr(target.value)
            elif isinstance(target, (ast.Attribute, ast.Name)):
                name = self.__bb.toNameStr(target)
            else:
                name = ""  # fallback
                self.generic_visit(target)

            if name == self.__name:
                self.mutations.append(node)

    def visit_Call(self, node):
        """
        Public method handling 'Call' nodes.

        @param node reference to the node to be processed
        @type ast.Call
        """
        if isinstance(node.func, ast.Attribute):
            name = self.__bb.toNameStr(node.func.value)
            functionObject = name
            functionName = node.func.attr

            if (
                functionObject == self.__name
                and functionName in self.MUTATING_FUNCTIONS
            ):
                self.mutations.append(node)

        self.generic_visit(node)

    def visit(self, node):
        """
        Public method to inspect an ast node.

        Like super-visit but supports iteration over lists.

        @param node AST node to be traversed
        @type TYPE
        @return reference to the last processed node
        @rtype ast.Node
        """
        if not isinstance(node, list):
            return super().visit(node)

        for elem in node:
            super().visit(elem)
        return node


class NamedExprFinder(ast.NodeVisitor):
    """
    Class to extract names defined through an ast.NamedExpr.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.__names = {}

    def visit_NamedExpr(self, node: ast.NamedExpr):
        """
        Public method handling 'NamedExpr' nodes.

        @param node reference to the node to be processed
        @type ast.NamedExpr
        """
        self.__names.setdefault(node.target.id, []).append(node.target)

        self.generic_visit(node)

    def visit(self, node):
        """
        Public method to traverse a given AST node.

        Like super-visit but supports iteration over lists.

        @param node AST node to be traversed
        @type TYPE
        @return reference to the last processed node
        @rtype ast.Node
        """
        if not isinstance(node, list):
            super().visit(node)

        for elem in node:
            super().visit(elem)

        return node

    def getNames(self):
        """
        Public method to return the extracted names and Name nodes.

        @return dictionary containing the names as keys and the list of nodes
        @rtype dict
        """
        return self.__names


class ExceptBaseExceptionVisitor(ast.NodeVisitor):
    """
    Class to determine, if a 'BaseException' is re-raised.
    """

    def __init__(self, exceptNode):
        """
        Constructor

        @param exceptNode exception node to be inspected
        @type ast.ExceptHandler
        """
        super().__init__()
        self.__root = exceptNode
        self.__reRaised = False

    def reRaised(self) -> bool:
        """
        Public method to check, if the exception is re-raised.

        @return flag indicating a re-raised exception
        @rtype bool
        """
        self.visit(self.__root)
        return self.__reRaised

    def visit_Raise(self, node):
        """
        Public method to handle 'Raise' nodes.

        If we find a corresponding `raise` or `raise e` where e was from
        `except BaseException as e:` then we mark re_raised as True and can
        stop scanning.

        @param node reference to the node to be processed
        @type ast.Raise
        """
        if node.exc is None or (
            isinstance(node.exc, ast.Name) and node.exc.id == self.__root.name
        ):
            self.__reRaised = True
            return

        super().generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        """
        Public method to handle 'ExceptHandler' nodes.

        @param node reference to the node to be processed
        @type ast.ExceptHandler
        """
        if node is not self.__root:
            return  # entered a nested except - stop searching

        super().generic_visit(node)


class FunctionDefDefaultsVisitor(ast.NodeVisitor):
    """
    Class used by M506, M508 and M539.
    """

    def __init__(
        self,
        errorCodeCalls,  # M506 or M539
        errorCodeLiterals,  # M508 or M539
    ):
        """
        Constructor

        @param errorCodeCalls error code for ast.Call nodes
        @type str
        @param errorCodeLiterals error code for literal nodes
        @type str
        """
        self.__errorCodeCalls = errorCodeCalls
        self.__errorCodeLiterals = errorCodeLiterals
        for nodeType in BugbearMutableLiterals + BugbearMutableComprehensions:
            setattr(
                self, f"visit_{nodeType}", self.__visitMutableLiteralOrComprehension
            )
        self.errors = []
        self.__argDepth = 0

        super().__init__()

    def __visitMutableLiteralOrComprehension(self, node):
        """
        Private method to flag mutable literals and comprehensions.

        @param node AST node to be processed
        @type ast.Dict, ast.List, ast.Set, ast.ListComp, ast.DictComp or ast.SetComp
        """
        # Flag M506 if mutable literal/comprehension is not nested.
        # We only flag these at the top level of the expression as we
        # cannot easily guarantee that nested mutable structures are not
        # made immutable by outer operations, so we prefer no false positives.
        # e.g.
        # >>> def this_is_fine(a=frozenset({"a", "b", "c"})): ...
        #
        # >>> def this_is_not_fine_but_hard_to_detect(a=(lambda x: x)([1, 2, 3]))
        #
        # We do still search for cases of B008 within mutable structures though.
        if self.__argDepth == 1:
            self.errors.append((node, self.__errorCodeCalls))

        # Check for nested functions.
        self.generic_visit(node)

    def visit_Call(self, node):
        """
        Public method to process Call nodes.

        @param node AST node to be processed
        @type ast.Call
        """
        callPath = ".".join(composeCallPath(node.func))
        if callPath in BugbearMutableCalls:
            self.errors.append((node, self.__errorCodeCalls))
            self.generic_visit(node)
            return

        if callPath in BugbearImmutableCalls:
            self.generic_visit(node)
            return

        # Check if function call is actually a float infinity/NaN literal
        if callPath == "float" and len(node.args) == 1:
            try:
                value = float(ast.literal_eval(node.args[0]))
            except Exception:  # secok
                pass
            else:
                if math.isfinite(value):
                    self.errors.append((node, self.__errorCodeLiterals))
        else:
            self.errors.append((node, self.__errorCodeLiterals))

        # Check for nested functions.
        self.generic_visit(node)

    def visit_Lambda(self, node):
        """
        Public method to process Lambda nodes.

        @param node AST node to be processed
        @type ast.Lambda
        """
        # Don't recurse into lambda expressions
        # as they are evaluated at call time.
        pass

    def visit(self, node):
        """
        Public method to traverse an AST node or a list of AST nodes.

        This is an extended method that can also handle a list of AST nodes.

        @param node AST node or list of AST nodes to be processed
        @type ast.AST or list of ast.AST
        """
        self.__argDepth += 1
        if isinstance(node, list):
            for elem in node:
                if elem is not None:
                    super().visit(elem)
        else:
            super().visit(node)
        self.__argDepth -= 1


class NameFinder(ast.NodeVisitor):
    """
    Class to extract a name out of a tree of nodes.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.__names = {}

    def visit_Name(self, node):
        """
        Public method to handle 'Name' nodes.

        @param node reference to the node to be processed
        @type ast.Name
        """
        self.__names.setdefault(node.id, []).append(node)

    def visit(self, node):
        """
        Public method to traverse a given AST node.

        @param node AST node to be traversed
        @type ast.Node
        @return reference to the last processed node
        @rtype ast.Node
        """
        if isinstance(node, list):
            for elem in node:
                super().visit(elem)
            return node
        else:
            return super().visit(node)

    def getNames(self):
        """
        Public method to return the extracted names and Name nodes.

        @return dictionary containing the names as keys and the list of nodes
        @rtype dict
        """
        return self.__names


class M520NameFinder(NameFinder):
    """
    Class to extract a name out of a tree of nodes ignoring names defined within the
    local scope of a comprehension.
    """

    def visit_GeneratorExp(self, node):
        """
        Public method to handle a generator expressions.

        @param node reference to the node to be processed
        @type ast.GeneratorExp
        """
        self.visit(node.generators)

    def visit_ListComp(self, node):
        """
        Public method  to handle a list comprehension.

        @param node reference to the node to be processed
        @type TYPE
        """
        self.visit(node.generators)

    def visit_DictComp(self, node):
        """
        Public method  to handle a dictionary comprehension.

        @param node reference to the node to be processed
        @type TYPE
        """
        self.visit(node.generators)

    def visit_comprehension(self, node):
        """
        Public method  to handle the 'for' of a comprehension.

        @param node reference to the node to be processed
        @type ast.comprehension
        """
        self.visit(node.iter)

    def visit_Lambda(self, node):
        """
        Public method  to handle a Lambda function.

        @param node reference to the node to be processed
        @type ast.Lambda
        """
        self.visit(node.body)
        for lambdaArg in node.args.args:
            self.getNames().pop(lambdaArg.arg, None)
