# -*- coding: utf-8 -*-

# Copyright (c) 2013 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for documentation string conventions.
"""

#
# The routines of the checker class are modeled after the ones found in
# pep257.py (version 0.2.4).
#

import ast
import collections
import contextlib
import tokenize

from io import StringIO

try:
    ast.AsyncFunctionDef  # __IGNORE_EXCEPTION__
except AttributeError:
    ast.AsyncFunctionDef = ast.FunctionDef

from CodeStyleTopicChecker import CodeStyleTopicChecker


class DocStyleContext:
    """
    Class implementing the source context.
    """

    def __init__(self, source, startLine, contextType):
        """
        Constructor

        @param source source code of the context
        @type list of str or str
        @param startLine line number the context starts in the source
        @type int
        @param contextType type of the context object
        @type str
        """
        if isinstance(source, str):
            self.__source = source.splitlines(True)
        else:
            self.__source = source[:]
        self.__start = startLine
        self.__indent = ""
        self.__type = contextType
        self.__special = ""

        # ensure first line is left justified
        if self.__source:
            self.__indent = self.__source[0].replace(self.__source[0].lstrip(), "")
            self.__source[0] = self.__source[0].lstrip()

    def source(self):
        """
        Public method to get the source.

        @return source
        @rtype list of str
        """
        return self.__source

    def ssource(self):
        """
        Public method to get the joined source lines.

        @return source
        @rtype str
        """
        return "".join(self.__source)

    def start(self):
        """
        Public method to get the start line number.

        @return start line number
        @rtype int
        """
        return self.__start

    def end(self):
        """
        Public method to get the end line number.

        @return end line number
        @rtype int
        """
        return self.__start + len(self.__source) - 1

    def indent(self):
        """
        Public method to get the indentation of the first line.

        @return indentation string
        @rtype str
        """
        return self.__indent

    def contextType(self):
        """
        Public method to get the context type.

        @return context type
        @rtype str
        """
        return self.__type

    def setSpecial(self, special):
        """
        Public method to set a special attribute for the context.

        @param special attribute string
        @type str
        """
        self.__special = special

    def special(self):
        """
        Public method to get the special context attribute string.

        @return attribute string
        @rtype str
        """
        return self.__special


class DocStyleChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for documentation string conventions.
    """

    Codes = [
        "D-101",
        "D-102",
        "D-103",
        "D-104",
        "D-105",
        "D-111",
        "D-112",
        "D-121",
        "D-122",
        "D-130",
        "D-131",
        "D-132",
        "D-133",
        "D-134",
        "D-141",
        "D-142",
        "D-143",
        "D-144",
        "D-145",
        "D-201",
        "D-202.1",
        "D-202.2",
        "D-203",
        "D-205",
        "D-206",
        "D-221",
        "D-222",
        "D-231",
        "D-232",
        "D-234r",
        "D-234y",
        "D-235r",
        "D-235y",
        "D-236",
        "D-237",
        "D-238",
        "D-239",
        "D-242",
        "D-243",
        "D-244",
        "D-245",
        "D-246",
        "D-247",
        "D-250",
        "D-251",
        "D-252",
        "D-253",
        "D-260",
        "D-261",
        "D-262",
        "D-263",
        "D-270",
        "D-271",
        "D-272",
        "D-273",
    ]
    Category = "D"

    def __init__(
        self,
        source,
        filename,
        select,
        ignore,
        expected,
        repeat,
        maxLineLength=88,
        docType="pep257",
    ):
        """
        Constructor

        @param source source code to be checked
        @type list of str
        @param filename name of the source file
        @type str
        @param select list of selected codes
        @type list of str
        @param ignore list of codes to be ignored
        @type list of str
        @param expected list of expected codes
        @type list of str
        @param repeat flag indicating to report each occurrence of a code
        @type bool
        @param maxLineLength allowed line length
        @type int
        @param docType type of the documentation strings (one of 'eric' or 'pep257')
        @type str
        """
        super().__init__(
            DocStyleChecker.Category,
            source,
            filename,
            None,
            select,
            ignore,
            expected,
            repeat,
            [],
        )

        self.__maxLineLength = maxLineLength
        self.__docType = docType
        self.__lineNumber = 0

        # caches
        self.__functionsCache = None
        self.__classesCache = None
        self.__methodsCache = None

        self.__keywords = [
            "moduleDocstring",
            "functionDocstring",
            "classDocstring",
            "methodDocstring",
            "defDocstring",
            "docstring",
        ]
        if self.__docType == "pep257":
            checkersWithCodes = {
                "moduleDocstring": [
                    (self.__checkModulesDocstrings, ("D-101",)),
                ],
                "functionDocstring": [],
                "classDocstring": [
                    (self.__checkClassDocstring, ("D-104", "D-105")),
                    (self.__checkBlankBeforeAndAfterClass, ("D-142", "D-143")),
                ],
                "methodDocstring": [],
                "defDocstring": [
                    (self.__checkFunctionDocstring, ("D-102", "D-103")),
                    (self.__checkImperativeMood, ("D-132",)),
                    (self.__checkNoSignature, ("D-133",)),
                    (self.__checkReturnType, ("D-134",)),
                    (self.__checkNoBlankLineBefore, ("D-141",)),
                ],
                "docstring": [
                    (self.__checkTripleDoubleQuotes, ("D-111",)),
                    (self.__checkBackslashes, ("D-112",)),
                    (self.__checkOneLiner, ("D-121",)),
                    (self.__checkIndent, ("D-122",)),
                    (self.__checkSummary, ("D-130",)),
                    (self.__checkEndsWithPeriod, ("D-131",)),
                    (self.__checkBlankAfterSummary, ("D-144",)),
                    (self.__checkBlankAfterLastParagraph, ("D-145",)),
                ],
            }
        elif self.__docType in ("eric", "eric_black"):
            checkersWithCodes = {
                "moduleDocstring": [
                    (self.__checkModulesDocstrings, ("D-101", "D-201")),
                ],
                "functionDocstring": [],
                "classDocstring": [
                    (self.__checkClassDocstring, ("D-104", "D-205", "D-206")),
                    (
                        self.__checkEricNoBlankBeforeAndAfterClassOrFunction,
                        ("D-242", "D-243"),
                    ),
                    (self.__checkEricSignal, ("D-260", "D-261", "D-262", "D-263")),
                ],
                "methodDocstring": [
                    (self.__checkEricSummary, ("D-232")),
                ],
                "defDocstring": [
                    (
                        self.__checkFunctionDocstring,
                        ("D-102", "D-202.1", "D-202.2", "D-203"),
                    ),
                    (self.__checkImperativeMood, ("D-132",)),
                    (self.__checkNoSignature, ("D-133",)),
                    (self.__checkEricReturn, ("D-234r", "D-235r")),
                    (self.__checkEricYield, ("D-234y", "D-235y")),
                    (
                        self.__checkEricFunctionArguments,
                        ("D-236", "D-237", "D-238", "D-239"),
                    ),
                    (
                        self.__checkEricNoBlankBeforeAndAfterClassOrFunction,
                        ("D-244", "D-245"),
                    ),
                    (self.__checkEricException, ("D-250", "D-251", "D-252", "D-253")),
                    (self.__checkEricDocumentationSequence, ("D-270", "D-271")),
                    (self.__checkEricDocumentationDeprecatedTags, ("D-272",)),
                    (self.__checkEricDocumentationIndent, ("D-273",)),
                ],
                "docstring": [
                    (self.__checkTripleDoubleQuotes, ("D-111",)),
                    (self.__checkBackslashes, ("D-112",)),
                    (self.__checkIndent, ("D-122",)),
                    (self.__checkSummary, ("D-130",)),
                    (self.__checkEricEndsWithPeriod, ("D-231",)),
                    (self.__checkEricBlankAfterSummary, ("D-246",)),
                    (self.__checkEricNBlankAfterLastParagraph, ("D-247",)),
                    (self.__checkEricQuotesOnSeparateLines, ("D-222", "D-223")),
                ],
            }

        self.__checkers = collections.defaultdict(list)
        for key, checkers in checkersWithCodes.items():
            for checker, codes in checkers:
                if any(
                    not (msgCode and self._ignoreCode(msgCode)) for msgCode in codes
                ):
                    self.__checkers[key].append(checker)

    def addError(self, lineNumber, offset, msgCode, *args):
        """
        Public method to record an issue.

        @param lineNumber line number of the issue (zero based)
        @type int
        @param offset position within line of the issue
        @type int
        @param msgCode message code
        @type str
        @param args arguments for the message
        @type list
        """
        # call super class method with one based line number
        super().addError(lineNumber + 1, offset, msgCode, *args)

    def __resetReadline(self):
        """
        Private method to reset the internal readline function.
        """
        self.__lineNumber = 0

    def __readline(self):
        """
        Private method to get the next line from the source.

        @return next line of source
        @rtype str
        """
        self.__lineNumber += 1
        if self.__lineNumber > len(self.source):
            return ""
        return self.source[self.__lineNumber - 1]

    def run(self):
        """
        Public method to check the given source for violations of doc string
        conventions.
        """
        if not self.filename:
            # don't do anything, if essential data is missing
            return

        if not self.__checkers:
            # don't do anything, if no codes were selected
            return

        for key in self.__keywords:
            if key in self.__checkers:
                for check in self.__checkers[key]:
                    for context in self.__parseContexts(key):
                        docstring = self.__parseDocstring(context, key)
                        check(docstring, context)

    def __getSummaryLine(self, docstringContext):
        """
        Private method to extract the summary line.

        @param docstringContext docstring context
        @type DocStyleContext
        @return summary line (string) and the line it was found on
        @rtype int
        """
        lines = docstringContext.source()

        line = (
            lines[0]
            .replace('r"""', "", 1)
            .replace('u"""', "", 1)
            .replace('"""', "")
            .replace("r'''", "", 1)
            .replace("u'''", "", 1)
            .replace("'''", "")
            .strip()
        )

        if len(lines) == 1 or len(line) > 0:
            return line, 0
        return lines[1].strip().replace('"""', "").replace("'''", ""), 1

    def __getSummaryLines(self, docstringContext):
        """
        Private method to extract the summary lines.

        @param docstringContext docstring context
        @type DocStyleContext
        @return summary lines (list of string) and the line it was found on
        @rtype int
        """
        summaries = []
        lines = docstringContext.source()

        line0 = (
            lines[0]
            .replace('r"""', "", 1)
            .replace('u"""', "", 1)
            .replace('"""', "")
            .replace("r'''", "", 1)
            .replace("u'''", "", 1)
            .replace("'''", "")
            .strip()
        )
        line1 = (
            lines[1].strip().replace('"""', "").replace("'''", "")
            if len(lines) > 1
            else ""
        )
        line2 = (
            lines[2].strip().replace('"""', "").replace("'''", "")
            if len(lines) > 2
            else ""
        )
        if line0:
            lineno = 0
            summaries.append(line0)
            if not line0.endswith(".") and line1:
                # two line summary
                summaries.append(line1)
        elif line1:
            lineno = 1
            summaries.append(line1)
            if not line1.endswith(".") and line2:
                # two line summary
                summaries.append(line2)
        else:
            lineno = 2
            summaries.append(line2)
        return summaries, lineno

    def __getArgNames(self, node):
        """
        Private method to get the argument names of a function node.

        @param node AST node to extract arguments names from
        @type ast.AST
        @return tuple of two list of argument names, one for arguments
            and one for keyword arguments
        @rtype tuple of (list of str, list of str)
        """
        arguments = []
        arguments.extend([arg.arg for arg in node.args.args])
        if node.args.vararg is not None:
            arguments.append(node.args.vararg.arg)

        kwarguments = []
        kwarguments.extend([arg.arg for arg in node.args.kwonlyargs])
        if node.args.kwarg is not None:
            kwarguments.append(node.args.kwarg.arg)
        return arguments, kwarguments

    ##################################################################
    ## Parsing functionality below
    ##################################################################

    def __parseModuleDocstring(self, source):
        """
        Private method to extract a docstring given a module source.

        @param source source to parse
        @type list of str
        @return context of extracted docstring
        @rtype DocStyleContext
        """
        for kind, value, (line, _char), _, _ in tokenize.generate_tokens(
            StringIO("".join(source)).readline
        ):
            if kind in [tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL]:
                continue
            elif kind == tokenize.STRING:  # first STRING should be docstring
                return DocStyleContext(value, line - 1, "docstring")
            else:
                return None

        return None

    def __parseDocstring(self, context, what=""):
        """
        Private method to extract a docstring given `def` or `class` source.

        @param context context data to get the docstring from
        @type DocStyleContext
        @param what string denoting what is being parsed
        @type str
        @return context of extracted docstring
        @rtype DocStyleContext
        """
        moduleDocstring = self.__parseModuleDocstring(context.source())
        if what.startswith("module") or context.contextType() == "module":
            return moduleDocstring
        if moduleDocstring:
            return moduleDocstring

        tokenGenerator = tokenize.generate_tokens(StringIO(context.ssource()).readline)
        with contextlib.suppress(StopIteration):
            kind = None
            while kind != tokenize.INDENT:
                kind, _, _, _, _ = next(tokenGenerator)
            kind, value, (line, char), _, _ = next(tokenGenerator)
            if kind == tokenize.STRING:  # STRING after INDENT is a docstring
                return DocStyleContext(value, context.start() + line - 1, "docstring")

        return None

    def __parseTopLevel(self, keyword):
        """
        Private method to extract top-level functions or classes.

        @param keyword keyword signaling what to extract
        @type str
        @return extracted function or class contexts
        @rtype list of DocStyleContext
        """
        self.__resetReadline()
        tokenGenerator = tokenize.generate_tokens(self.__readline)
        kind, value, char = None, None, None
        contexts = []
        try:
            while True:
                start, end = None, None
                while not (kind == tokenize.NAME and value == keyword and char == 0):
                    kind, value, (line, char), _, _ = next(tokenGenerator)
                start = line - 1, char
                while not (kind == tokenize.DEDENT and value == "" and char == 0):
                    kind, value, (line, char), _, _ = next(tokenGenerator)
                end = line - 1, char
                contexts.append(
                    DocStyleContext(self.source[start[0] : end[0]], start[0], keyword)
                )
        except StopIteration:
            return contexts

    def __parseFunctions(self):
        """
        Private method to extract top-level functions.

        @return extracted function contexts
        @rtype list of DocStyleContext
        """
        if not self.__functionsCache:
            self.__functionsCache = self.__parseTopLevel("def")
        return self.__functionsCache

    def __parseClasses(self):
        """
        Private method to extract top-level classes.

        @return extracted class contexts
        @rtype list of DocStyleContext
        """
        if not self.__classesCache:
            self.__classesCache = self.__parseTopLevel("class")
        return self.__classesCache

    def __skipIndentedBlock(self, tokenGenerator):
        """
        Private method to skip over an indented block of source code.

        @param tokenGenerator token generator
        @type str iterator
        @return last token of the indented block
        @rtype tuple
        """
        kind, value, start, end, raw = next(tokenGenerator)
        while kind != tokenize.INDENT:
            kind, value, start, end, raw = next(tokenGenerator)
        indent = 1
        for kind, value, start, end, raw in tokenGenerator:
            if kind == tokenize.INDENT:
                indent += 1
            elif kind == tokenize.DEDENT:
                indent -= 1
            if indent == 0:
                return kind, value, start, end, raw

        return None

    def __parseMethods(self):
        """
        Private method to extract methods of all classes.

        @return extracted method contexts
        @rtype list of DocStyleContext
        """
        if not self.__methodsCache:
            contexts = []
            for classContext in self.__parseClasses():
                tokenGenerator = tokenize.generate_tokens(
                    StringIO(classContext.ssource()).readline
                )
                kind, value, char = None, None, None
                with contextlib.suppress(StopIteration):
                    while True:
                        start, end = None, None
                        while not (kind == tokenize.NAME and value == "def"):
                            kind, value, (line, char), _, _ = next(tokenGenerator)
                        start = line - 1, char
                        kind, value, (line, char), _, _ = self.__skipIndentedBlock(
                            tokenGenerator
                        )
                        end = line - 1, char
                        startLine = classContext.start() + start[0]
                        endLine = classContext.start() + end[0]
                        context = DocStyleContext(
                            self.source[startLine:endLine], startLine, "def"
                        )
                        if startLine > 0:
                            if self.source[startLine - 1].strip() == "@staticmethod":
                                context.setSpecial("staticmethod")
                            elif self.source[startLine - 1].strip() == "@classmethod":
                                context.setSpecial("classmethod")
                        contexts.append(context)
            self.__methodsCache = contexts

        return self.__methodsCache

    def __parseContexts(self, kind):
        """
        Private method to extract a context from the source.

        @param kind kind of context to extract
        @type str
        @return requested contexts
        @rtype list of DocStyleContext
        """
        if kind == "moduleDocstring":
            return [DocStyleContext(self.source, 0, "module")]
        if kind == "functionDocstring":
            return self.__parseFunctions()
        if kind == "classDocstring":
            return self.__parseClasses()
        if kind == "methodDocstring":
            return self.__parseMethods()
        if kind == "defDocstring":
            return self.__parseFunctions() + self.__parseMethods()
        if kind == "docstring":
            return (
                [DocStyleContext(self.source, 0, "module")]
                + self.__parseFunctions()
                + self.__parseClasses()
                + self.__parseMethods()
            )
        return []  # fall back

    ##################################################################
    ## Checking functionality below (PEP-257)
    ##################################################################

    def __checkModulesDocstrings(self, docstringContext, context):
        """
        Private method to check, if the module has a docstring.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            self.addError(context.start(), 0, "D-101")
            return

        docstring = docstringContext.ssource()
        if not docstring or not docstring.strip() or not docstring.strip("'\""):
            self.addError(context.start(), 0, "D-101")

        if (
            self.__docType == "eric"
            and docstring.strip("'\"").strip() == "Module documentation goes here."
        ):
            self.addError(docstringContext.end(), 0, "D-201")
            return

    def __checkFunctionDocstring(self, docstringContext, context):
        """
        Private method to check, that all public functions and methods
        have a docstring.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        functionName = context.source()[0].lstrip().split()[1].split("(")[0]
        if functionName.startswith("_") and not functionName.endswith("__"):
            if self.__docType == "eric":
                code = "D-203"
            else:
                code = "D-103"
        else:
            code = "D-102"

        if docstringContext is None:
            self.addError(context.start(), 0, code)
            return

        docstring = docstringContext.ssource()
        if not docstring or not docstring.strip() or not docstring.strip("'\""):
            self.addError(context.start(), 0, code)

        if self.__docType == "eric":
            if docstring.strip("'\"").strip() == "Function documentation goes here.":
                self.addError(docstringContext.end(), 0, "D-202.1")
                return

            if "DESCRIPTION" in docstring or "TYPE" in docstring:
                self.addError(docstringContext.end(), 0, "D-202.2")
                return

    def __checkClassDocstring(self, docstringContext, context):
        """
        Private method to check, that all public functions and methods
        have a docstring.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        className = context.source()[0].lstrip().split()[1].split("(")[0]
        if className.startswith("_"):
            if self.__docType == "eric":
                code = "D-205"
            else:
                code = "D-105"
        else:
            code = "D-104"

        if docstringContext is None:
            self.addError(context.start(), 0, code)
            return

        docstring = docstringContext.ssource()
        if not docstring or not docstring.strip() or not docstring.strip("'\""):
            self.addError(context.start(), 0, code)
            return

        if (
            self.__docType == "eric"
            and docstring.strip("'\"").strip() == "Class documentation goes here."
        ):
            self.addError(docstringContext.end(), 0, "D-206")
            return

    def __checkTripleDoubleQuotes(self, docstringContext, _context):
        """
        Private method to check, that all docstrings are surrounded
        by triple double quotes.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstring = docstringContext.ssource().strip()
        if not docstring.startswith(('"""', 'r"""', 'u"""')):
            self.addError(docstringContext.start(), 0, "D-111")

    def __checkBackslashes(self, docstringContext, _context):
        """
        Private method to check, that all docstrings containing
        backslashes are surrounded by raw triple double quotes.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstring = docstringContext.ssource().strip()
        if "\\" in docstring and not docstring.startswith('r"""'):
            self.addError(docstringContext.start(), 0, "D-112")

    def __checkOneLiner(self, docstringContext, context):
        """
        Private method to check, that one-liner docstrings fit on
        one line with quotes.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        lines = docstringContext.source()
        if len(lines) > 1:
            nonEmptyLines = [line for line in lines if line.strip().strip("'\"")]
            if len(nonEmptyLines) == 1:
                modLen = len(
                    context.indent() + '"""' + nonEmptyLines[0].strip() + '"""'
                )
                if context.contextType() != "module":
                    modLen += 4
                if not nonEmptyLines[0].strip().endswith("."):
                    # account for a trailing dot
                    modLen += 1
                if modLen <= self.__maxLineLength:
                    self.addError(docstringContext.start(), 0, "D-121")

    def __checkIndent(self, docstringContext, context):
        """
        Private method to check, that docstrings are properly indented.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        lines = docstringContext.source()
        if len(lines) == 1:
            return

        nonEmptyLines = [line.rstrip() for line in lines[1:] if line.strip()]
        if not nonEmptyLines:
            return

        indent = min(len(line) - len(line.strip()) for line in nonEmptyLines)
        expectedIndent = (
            0 if context.contextType() == "module" else len(context.indent()) + 4
        )
        if indent != expectedIndent:
            self.addError(docstringContext.start(), 0, "D-122")

    def __checkSummary(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries contain some text.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if summary == "":
            self.addError(docstringContext.start() + lineNumber, 0, "D-130")

    def __checkEndsWithPeriod(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries end with a period.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if not summary.endswith("."):
            self.addError(docstringContext.start() + lineNumber, 0, "D-131")

    def __checkImperativeMood(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries are in
        imperative mood.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if summary:
            firstWord = summary.strip().split()[0]
            if firstWord.endswith("s") and not firstWord.endswith("ss"):
                self.addError(docstringContext.start() + lineNumber, 0, "D-132")

    def __checkNoSignature(self, docstringContext, context):
        """
        Private method to check, that docstring summaries don't repeat
        the function's signature.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        functionName = context.source()[0].lstrip().split()[1].split("(")[0]
        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if functionName + "(" in summary.replace(
            " ", ""
        ) and functionName + "()" not in summary.replace(" ", ""):
            # report only, if it is not an abbreviated form (i.e. function() )
            self.addError(docstringContext.start() + lineNumber, 0, "D-133")

    def __checkReturnType(self, docstringContext, context):
        """
        Private method to check, that docstrings mention the return value type.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        if "return" not in docstringContext.ssource().lower():
            tokens = list(
                tokenize.generate_tokens(StringIO(context.ssource()).readline)
            )
            return_ = [
                tokens[i + 1][0]
                for i, token in enumerate(tokens)
                if token[1] == "return"
            ]
            if (
                set(return_) - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
                != set()
            ):
                self.addError(docstringContext.end(), 0, "D-134")

    def __checkNoBlankLineBefore(self, docstringContext, context):
        """
        Private method to check, that function/method docstrings are not
        preceded by a blank line.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        contextLines = context.source()
        cti = 0
        while cti < len(contextLines) and not contextLines[cti].strip().startswith(
            ('"""', 'r"""', 'u"""', "'''", "r'''", "u'''")
        ):
            cti += 1
        if cti == len(contextLines):
            return

        if not contextLines[cti - 1].strip():
            self.addError(docstringContext.start(), 0, "D-141")

    def __checkBlankBeforeAndAfterClass(self, docstringContext, context):
        """
        Private method to check, that class docstrings have one
        blank line around them.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        contextLines = context.source()
        cti = 0
        while cti < len(contextLines) and not contextLines[cti].strip().startswith(
            ('"""', 'r"""', 'u"""', "'''", "r'''", "u'''")
        ):
            cti += 1
        if cti == len(contextLines):
            return

        start = cti
        if contextLines[cti].strip() in ('"""', 'r"""', 'u"""', "'''", "r'''", "u'''"):
            # it is a multi line docstring
            cti += 1

        while cti < len(contextLines) and not contextLines[cti].strip().endswith(
            ('"""', "'''")
        ):
            cti += 1
        end = cti
        if cti >= len(contextLines) - 1:
            return

        if contextLines[start - 1].strip():
            self.addError(docstringContext.start(), 0, "D-142")
        if contextLines[end + 1].strip():
            self.addError(docstringContext.end(), 0, "D-143")

    def __checkBlankAfterSummary(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries are followed
        by a blank line.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstrings = docstringContext.source()
        if len(docstrings) <= 3:
            # correct/invalid one-liner
            return

        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if len(docstrings) > 2 and docstrings[lineNumber + 1].strip():
            self.addError(docstringContext.start() + lineNumber, 0, "D-144")

    def __checkBlankAfterLastParagraph(self, docstringContext, _context):
        """
        Private method to check, that the last paragraph of docstrings is
        followed by a blank line.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstrings = docstringContext.source()
        if len(docstrings) <= 3:
            # correct/invalid one-liner
            return

        if docstrings[-2].strip():
            self.addError(docstringContext.end(), 0, "D-145")

    ##################################################################
    ## Checking functionality below (eric specific ones)
    ##################################################################

    def __checkEricQuotesOnSeparateLines(self, docstringContext, _context):
        """
        Private method to check, that leading and trailing quotes are on
        a line by themselves.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        lines = docstringContext.source()
        if lines[0].strip().strip("ru\"'"):
            self.addError(docstringContext.start(), 0, "D-221")
        if lines[-1].strip().strip("\"'"):
            self.addError(docstringContext.end(), 0, "D-222")

    def __checkEricEndsWithPeriod(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries end with a period.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        summaryLines, lineNumber = self.__getSummaryLines(docstringContext)
        if summaryLines:
            if summaryLines[-1].lstrip().startswith("@"):
                summaryLines.pop(-1)
            summary = " ".join([s.strip() for s in summaryLines if s])
            if (
                summary
                and not summary.endswith(".")
                and summary.split(None, 1)[0].lower() != "constructor"
            ):
                self.addError(
                    docstringContext.start() + lineNumber + len(summaryLines) - 1,
                    0,
                    "D-231",
                )

    def __checkEricReturn(self, docstringContext, context):
        """
        Private method to check, that docstrings contain an &#64;return line
        if they return anything and don't otherwise.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        tokens = list(tokenize.generate_tokens(StringIO(context.ssource()).readline))
        return_ = [
            tokens[i + 1][0] for i, token in enumerate(tokens) if token[1] == "return"
        ]
        if "@return" not in docstringContext.ssource():
            if (
                set(return_) - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
                != set()
            ):
                self.addError(docstringContext.end(), 0, "D-234r")
        else:
            if (
                set(return_) - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE}
                == set()
            ):
                self.addError(docstringContext.end(), 0, "D-235r")

    def __checkEricYield(self, docstringContext, context):
        """
        Private method to check, that docstrings contain an &#64;yield line
        if they return anything and don't otherwise.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        tokens = list(tokenize.generate_tokens(StringIO(context.ssource()).readline))
        yield_ = [
            tokens[i + 1][0] for i, token in enumerate(tokens) if token[1] == "yield"
        ]
        if "@yield" not in docstringContext.ssource():
            if set(yield_) - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE} != set():
                self.addError(docstringContext.end(), 0, "D-234y")
        else:
            if set(yield_) - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE} == set():
                self.addError(docstringContext.end(), 0, "D-235y")

    def __checkEricFunctionArguments(self, docstringContext, context):
        """
        Private method to check, that docstrings contain an &#64;param and/or
        &#64;keyparam line for each argument.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        try:
            tree = ast.parse(context.ssource())
        except (SyntaxError, TypeError):
            return
        if (
            isinstance(tree, ast.Module)
            and len(tree.body) == 1
            and isinstance(tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            functionDef = tree.body[0]
            argNames, kwNames = self.__getArgNames(functionDef)
            if "self" in argNames:
                argNames.remove("self")
            if "cls" in argNames:
                argNames.remove("cls")

            tagstring = "".join(
                line.lstrip()
                for line in docstringContext.source()
                if line.lstrip().startswith("@")
            )
            if tagstring.count("@param") + tagstring.count("@keyparam") < len(
                argNames + kwNames
            ):
                self.addError(docstringContext.end(), 0, "D-236")
            elif tagstring.count("@param") + tagstring.count("@keyparam") > len(
                argNames + kwNames
            ):
                self.addError(docstringContext.end(), 0, "D-237")
            else:
                # extract @param and @keyparam from docstring
                args = []
                kwargs = []
                for line in docstringContext.source():
                    if line.strip().startswith(("@param", "@keyparam")):
                        paramParts = line.strip().split(None, 2)
                        if len(paramParts) >= 2:
                            at, name = paramParts[:2]
                            if at == "@keyparam":
                                kwargs.append(name.lstrip("*"))
                            args.append(name.lstrip("*"))

                # do the checks
                for name in kwNames:
                    if name not in kwargs:
                        self.addError(docstringContext.end(), 0, "D-238")
                        return
                if argNames + kwNames != args:
                    self.addError(docstringContext.end(), 0, "D-239")

    def __checkEricException(self, docstringContext, context):
        """
        Private method to check, that docstrings contain an &#64;exception line
        if they raise an exception and don't otherwise.

        Note: This method also checks the raised and documented exceptions for
        completeness (i.e. raised exceptions that are not documented or
        documented exceptions that are not raised)

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        tokens = list(tokenize.generate_tokens(StringIO(context.ssource()).readline))
        exceptions = set()
        raisedExceptions = set()
        tokensLen = len(tokens)
        for i, token in enumerate(tokens):
            if token[1] == "raise":
                exceptions.add(tokens[i + 1][0])
                if tokens[i + 1][0] == tokenize.NAME:
                    if tokensLen > (i + 2) and tokens[i + 2][1] == ".":
                        raisedExceptions.add(
                            "{0}.{1}".format(tokens[i + 1][1], tokens[i + 3][1])
                        )
                    else:
                        raisedExceptions.add(tokens[i + 1][1])

        if (
            "@exception" not in docstringContext.ssource()
            and "@throws" not in docstringContext.ssource()
            and "@raise" not in docstringContext.ssource()
        ):
            if exceptions - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE} != set():
                self.addError(docstringContext.end(), 0, "D-250")
        else:
            if exceptions - {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE} == set():
                self.addError(docstringContext.end(), 0, "D-251")
            else:
                # step 1: extract documented exceptions
                documentedExceptions = set()
                for line in docstringContext.source():
                    line = line.strip()
                    if line.startswith(("@exception", "@throws", "@raise")):
                        exceptionTokens = line.split(None, 2)
                        if len(exceptionTokens) >= 2:
                            documentedExceptions.add(exceptionTokens[1])

                # step 2: report undocumented exceptions
                for exception in raisedExceptions:
                    if exception not in documentedExceptions:
                        self.addError(docstringContext.end(), 0, "D-252", exception)

                # step 3: report undefined signals
                for exception in documentedExceptions:
                    if exception not in raisedExceptions:
                        self.addError(docstringContext.end(), 0, "D-253", exception)

    def __checkEricSignal(self, docstringContext, context):
        """
        Private method to check, that docstrings contain an &#64;signal line
        if they define signals and don't otherwise.

        Note: This method also checks the defined and documented signals for
        completeness (i.e. defined signals that are not documented or
        documented signals that are not defined)

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        tokens = list(tokenize.generate_tokens(StringIO(context.ssource()).readline))
        definedSignals = set()
        for i, token in enumerate(tokens):
            if token[1] in ("pyqtSignal", "Signal"):
                if tokens[i - 1][1] == "." and tokens[i - 2][1] == "QtCore":
                    definedSignals.add(tokens[i - 4][1])
                elif tokens[i - 1][1] == "=":
                    definedSignals.add(tokens[i - 2][1])

        if "@signal" not in docstringContext.ssource() and definedSignals:
            self.addError(docstringContext.end(), 0, "D-260")
        elif "@signal" in docstringContext.ssource():
            if not definedSignals:
                self.addError(docstringContext.end(), 0, "D-261")
            else:
                # step 1: extract documented signals
                documentedSignals = set()
                for line in docstringContext.source():
                    line = line.strip()
                    if line.startswith("@signal"):
                        signalTokens = line.split(None, 2)
                        if len(signalTokens) >= 2:
                            signal = signalTokens[1]
                            if "(" in signal:
                                signal = signal.split("(", 1)[0]
                            documentedSignals.add(signal)

                # step 2: report undocumented signals
                for signal in definedSignals:
                    if signal not in documentedSignals:
                        self.addError(docstringContext.end(), 0, "D-262", signal)

                # step 3: report undefined signals
                for signal in documentedSignals:
                    if signal not in definedSignals:
                        self.addError(docstringContext.end(), 0, "D-263", signal)

    def __checkEricBlankAfterSummary(self, docstringContext, _context):
        """
        Private method to check, that docstring summaries are followed
        by a blank line.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstrings = docstringContext.source()
        if len(docstrings) <= 3:
            # correct/invalid one-liner
            return

        summaryLines, lineNumber = self.__getSummaryLines(docstringContext)
        if (
            len(docstrings) - 2 > lineNumber + len(summaryLines) - 1
            and docstrings[lineNumber + len(summaryLines)].strip()
        ):
            self.addError(docstringContext.start() + lineNumber, 0, "D-246")

    def __checkEricNoBlankBeforeAndAfterClassOrFunction(
        self, docstringContext, context
    ):
        """
        Private method to check, that class and function/method docstrings
        have no blank line around them.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        contextLines = context.source()
        isClassContext = contextLines[0].lstrip().startswith("class ")
        cti = 0
        while cti < len(contextLines) and not contextLines[cti].strip().startswith(
            ('"""', 'r"""', 'u"""', "'''", "r'''", "u'''")
        ):
            cti += 1
        if cti == len(contextLines):
            return

        start = cti
        if contextLines[cti].strip() in ('"""', 'r"""', 'u"""', "'''", "r'''", "u'''"):
            # it is a multi line docstring
            cti += 1

        while cti < len(contextLines) and not contextLines[cti].strip().endswith(
            ('"""', "'''")
        ):
            cti += 1
        end = cti
        if cti >= len(contextLines) - 1:
            return

        if isClassContext:
            if not contextLines[start - 1].strip():
                self.addError(docstringContext.start(), 0, "D-242")
            if not contextLines[end + 1].strip() and self.__docType == "eric":
                self.addError(docstringContext.end(), 0, "D-243")
            elif contextLines[end + 1].strip() and self.__docType == "eric_black":
                self.addError(docstringContext.end(), 0, "D-143")
        else:
            if not contextLines[start - 1].strip():
                self.addError(docstringContext.start(), 0, "D-244")
            if not contextLines[end + 1].strip():
                if (
                    self.__docType == "eric_black"
                    and len(contextLines) > end + 2
                    and contextLines[end + 2].strip().startswith("def ")
                ):
                    return

                self.addError(docstringContext.end(), 0, "D-245")

    def __checkEricNBlankAfterLastParagraph(self, docstringContext, _context):
        """
        Private method to check, that the last paragraph of docstrings is
        not followed by a blank line.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docstrings = docstringContext.source()
        if len(docstrings) <= 3:
            # correct/invalid one-liner
            return

        if not docstrings[-2].strip():
            self.addError(docstringContext.end(), 0, "D-247")

    def __checkEricSummary(self, docstringContext, context):
        """
        Private method to check, that method docstring summaries start with
        specific words.

        @param docstringContext docstring context
        @type DocStyleContext
        @param context context of the docstring
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        summary, lineNumber = self.__getSummaryLine(docstringContext)
        if summary:
            # check, if the first word is 'Constructor', 'Public',
            # 'Protected' or 'Private'
            functionName, arguments = (
                context.source()[0].lstrip().split()[1].split("(", 1)
            )
            firstWord = summary.strip().split(None, 1)[0].lower()
            if functionName == "__init__":
                if firstWord != "constructor":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "constructor"
                    )
            elif functionName.startswith("__") and functionName.endswith("__"):
                if firstWord != "special":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "special"
                    )
            elif context.special() == "staticmethod":
                secondWord = summary.strip().split(None, 2)[1].lower()
                if firstWord != "static" and secondWord != "static":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "static"
                    )
                elif secondWord == "static":
                    if functionName.startswith(("__", "on_")):
                        if firstWord != "private":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "private static",
                            )
                    elif functionName.startswith("_") or functionName.endswith("Event"):
                        if firstWord != "protected":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "protected static",
                            )
                    else:
                        if firstWord != "public":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "public static",
                            )
            elif (
                arguments.startswith(("cls,", "cls)"))
                or context.special() == "classmethod"
            ):
                secondWord = summary.strip().split(None, 2)[1].lower()
                if firstWord != "class" and secondWord != "class":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "class"
                    )
                elif secondWord == "class":
                    if functionName.startswith(("__", "on_")):
                        if firstWord != "private":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "private class",
                            )
                    elif functionName.startswith("_") or functionName.endswith("Event"):
                        if firstWord != "protected":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "protected class",
                            )
                    else:
                        if firstWord != "public":
                            self.addError(
                                docstringContext.start() + lineNumber,
                                0,
                                "D-232",
                                "public class",
                            )
            elif functionName.startswith(("__", "on_")):
                if firstWord != "private":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "private"
                    )
            elif functionName.startswith("_") or functionName.endswith("Event"):
                if firstWord != "protected":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "protected"
                    )
            else:
                if firstWord != "public":
                    self.addError(
                        docstringContext.start() + lineNumber, 0, "D-232", "public"
                    )

    def __checkEricDocumentationSequence(
        self,
        docstringContext,
        _context,
    ):
        """
        Private method to check, that method docstring follows the correct sequence
        of entries (e.g. @param is followed by @type).

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        docTokens = []
        lines = docstringContext.source()
        for lineno, line in enumerate(lines):
            strippedLine = line.lstrip()
            if strippedLine.startswith("@"):
                docToken = strippedLine.split(None, 1)[0]
                docTokens.append((docToken, lineno))

                # check, that a type tag is not preceded by an empty line
                if (
                    docToken in ("@type", "@rtype", "@ytype")
                    and lineno > 0
                    and lines[lineno - 1].strip() == ""
                ):
                    self.addError(
                        docstringContext.start() + lineno, 0, "D-271", docToken
                    )

        # check the correct sequence of @param/@return/@yield and their accompanying
        # type tag
        for index in range(len(docTokens)):
            docToken, lineno = docTokens[index]
            try:
                docToken2, _ = docTokens[index + 1]
            except IndexError:
                docToken2 = ""

            if docToken in ("@param", "@keyparam") and docToken2 != "@type":
                self.addError(
                    docstringContext.start() + lineno, 0, "D-270", docToken, "@type"
                )
            elif docToken == "@return" and docToken2 != "@rtype":
                self.addError(
                    docstringContext.start() + lineno, 0, "D-270", docToken, "@rtype"
                )
            elif docToken == "@yield" and docToken2 != "@ytype":
                self.addError(
                    docstringContext.start() + lineno, 0, "D-270", docToken, "@ytype"
                )

    def __checkEricDocumentationDeprecatedTags(
        self,
        docstringContext,
        _context,
    ):
        """
        Private method to check the use of deprecated documentation tags.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None:
            return

        deprecationsList = {
            # key is deprecated tag, value is the tag to be used
            "@ireturn": "@return",
            "@ptype": "@type",
            "@raise": "@exception",
            "@throws": "@exception",
        }

        for lineno, line in enumerate(docstringContext.source()):
            strippedLine = line.lstrip()
            if strippedLine.startswith("@"):
                # it is a tag line
                tag = strippedLine.split(None, 1)[0]
                with contextlib.suppress(KeyError):
                    self.addError(
                        docstringContext.start() + lineno,
                        0,
                        "D-272",
                        tag,
                        deprecationsList[tag],
                    )

    def __checkEricDocumentationIndent(
        self,
        docstringContext,
        _context,
    ):
        """
        Private method to check the the correct indentation of the tag lines.

        @param docstringContext docstring context
        @type DocStyleContext
        @param _context context of the docstring (unused)
        @type DocStyleContext
        """
        if docstringContext is None or not docstringContext.source():
            return

        lines = docstringContext.source()
        for line in lines[1:]:
            if line.strip():
                indentationLength = len(line) - len(line.lstrip())
                break
        else:
            # only empty lines except the first one
            return

        for lineno, line in enumerate(lines):
            strippedLine = line.lstrip()
            if strippedLine.startswith("@"):
                tag = strippedLine.split(None, 1)[0]
                currentIndentation = len(line) - len(strippedLine)
                if currentIndentation != indentationLength:
                    self.addError(docstringContext.start() + lineno, 0, "D-273", tag)
