# -*- coding: utf-8 -*-

# Copyright (c) 2019 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for function type annotations.
"""

import ast
import contextlib
import sys

from functools import lru_cache

import AstUtilities

from CodeStyleTopicChecker import CodeStyleTopicChecker

from .AnnotationsCheckerDefaults import AnnotationsCheckerDefaultArgs
from .AnnotationsEnums import AnnotationType, ClassDecoratorType, FunctionType


class AnnotationsChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for function type annotations.
    """

    Codes = [
        ## Function Annotations
        "A-001",
        "A-002",
        "A-003",
        ## Method Annotations
        "A-101",
        "A-102",
        ## Return Annotations
        "A-201",
        "A-202",
        "A-203",
        "A-204",
        "A-205",
        "A-206",
        ## Dynamically typed annotations
        "A-401",
        ## Type comments
        "A-402",
        ## Annotations Future
        "A-871",
        "A-872",
        "A-873",
        ## Annotation Coverage
        "A-881",
        ## Annotation Complexity
        "A-891",
        "A-892",
        ## use of typing.Union (PEP 604)
        "A-901",
        ## deprecated 'typing' symbols (PEP 585)
        "A-911",
    ]
    Category = "A"

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
        @param args dictionary of arguments for the annotation checks
        @type dict
        """
        super().__init__(
            AnnotationsChecker.Category,
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
            (
                self.__checkFunctionAnnotations,
                (
                    "A-001",
                    "A-002",
                    "A-003",
                    "A-101",
                    "A-102",
                    "A-201",
                    "A-202",
                    "A-203",
                    "A-204",
                    "A-205",
                    "A-206",
                    "A-401",
                    "A-402",
                ),
            ),
            (self.__checkAnnotationsFuture, ("A-871", "A-872", "A-873")),
            (self.__checkAnnotationsCoverage, ("A-881",)),
            (self.__checkAnnotationComplexity, ("A-891", "A-892")),
            (self.__checkAnnotationPep604, ("A-901",)),
            (self.__checkDeprecatedTypingSymbols, ("A-911",)),
        ]
        self._initializeCheckers(checkersWithCodes)

    #######################################################################
    ## Annotations
    ##
    ## adapted from: flake8-annotations v3.1.1
    #######################################################################

    def __checkFunctionAnnotations(self):
        """
        Private method to check for function annotation issues.
        """
        from .AnnotationsFunctionVisitor import FunctionVisitor

        # Type ignores are provided by ast at the module level & we'll need them later
        # when deciding whether or not to emit errors for a given function
        typeIgnoreLineno = {ti.lineno for ti in self.tree.type_ignores}
        hasMypyIgnoreErrors = any(
            "# mypy: ignore-errors" in line for line in self.source[:5]
        )

        suppressNoneReturning = self.args.get(
            "SuppressNoneReturning",
            AnnotationsCheckerDefaultArgs["SuppressNoneReturning"],
        )
        suppressDummyArgs = self.args.get(
            "SuppressDummyArgs", AnnotationsCheckerDefaultArgs["SuppressDummyArgs"]
        )
        allowUntypedDefs = self.args.get(
            "AllowUntypedDefs", AnnotationsCheckerDefaultArgs["AllowUntypedDefs"]
        )
        allowUntypedNested = self.args.get(
            "AllowUntypedNested", AnnotationsCheckerDefaultArgs["AllowUntypedNested"]
        )
        mypyInitReturn = self.args.get(
            "MypyInitReturn", AnnotationsCheckerDefaultArgs["MypyInitReturn"]
        )
        allowStarArgAny = self.args.get(
            "AllowStarArgAny", AnnotationsCheckerDefaultArgs["AllowStarArgAny"]
        )
        respectTypeIgnore = self.args.get(
            "RespectTypeIgnore", AnnotationsCheckerDefaultArgs["RespectTypeIgnore"]
        )

        # Store decorator lists as sets for easier lookup
        dispatchDecorators = set(
            self.args.get(
                "DispatchDecorators",
                AnnotationsCheckerDefaultArgs["DispatchDecorators"],
            )
        )
        overloadDecorators = set(
            self.args.get(
                "OverloadDecorators",
                AnnotationsCheckerDefaultArgs["OverloadDecorators"],
            )
        )

        visitor = FunctionVisitor(self.source)
        visitor.visit(self.tree)

        # Keep track of the last encountered function decorated by
        # `typing.overload`, if any. Per the `typing` module documentation,
        # a series of overload-decorated definitions must be followed by
        # exactly one non-overload-decorated definition of the same function.
        lastOverloadDecoratedFunctionName = None

        # Iterate over the arguments with missing type hints, by function.
        for function in visitor.functionDefinitions:
            if function.hasTypeComment:
                self.addErrorFromNode(function, "A-402")

            if function.isDynamicallyTyped() and (
                allowUntypedDefs or (function.isNested and allowUntypedNested)
            ):
                # Skip recording errors from dynamically typed functions
                # or nested functions
                continue

            # Skip recording errors for configured dispatch functions, such as
            # (by default) `functools.singledispatch` and
            # `functools.singledispatchmethod`
            if function.hasDecorator(dispatchDecorators):
                continue

            # Iterate over the annotated args to look for opinionated warnings
            annotatedArgs = function.getAnnotatedArguments()
            for arg in annotatedArgs:
                if arg.isDynamicallyTyped:
                    if allowStarArgAny and arg.annotationType in {
                        AnnotationType.VARARG,
                        AnnotationType.KWARG,
                    }:
                        continue

                    self.addErrorFromNode(function, "A-401")

            # Before we iterate over the function's missing annotations, check
            # to see if it's the closing function def in a series of
            # `typing.overload` decorated functions.
            if lastOverloadDecoratedFunctionName == function.name:
                continue

            # If it's not, and it is overload decorated, store it for the next
            # iteration
            if function.hasDecorator(overloadDecorators):
                lastOverloadDecoratedFunctionName = function.name

            # Optionally respect a 'type: ignore' comment
            # These are considered at the function level & tags are not considered
            if respectTypeIgnore:
                if function.lineno in typeIgnoreLineno:
                    # function-level ignore
                    continue
                elif (
                    any(lineno in typeIgnoreLineno for lineno in range(1, 6))
                    or hasMypyIgnoreErrors
                ):
                    # module-level ignore
                    # lineno from ast is 1-indexed
                    # check first five lines
                    continue

            # Record explicit errors for arguments that are missing annotations
            for arg in function.getMissedAnnotations():
                # Check for type comments here since we're not considering them as
                # typed args
                if arg.hasTypeComment:
                    self.addErrorFromNode(arg, "A-402")

                if arg.argname == "return":
                    # return annotations have multiple possible short-circuit
                    # paths
                    if (
                        suppressNoneReturning
                        and not arg.hasTypeAnnotation
                        and function.hasOnlyNoneReturns
                    ):
                        # Skip recording return errors if the function has only
                        # `None` returns. This includes the case of no returns.
                        continue

                    if (
                        mypyInitReturn
                        and function.isClassMethod
                        and function.name == "__init__"
                        and annotatedArgs
                    ):
                        # Skip recording return errors for `__init__` if at
                        # least one argument is annotated
                        continue

                # If the `suppressDummyArgs` flag is `True`, skip recording
                # errors for any arguments named `_`
                if arg.argname == "_" and suppressDummyArgs:
                    continue

                self.__classifyError(function, arg)

    def __classifyError(self, function, arg):
        """
        Private method to classify the missing type annotation based on the
        Function & Argument metadata.

        For the currently defined rules & program flow, the assumption can be
        made that an argument passed to this method will match a linting error,
        and will only match a single linting error

        This function provides an initial classificaton, then passes relevant
        attributes to cached helper function(s).

        @param function reference to the Function object
        @type Function
        @param arg reference to the Argument object
        @type Argument
        """
        # Check for return type
        # All return "arguments" have an explicitly defined name "return"
        if arg.argname == "return":
            errorCode = self.__returnErrorClassifier(
                function.isClassMethod,
                function.classDecoratorType,
                function.functionType,
            )
        else:
            # Otherwise, classify function argument error
            isFirstArg = arg == function.args[0]
            errorCode = self.__argumentErrorClassifier(
                function.isClassMethod,
                isFirstArg,
                function.classDecoratorType,
                arg.annotationType,
            )

        if errorCode in ("A-001", "A-002", "A-003"):
            self.addErrorFromNode(arg, errorCode, arg.argname)
        else:
            self.addErrorFromNode(arg, errorCode)

    @lru_cache()  # __IGNORE_WARNING_M-519__
    def __returnErrorClassifier(self, isClassMethod, classDecoratorType, functionType):
        """
        Private method to classify a return type annotation issue.

        @param isClassMethod flag indicating a classmethod type function
        @type bool
        @param classDecoratorType type of class decorator
        @type ClassDecoratorType
        @param functionType type of function
        @type FunctionType
        @return error code
        @rtype str
        """
        # Decorated class methods (@classmethod, @staticmethod) have a higher
        # priority than the rest
        if isClassMethod:
            if classDecoratorType == ClassDecoratorType.CLASSMETHOD:
                return "A-206"
            elif classDecoratorType == ClassDecoratorType.STATICMETHOD:
                return "A-205"

        if functionType == FunctionType.SPECIAL:
            return "A-204"
        elif functionType == FunctionType.PRIVATE:
            return "A-203"
        elif functionType == FunctionType.PROTECTED:
            return "A-202"
        else:
            return "A-201"

    @lru_cache()  # __IGNORE_WARNING_M-519__
    def __argumentErrorClassifier(
        self, isClassMethod, isFirstArg, classDecoratorType, annotationType
    ):
        """
        Private method to classify an argument type annotation issue.

        @param isClassMethod flag indicating a classmethod type function
        @type bool
        @param isFirstArg flag indicating the first argument
        @type bool
        @param classDecoratorType type of class decorator
        @type enums.ClassDecoratorType
        @param annotationType type of annotation
        @type AnnotationType
        @return error code
        @rtype str
        """
        # Check for regular class methods and @classmethod, @staticmethod is
        # deferred to final check
        if isClassMethod and isFirstArg:
            # The first function argument here would be an instance of self or
            # class
            if classDecoratorType == ClassDecoratorType.CLASSMETHOD:
                return "A-102"
            elif classDecoratorType != ClassDecoratorType.STATICMETHOD:
                # Regular class method
                return "A-101"

        # Check for remaining codes
        if annotationType == AnnotationType.KWARG:
            return "A-003"
        elif annotationType == AnnotationType.VARARG:
            return "A-002"
        else:
            # Combine PosOnlyArgs, Args, and KwOnlyArgs
            return "A-001"

    #######################################################################
    ## Annotations Coverage
    ##
    ## adapted from: flake8-annotations-coverage v0.0.6
    #######################################################################

    def __checkAnnotationsCoverage(self):
        """
        Private method to check for function annotation coverage.
        """
        minAnnotationsCoverage = self.args.get(
            "MinimumCoverage", AnnotationsCheckerDefaultArgs["MinimumCoverage"]
        )
        if minAnnotationsCoverage == 0:
            # 0 means it is switched off
            return

        functionDefs = [
            f
            for f in ast.walk(self.tree)
            if isinstance(f, (ast.AsyncFunctionDef, ast.FunctionDef))
        ]
        if not functionDefs:
            # no functions/methods at all
            return

        functionDefAnnotationsInfo = [
            self.__hasTypeAnnotations(f) for f in functionDefs
        ]
        if not bool(functionDefAnnotationsInfo):
            return

        annotationsCoverage = int(
            len(list(filter(None, functionDefAnnotationsInfo)))
            / len(functionDefAnnotationsInfo)
            * 100
        )
        if annotationsCoverage < minAnnotationsCoverage:
            self.addError(1, 0, "A-881", annotationsCoverage)

    def __hasTypeAnnotations(self, funcNode):
        """
        Private method to check for type annotations.

        @param funcNode reference to the function definition node to be checked
        @type ast.AsyncFunctionDef or ast.FunctionDef
        @return flag indicating the presence of type annotations
        @rtype bool
        """
        hasReturnAnnotation = funcNode.returns is not None
        hasArgsAnnotations = any(
            a for a in funcNode.args.args if a.annotation is not None
        )
        hasKwargsAnnotations = (
            funcNode.args
            and funcNode.args.kwarg
            and funcNode.args.kwarg.annotation is not None
        )
        hasKwonlyargsAnnotations = any(
            a for a in funcNode.args.kwonlyargs if a.annotation is not None
        )

        return any(
            (
                hasReturnAnnotation,
                hasArgsAnnotations,
                hasKwargsAnnotations,
                hasKwonlyargsAnnotations,
            )
        )

    #######################################################################
    ## Annotations Complexity
    ##
    ## adapted from: flake8-annotations-complexity v0.1.0
    #######################################################################

    def __checkAnnotationComplexity(self):
        """
        Private method to check the type annotation complexity.
        """
        maxAnnotationComplexity = self.args.get(
            "MaximumComplexity", AnnotationsCheckerDefaultArgs["MaximumComplexity"]
        )
        maxAnnotationLength = self.args.get(
            "MaximumLength", AnnotationsCheckerDefaultArgs["MaximumLength"]
        )
        typeAnnotations = []

        functionDefs = [
            f
            for f in ast.walk(self.tree)
            if isinstance(f, (ast.AsyncFunctionDef, ast.FunctionDef))
        ]
        for functionDef in functionDefs:
            typeAnnotations += list(
                filter(None, (a.annotation for a in functionDef.args.args))
            )
            if functionDef.returns:
                typeAnnotations.append(functionDef.returns)
        typeAnnotations += [
            a.annotation
            for a in ast.walk(self.tree)
            if isinstance(a, ast.AnnAssign) and a.annotation
        ]
        for annotation in typeAnnotations:
            complexity = self.__getAnnotationComplexity(annotation)
            if complexity > maxAnnotationComplexity:
                self.addErrorFromNode(
                    annotation, "A-891", complexity, maxAnnotationComplexity
                )

            annotationLength = self.__getAnnotationLength(annotation)
            if annotationLength > maxAnnotationLength:
                self.addErrorFromNode(
                    annotation, "A-892", annotationLength, maxAnnotationLength
                )

    def __getAnnotationComplexity(self, annotationNode, defaultComplexity=1):
        """
        Private method to determine the annotation complexity.

        It recursively counts the complexity of annotation nodes. When
        annotations are written as strings, it additionally parses them
        to 'ast' nodes.

        @param annotationNode reference to the node to determine the annotation
            complexity for
        @type ast.AST
        @param defaultComplexity default complexity value (defaults to 1)
        @type int (optional)
        @return annotation complexity
        @rtype = int
        """
        if AstUtilities.isString(annotationNode):
            try:
                annotationNode = ast.parse(annotationNode.value).body[0].value
            except (IndexError, SyntaxError):
                return defaultComplexity

        if isinstance(annotationNode, ast.Subscript):
            return defaultComplexity + self.__getAnnotationComplexity(
                annotationNode.slice
            )

        if isinstance(annotationNode, (ast.Tuple, ast.List)):
            return max(
                (self.__getAnnotationComplexity(n) for n in annotationNode.elts),
                default=defaultComplexity,
            )

        return defaultComplexity

    def __getAnnotationLength(self, annotationNode):
        """
        Private method to determine the annotation length.

        It recursively counts the length of annotation nodes. When annotations
        are written as strings, it additionally parses them to 'ast' nodes.

        @param annotationNode reference to the node to determine the annotation
            length for
        @type ast.AST
        @return annotation length
        @rtype = int
        """
        if AstUtilities.isString(annotationNode):
            # try to parse string-wrapped annotations
            try:
                annotationNode = ast.parse(annotationNode.value).body[0].value
            except (IndexError, SyntaxError):
                return 0

        if isinstance(annotationNode, ast.Subscript):
            with contextlib.suppress(AttributeError):
                return len(annotationNode.slice.elts)

        return 0

    #######################################################################
    ## 'from __future__ import annotations' check
    ##
    ## adapted from: flake8-future-annotations v1.1.0
    #######################################################################

    def __checkAnnotationsFuture(self):
        """
        Private method to check the use of __future__ and typing imports.
        """
        from .AnnotationsFutureVisitor import AnnotationsFutureVisitor

        if sys.version_info >= (3, 9):
            # the __future__ typing import is only needed before Python 3.9
            return

        forceFutureAnnotations = self.args.get(
            "ForceFutureAnnotations",
            AnnotationsCheckerDefaultArgs["ForceFutureAnnotations"],
        )
        checkFutureAnnotations = self.args.get(
            "CheckFutureAnnotations",
            AnnotationsCheckerDefaultArgs["CheckFutureAnnotations"],
        )

        visitor = AnnotationsFutureVisitor()
        visitor.visit(self.tree)

        if visitor.importsFutureAnnotations():
            return

        if visitor.hasTypingImports():
            imports = ", ".join(visitor.getTypingImports())
            self.addError(1, 0, "A-871", imports)
        elif forceFutureAnnotations:
            self.addError(1, 0, "A-872")

        if checkFutureAnnotations and visitor.hasSimplifiedTypes():
            simplifiedTypes = ", ".join(sorted(visitor.getSimplifiedTypes()))
            self.addError(1, 0, "A-873", simplifiedTypes)

    #######################################################################
    ## check use of 'typing.Union' (see PEP 604)
    ##
    ## adapted from: flake8-pep604 v1.1.0
    #######################################################################

    def __checkAnnotationPep604(self):
        """
        Private method to check the use of typing.Union.
        """
        from .AnnotationsUnionVisitor import AnnotationsUnionVisitor

        if sys.version_info < (3, 10):
            # the union operator was introduced with Python 3.10
            return

        visitor = AnnotationsUnionVisitor()
        visitor.visit(self.tree)

        for node in visitor.getIssues():
            self.addErrorFromNode(node, "A-901")

    #######################################################################
    ## check use of 'typing.Union' (see PEP 604)
    ##
    ## adapted from: flake8-pep585 v0.1.7
    #######################################################################

    def __checkDeprecatedTypingSymbols(self):
        """
        Private method to check the use of deprecated 'typing' symbols.
        """
        from .AnnotationsDeprecationsVisitor import (
            AnnotationsDeprecationsVisitor,
            AnnotationsFutureImportVisitor,
        )

        if sys.version_info < (3, 9):
            # py 3.8: only if activated via __future__ import
            visitor = AnnotationsFutureImportVisitor()
            visitor.visit(self.tree)
            if not visitor.futureImportPresent():
                return

        visitor = AnnotationsDeprecationsVisitor(
            self.args.get(
                "ExemptedTypingSymbols",
                AnnotationsCheckerDefaultArgs["ExemptedTypingSymbols"],
            )
        )
        visitor.visit(self.tree)

        for node, (name, replacement) in visitor.getIssues():
            self.addErrorFromNode(node, "A-911", name, replacement)
