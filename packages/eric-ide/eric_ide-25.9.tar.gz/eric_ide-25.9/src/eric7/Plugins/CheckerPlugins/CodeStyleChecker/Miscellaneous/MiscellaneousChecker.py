# -*- coding: utf-8 -*-

# Copyright (c) 2015 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a checker for miscellaneous checks.
"""

import ast
import builtins
import contextlib
import copy
import itertools
import re
import sys
import tokenize

from string import Formatter

try:
    # Python 3.10+
    from itertools import pairwise
except ImportError:
    # replacement for Python < 3.10
    from itertools import tee

    def pairwise(iterable):
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)


import AstUtilities

from CodeStyleTopicChecker import CodeStyleTopicChecker

from .BugBearVisitor import BugBearVisitor
from .ConstantModificationVisitor import ConstantModificationVisitor
from .DateTimeVisitor import DateTimeVisitor
from .DefaultMatchCaseVisitor import DefaultMatchCaseVisitor
from .eradicate import Eradicator
from .MiscellaneousDefaults import MiscellaneousCheckerDefaultArgs
from .ReturnVisitor import ReturnVisitor
from .SysVersionVisitor import SysVersionVisitor
from .TextVisitor import TextVisitor


class MiscellaneousChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for miscellaneous checks.
    """

    Codes = [
        ## Coding line
        "M-101",
        "M-102",
        ## Copyright
        "M-111",
        "M-112",
        ## Shadowed Builtins
        "M-131",
        "M-132",
        ## Comprehensions
        "M-180",
        "M-181",
        "M-182",
        "M-183",
        "M-184",
        "M-185",
        "M-186",
        "M-188",
        "M-189",
        "M-189a",
        "M-189b",
        "M-190",
        "M-190a",
        "M-190b",
        "M-191",
        "M-193",
        "M-193a",
        "M-193b",
        "M-193c",
        "M-194",
        "M-195",
        "M-196",
        "M-197",
        "M-198",
        "M-199",
        "M-200",
        "M-201",
        ## Dictionaries with sorted keys
        "M-251",
        ## Property
        "M-260",
        "M-261",
        "M-262",
        "M-263",
        "M-264",
        "M-265",
        "M-266",
        "M-267",
        ## Naive datetime usage
        "M-301",
        "M-302",
        "M-303",
        "M-304",
        "M-305",
        "M-306",
        "M-307",
        "M-308",
        "M-311",
        "M-312",
        "M-313",
        "M-314",
        "M-315",
        "M-321",
        ## sys.version and sys.version_info usage
        "M-401",
        "M-402",
        "M-403",
        "M-411",
        "M-412",
        "M-413",
        "M-414",
        "M-421",
        "M-422",
        "M-423",
        ## Bugbear
        "M-501",
        "M-502",
        "M-503",
        "M-504",
        "M-505",
        "M-506",
        "M-507",
        "M-508",
        "M-509",
        "M-510",
        "M-511",
        "M-512",
        "M-513",
        "M-514",
        "M-515",
        "M-516",
        "M-517",
        "M-518",
        "M-519",
        "M-520",
        "M-521",
        "M-522",
        "M-523",
        "M-524",
        "M-525",
        "M-526",
        "M-527",
        "M-528",
        "M-529",
        "M-530",
        "M-531",
        "M-532",
        "M-533",
        "M-534",
        "M-535",
        "M-536",
        "M-537",
        "M-539",
        "M-540",
        "M-541",
        ## Bugbear, opininonated
        "M-569",
        ## Bugbear++
        "M-581",
        "M-582",
        ## Format Strings
        "M-601",
        "M-611",
        "M-612",
        "M-613",
        "M-621",
        "M-622",
        "M-623",
        "M-624",
        "M-625",
        "M-631",
        "M-632",
        ## Future statements
        "M-701",
        "M-702",
        ## Gettext
        "M-711",
        ## print() statements
        "M-801",
        ## one element tuple
        "M-811",
        ## return statements  # noqa: M-891
        "M-831",
        "M-832",
        "M-833",
        "M-834",
        ## line continuation
        "M-841",
        ## implicitly concatenated strings
        "M-851",
        "M-852",
        "M-853",
        ## commented code
        "M-891",
        ## structural pattern matching
        "M-901",
        "M-902",
        ## constant modification
        "M-911",
        "M-912",
        "M-913",
        "M-914",
        "M-915",
        "M-916",
    ]
    Category = "M"

    Formatter = Formatter()
    FormatFieldRegex = re.compile(r"^((?:\s|.)*?)(\..*|\[.*\])?$")

    BuiltinsWhiteList = [
        "__name__",
        "__doc__",
        "credits",
    ]

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
        @param args dictionary of arguments for the miscellaneous checks
        @type dict
        """
        super().__init__(
            MiscellaneousChecker.Category,
            source,
            filename,
            tree,
            select,
            ignore,
            expected,
            repeat,
            args,
        )

        linesIterator = iter(self.source)
        self.__tokens = list(tokenize.generate_tokens(lambda: next(linesIterator)))

        self.__pep3101FormatRegex = re.compile(
            r'^(?:[^\'"]*[\'"][^\'"]*[\'"])*\s*%|^\s*%'
        )

        self.__builtins = [b for b in dir(builtins) if b not in self.BuiltinsWhiteList]

        self.__eradicator = Eradicator()

        checkersWithCodes = [
            (self.__checkCoding, ("M-101", "M-102")),
            (self.__checkCopyright, ("M-111", "M-112")),
            (self.__checkBuiltins, ("M-131", "M-132")),
            (
                self.__checkComprehensions,
                (
                    "M-180",
                    "M-181",
                    "M-182",
                    "M-183",
                    "M-184",
                    "M-185",
                    "M-186",
                    "M-188",
                    "M-189",
                    "M-189a",
                    "M-189b",
                    "M-190",
                    "M-190a",
                    "M-190b",
                    "M-191",
                    "M-193",
                    "M-193a",
                    "M-193b",
                    "M-193c",
                    "M-194",
                    "M-195",
                    "M-196",
                    "M-197",
                    "M-198",
                    "M-199",
                    "M-200",
                    "M-201",
                ),
            ),
            (self.__checkDictWithSortedKeys, ("M-251",)),
            (
                self.__checkProperties,
                (
                    "M-260",
                    "M-261",
                    "M-262",
                    "M-263",
                    "M-264",
                    "M-265",
                    "M-266",
                    "M-267",
                ),
            ),
            (
                self.__checkDateTime,
                (
                    "M-301",
                    "M-302",
                    "M-303",
                    "M-304",
                    "M-305",
                    "M-306",
                    "M-307",
                    "M-308",
                    "M-311",
                    "M-312",
                    "M-313",
                    "M-314",
                    "M-315",
                    "M-321",
                ),
            ),
            (
                self.__checkSysVersion,
                (
                    "M-401",
                    "M-402",
                    "M-403",
                    "M-411",
                    "M-412",
                    "M-413",
                    "M-414",
                    "M-421",
                    "M-422",
                    "M-423",
                ),
            ),
            (
                self.__checkBugBear,
                (
                    "M-501",
                    "M-502",
                    "M-503",
                    "M-504",
                    "M-505",
                    "M-506",
                    "M-507",
                    "M-508",
                    "M-509",
                    "M-510",
                    "M-511",
                    "M-512",
                    "M-513",
                    "M-514",
                    "M-515",
                    "M-516",
                    "M-517",
                    "M-518",
                    "M-519",
                    "M-520",
                    "M-521",
                    "M-522",
                    "M-523",
                    "M-524",
                    "M-525",
                    "M-526",
                    "M-527",
                    "M-528",
                    "M-529",
                    "M-530",
                    "M-531",
                    "M-532",
                    "M-533",
                    "M-534",
                    "M-535",
                    "M-536",
                    "M-537",
                    "M-539",
                    "M-540",
                    "M-541",
                    "M-569",
                    "M-581",
                    "M-582",
                ),
            ),
            (self.__checkPep3101, ("M-601",)),
            (
                self.__checkFormatString,
                (
                    "M-611",
                    "M-612",
                    "M-613",
                    "M-621",
                    "M-622",
                    "M-623",
                    "M-624",
                    "M-625",
                    "M-631",
                    "M-632",
                ),
            ),
            (self.__checkFuture, ("M-701", "M-702")),
            (self.__checkGettext, ("M-711",)),
            (self.__checkPrintStatements, ("M-801",)),
            (self.__checkTuple, ("M-811",)),
            (self.__checkReturn, ("M-831", "M-832", "M-833", "M-834")),
            (self.__checkLineContinuation, ("M-841",)),
            (self.__checkImplicitStringConcat, ("M-851", "M-852")),
            (self.__checkExplicitStringConcat, ("M-853",)),
            (self.__checkCommentedCode, ("M-891",)),
            (self.__checkDefaultMatchCase, ("M-901", "M-902")),
            (
                self.__checkConstantModification,
                ("M-911", "M-912", "M-913", "M-914", "M-915", "M-916"),
            ),
        ]
        self._initializeCheckers(checkersWithCodes)

        # the eradicate whitelist
        commentedCodeCheckerArgs = self.args.get(
            "CommentedCodeChecker",
            MiscellaneousCheckerDefaultArgs["CommentedCodeChecker"],
        )
        commentedCodeCheckerWhitelist = commentedCodeCheckerArgs.get(
            "WhiteList",
            MiscellaneousCheckerDefaultArgs["CommentedCodeChecker"]["WhiteList"],
        )
        self.__eradicator.update_whitelist(
            commentedCodeCheckerWhitelist, extend_default=False
        )

    def __getCoding(self):
        """
        Private method to get the defined coding of the source.

        @return tuple containing the line number and the coding
        @rtype tuple of int and str
        """
        for lineno, line in enumerate(self.source[:5], start=1):
            matched = re.search(r"coding[:=]\s*([-\w_.]+)", line, re.IGNORECASE)
            if matched:
                return lineno, matched.group(1)
        else:
            return 0, ""

    def __checkCoding(self):
        """
        Private method to check the presence of a coding line and valid
        encodings.
        """
        if len(self.source) == 0:
            return

        encodings = [
            e.lower().strip()
            for e in self.args.get(
                "CodingChecker", MiscellaneousCheckerDefaultArgs["CodingChecker"]
            ).split(",")
        ]
        lineno, coding = self.__getCoding()
        if coding:
            if coding.lower() not in encodings:
                self.addError(lineno, 0, "M-102", coding)
        else:
            self.addError(1, 0, "M-101")

    def __checkCopyright(self):
        """
        Private method to check the presence of a copyright statement.
        """
        source = "".join(self.source)
        copyrightArgs = self.args.get(
            "CopyrightChecker", MiscellaneousCheckerDefaultArgs["CopyrightChecker"]
        )
        copyrightMinFileSize = copyrightArgs.get(
            "MinFilesize",
            MiscellaneousCheckerDefaultArgs["CopyrightChecker"]["MinFilesize"],
        )
        copyrightAuthor = copyrightArgs.get(
            "Author", MiscellaneousCheckerDefaultArgs["CopyrightChecker"]["Author"]
        )
        copyrightRegexStr = (
            r"Copyright\s+(\(C\)\s+)?(\d{{4}}\s+-\s+)?\d{{4}}\s+{author}"
        )

        tocheck = max(1024, copyrightMinFileSize)
        topOfSource = source[:tocheck]
        if len(topOfSource) < copyrightMinFileSize:
            return

        copyrightRe = re.compile(copyrightRegexStr.format(author=r".*"), re.IGNORECASE)
        if not copyrightRe.search(topOfSource):
            self.addError(1, 0, "M-111")
            return

        if copyrightAuthor:
            copyrightAuthorRe = re.compile(
                copyrightRegexStr.format(author=copyrightAuthor), re.IGNORECASE
            )
            if not copyrightAuthorRe.search(topOfSource):
                self.addError(1, 0, "M-112")

    def __checkCommentedCode(self):
        """
        Private method to check for commented code.
        """
        source = "".join(self.source)
        commentedCodeCheckerArgs = self.args.get(
            "CommentedCodeChecker",
            MiscellaneousCheckerDefaultArgs["CommentedCodeChecker"],
        )
        aggressive = commentedCodeCheckerArgs.get(
            "Aggressive",
            MiscellaneousCheckerDefaultArgs["CommentedCodeChecker"]["Aggressive"],
        )
        for markedLine in self.__eradicator.commented_out_code_line_numbers(
            source, aggressive=aggressive
        ):
            self.addError(markedLine, 0, "M-891")

    def __checkLineContinuation(self):
        """
        Private method to check line continuation using backslash.
        """
        # generate source lines without comments
        comments = [tok for tok in self.__tokens if tok[0] == tokenize.COMMENT]
        stripped = self.source[:]
        for comment in comments:
            lineno = comment[3][0]
            start = comment[2][1]
            stop = comment[3][1]
            content = stripped[lineno - 1]
            withoutComment = content[:start] + content[stop:]
            stripped[lineno - 1] = withoutComment.rstrip()

        # perform check with 'cleaned' source
        for lineIndex, line in enumerate(stripped):
            strippedLine = line.strip()
            if strippedLine.endswith("\\") and not strippedLine.startswith(
                ("assert", "with")
            ):
                self.addError(lineIndex + 1, len(line), "M-841")

    def __checkPrintStatements(self):
        """
        Private method to check for print statements.
        """
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.Call) and getattr(node.func, "id", None) == "print"
            ) or (hasattr(ast, "Print") and isinstance(node, ast.Print)):
                self.addErrorFromNode(node, "M-801")

    def __checkTuple(self):
        """
        Private method to check for one element tuples.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Tuple) and len(node.elts) == 1:
                self.addErrorFromNode(node, "M-811")

    def __checkFuture(self):
        """
        Private method to check the __future__ imports.
        """
        expectedImports = {
            i.strip()
            for i in self.args.get("FutureChecker", "").split(",")
            if bool(i.strip())
        }
        if len(expectedImports) == 0:
            # nothing to check for; disabling the check
            return

        imports = set()
        node = None
        hasCode = False

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                imports |= {name.name for name in node.names}
            elif isinstance(node, ast.Expr):
                if not AstUtilities.isString(node.value):
                    hasCode = True
                    break
            elif not (AstUtilities.isString(node) or isinstance(node, ast.Module)):
                hasCode = True
                break

        if isinstance(node, ast.Module) or not hasCode:
            return

        if imports < expectedImports:
            if imports:
                self.addErrorFromNode(
                    node, "M-701", ", ".join(expectedImports), ", ".join(imports)
                )
            else:
                self.addErrorFromNode(node, "M-702", ", ".join(expectedImports))

    def __checkPep3101(self):
        """
        Private method to check for old style string formatting.
        """
        for lineno, line in enumerate(self.source, start=1):
            match = self.__pep3101FormatRegex.search(line)
            if match:
                lineLen = len(line)
                pos = line.find("%")
                formatPos = pos
                formatter = "%"
                if line[pos + 1] == "(":
                    pos = line.find(")", pos)
                c = line[pos]
                while c not in "diouxXeEfFgGcrs":
                    pos += 1
                    if pos >= lineLen:
                        break
                    c = line[pos]
                if c in "diouxXeEfFgGcrs":
                    formatter += c
                self.addError(lineno, formatPos, "M-601", formatter)

    def __checkFormatString(self):
        """
        Private method to check string format strings.
        """
        coding = self.__getCoding()[1]
        if not coding:
            # default to utf-8
            coding = "utf-8"

        visitor = TextVisitor()
        visitor.visit(self.tree)
        for node in visitor.nodes:
            text = node.value
            if isinstance(text, bytes):
                try:
                    text = text.decode(coding)
                except UnicodeDecodeError:
                    continue
            fields, implicit, explicit = self.__getFields(text)
            if implicit:
                if node in visitor.calls:
                    self.addErrorFromNode(node, "M-611")
                else:
                    if node.is_docstring:
                        self.addErrorFromNode(node, "M-612")
                    else:
                        self.addErrorFromNode(node, "M-613")

            if node in visitor.calls:
                call, strArgs = visitor.calls[node]

                numbers = set()
                names = set()
                # Determine which fields require a keyword and which an arg
                for name in fields:
                    fieldMatch = self.FormatFieldRegex.match(name)
                    try:
                        number = int(fieldMatch.group(1))
                    except ValueError:
                        number = -1
                    # negative numbers are considered keywords
                    if number >= 0:
                        numbers.add(number)
                    else:
                        names.add(fieldMatch.group(1))

                keywords = {kw.arg for kw in call.keywords}
                numArgs = len(call.args)
                if strArgs:
                    numArgs -= 1
                hasKwArgs = any(kw.arg is None for kw in call.keywords)
                hasStarArgs = sum(
                    1 for arg in call.args if isinstance(arg, ast.Starred)
                )

                if hasKwArgs:
                    keywords.discard(None)
                if hasStarArgs:
                    numArgs -= 1

                # if starargs or kwargs is not None, it can't count the
                # parameters but at least check if the args are used
                if hasKwArgs and not names:
                    # No names but kwargs
                    self.addErrorFromNode(call, "M-623")
                if hasStarArgs and not numbers:
                    # No numbers but args
                    self.addErrorFromNode(call, "M-624")

                if not hasKwArgs and not hasStarArgs:
                    # can actually verify numbers and names
                    for number in sorted(numbers):
                        if number >= numArgs:
                            self.addErrorFromNode(call, "M-621", number)

                    for name in sorted(names):
                        if name not in keywords:
                            self.addErrorFromNode(call, "M-622", name)

                for arg in range(numArgs):
                    if arg not in numbers:
                        self.addErrorFromNode(call, "M-631", arg)

                for kw in keywords:
                    if kw not in names:
                        self.addErrorFromNode(call, "M-632", kw)

                if implicit and explicit:
                    self.addErrorFromNode(call, "M-625")

    def __getFields(self, string):
        """
        Private method to extract the format field information.

        @param string format string to be parsed
        @type str
        @return format field information as a tuple with fields, implicit
            field definitions present and explicit field definitions present
        @rtype tuple of set of str, bool, bool
        """
        fields = set()
        cnt = itertools.count()
        implicit = False
        explicit = False
        try:
            for _literal, field, spec, conv in self.Formatter.parse(string):
                if field is not None and (conv is None or conv in "rsa"):
                    if not field:
                        field = str(next(cnt))
                        implicit = True
                    else:
                        explicit = True
                    fields.add(field)
                    fields.update(
                        parsedSpec[1]
                        for parsedSpec in self.Formatter.parse(spec)
                        if parsedSpec[1] is not None
                    )
        except ValueError:
            return set(), False, False
        else:
            return fields, implicit, explicit

    def __checkBuiltins(self):
        """
        Private method to check, if built-ins are shadowed.
        """
        functionDefs = [ast.FunctionDef]
        with contextlib.suppress(AttributeError):
            functionDefs.append(ast.AsyncFunctionDef)

        ignoreBuiltinAssignments = self.args.get(
            "BuiltinsChecker", MiscellaneousCheckerDefaultArgs["BuiltinsChecker"]
        )

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                # assign statement
                for element in node.targets:
                    if isinstance(element, ast.Name) and element.id in self.__builtins:
                        value = node.value
                        if (
                            isinstance(value, ast.Name)
                            and element.id in ignoreBuiltinAssignments
                            and value.id in ignoreBuiltinAssignments[element.id]
                        ):
                            # ignore compatibility assignments
                            continue
                        self.addErrorFromNode(element, "M-131", element.id)
                    elif isinstance(element, (ast.Tuple, ast.List)):
                        for tupleElement in element.elts:
                            if (
                                isinstance(tupleElement, ast.Name)
                                and tupleElement.id in self.__builtins
                            ):
                                self.addErrorFromNode(
                                    tupleElement, "M-131", tupleElement.id
                                )
            elif isinstance(node, ast.For):
                # for loop
                target = node.target
                if isinstance(target, ast.Name) and target.id in self.__builtins:
                    self.addErrorFromNode(target, "M-131", target.id)
                elif isinstance(target, (ast.Tuple, ast.List)):
                    for element in target.elts:
                        if (
                            isinstance(element, ast.Name)
                            and element.id in self.__builtins
                        ):
                            self.addErrorFromNode(element, "M-131", element.id)
            elif any(isinstance(node, functionDef) for functionDef in functionDefs):
                # (asynchronous) function definition
                for arg in node.args.args:
                    if isinstance(arg, ast.arg) and arg.arg in self.__builtins:
                        self.addErrorFromNode(arg, "M-132", arg.arg)

    def __checkComprehensions(self):
        """
        Private method to check some comprehension related things.

        This method is adapted from: flake8-comprehensions v3.16.0
        Original: Copyright (c) 2017 Adam Johnson

        The check for nested comprehensions was included and adapted from:
        flake8_no_nested_comprehensions v1.0.0
        Original: Copyright (c) 2024 Timmy Welch
        """
        comprehensionArgs = self.args.get(
            "ComprehensionsChecker",
            MiscellaneousCheckerDefaultArgs["ComprehensionsChecker"],
        )

        compType = {
            ast.DictComp: "dict",
            ast.ListComp: "list",
            ast.SetComp: "set",
        }

        visitedMapCalls = set()

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                numPositionalArgs = len(node.args)
                numKeywordArgs = len(node.keywords)

                if (
                    numPositionalArgs == 1
                    and isinstance(node.args[0], ast.GeneratorExp)
                    and node.func.id in ("list", "set")
                ):
                    errorCode = {
                        "list": "M-180",
                        "set": "M-181",
                    }[node.func.id]
                    self.addErrorFromNode(node, errorCode)

                elif (
                    numPositionalArgs == 1
                    and node.func.id == "dict"
                    and len(node.keywords) == 0
                    and isinstance(node.args[0], (ast.GeneratorExp, ast.ListComp))
                    and isinstance(node.args[0].elt, ast.Tuple)
                    and len(node.args[0].elt.elts) == 2
                ):
                    if isinstance(node.args[0], ast.GeneratorExp):
                        errorCode = "M-182"
                    else:
                        errorCode = "M-184"
                    self.addErrorFromNode(node, errorCode)

                elif (
                    numPositionalArgs == 1
                    and isinstance(node.args[0], ast.ListComp)
                    and node.func.id in ("list", "set", "any", "all")
                ):
                    errorCode = {
                        "list": "M-191",
                        "set": "M-183",
                        "any": "M-199",
                        "all": "M-199",
                    }[node.func.id]
                    self.addErrorFromNode(node, errorCode, node.func.id)

                elif numPositionalArgs == 1 and (
                    isinstance(node.args[0], ast.Tuple)
                    and node.func.id == "tuple"
                    or isinstance(node.args[0], ast.List)
                    and node.func.id == "list"
                ):
                    errorCode = {
                        "tuple": "M-189a",
                        "list": "M-190a",
                    }[node.func.id]
                    self.addErrorFromNode(
                        node,
                        errorCode,
                        type(node.args[0]).__name__.lower(),
                        node.func.id,
                    )

                elif (
                    numPositionalArgs == 1
                    and numKeywordArgs == 0
                    and isinstance(node.args[0], (ast.Dict, ast.DictComp))
                    and node.func.id == "dict"
                ):
                    if isinstance(node.args[0], ast.Dict):
                        type_ = "dict"
                    else:
                        type_ = "dict comprehension"
                    self.addErrorFromNode(node, "M-198", type_)

                elif (
                    numPositionalArgs == 1
                    and isinstance(node.args[0], (ast.Tuple, ast.List))
                    and (
                        node.func.id in ("tuple", "list", "set")
                        or (
                            node.func.id == "dict"
                            and all(
                                isinstance(elt, ast.Tuple) and len(elt.elts) == 2
                                for elt in node.args[0].elts
                            )
                        )
                    )
                ):
                    errorCode = {
                        "tuple": "M-189b",
                        "list": "M-190b",
                        "set": "M-185",
                        "dict": "M-186",
                    }[node.func.id]
                    self.addErrorFromNode(
                        node,
                        errorCode,
                        type(node.args[0]).__name__.lower(),
                        node.func.id,
                    )

                elif (
                    numPositionalArgs == 0
                    and not any(isinstance(a, ast.Starred) for a in node.args)
                    and not any(k.arg is None for k in node.keywords)
                    and node.func.id == "dict"
                ) or (
                    numPositionalArgs == 0
                    and numKeywordArgs == 0
                    and node.func.id in ("tuple", "list")
                ):
                    self.addErrorFromNode(node, "M-188", node.func.id)

                elif (
                    node.func.id in {"list", "reversed"}
                    and numPositionalArgs > 0
                    and isinstance(node.args[0], ast.Call)
                    and isinstance(node.args[0].func, ast.Name)
                    and node.args[0].func.id == "sorted"
                ):
                    if node.func.id == "reversed":
                        reverseFlagValue = False
                        for kw in node.args[0].keywords:
                            if kw.arg != "reverse":
                                continue
                            reverseFlagValue = (
                                bool(kw.value.value)
                                if isinstance(kw.value, ast.Constant)
                                else None
                            )

                        if reverseFlagValue is None:
                            self.addErrorFromNode(
                                node, "M-193a", node.func.id, node.args[0].func.id
                            )
                        else:
                            self.addErrorFromNode(
                                node,
                                "M-193b",
                                node.func.id,
                                node.args[0].func.id,
                                not reverseFlagValue,
                            )

                    else:
                        self.addErrorFromNode(
                            node, "M-193c", node.func.id, node.args[0].func.id
                        )

                elif (
                    numPositionalArgs > 0
                    and isinstance(node.args[0], ast.Call)
                    and isinstance(node.args[0].func, ast.Name)
                    and (
                        (
                            node.func.id in {"set", "sorted"}
                            and node.args[0].func.id
                            in {"list", "reversed", "sorted", "tuple"}
                        )
                        or (
                            node.func.id in {"list", "tuple"}
                            and node.args[0].func.id in {"list", "tuple"}
                        )
                        or (node.func.id == "set" and node.args[0].func.id == "set")
                    )
                ):
                    self.addErrorFromNode(
                        node, "M-194", node.args[0].func.id, node.func.id
                    )

                elif (
                    node.func.id in {"reversed", "set", "sorted"}
                    and numPositionalArgs > 0
                    and isinstance(node.args[0], ast.Subscript)
                    and isinstance(node.args[0].slice, ast.Slice)
                    and node.args[0].slice.lower is None
                    and node.args[0].slice.upper is None
                    and isinstance(node.args[0].slice.step, ast.UnaryOp)
                    and isinstance(node.args[0].slice.step.op, ast.USub)
                    and isinstance(node.args[0].slice.step.operand, ast.Constant)
                    and node.args[0].slice.step.operand.n == 1
                ):
                    self.addErrorFromNode(node, "M-195", node.func.id)

                elif (
                    node.func.id == "map"
                    and node not in visitedMapCalls
                    and len(node.args) == 2
                    and isinstance(node.args[0], ast.Lambda)
                ):
                    self.addErrorFromNode(node, "M-197", "generator expression")

                elif (
                    node.func.id in ("list", "set", "dict")
                    and len(node.args) == 1
                    and isinstance(node.args[0], ast.Call)
                    and isinstance(node.args[0].func, ast.Name)
                    and node.args[0].func.id == "map"
                    and len(node.args[0].args) == 2
                    and isinstance(node.args[0].args[0], ast.Lambda)
                ):
                    # To avoid raising M197 on the map() call inside the list/set/dict.
                    mapCall = node.args[0]
                    visitedMapCalls.add(mapCall)

                    rewriteable = True
                    if node.func.id == "dict":
                        # For the generator expression to be rewriteable as a
                        # dict comprehension, its lambda must return a 2-tuple.
                        lambdaNode = node.args[0].args[0]
                        if (
                            not isinstance(lambdaNode.body, (ast.List, ast.Tuple))
                            or len(lambdaNode.body.elts) != 2
                        ):
                            rewriteable = False

                    if rewriteable:
                        comprehensionType = f"{node.func.id} comprehension"
                        self.addErrorFromNode(node, "M-197", comprehensionType)

            elif isinstance(node, (ast.DictComp, ast.ListComp, ast.SetComp)) and (
                len(node.generators) == 1
                and not node.generators[0].ifs
                and not node.generators[0].is_async
            ):
                if (
                    isinstance(node, (ast.ListComp, ast.SetComp))
                    and isinstance(node.elt, ast.Name)
                    and isinstance(node.generators[0].target, ast.Name)
                    and node.elt.id == node.generators[0].target.id
                ) or (
                    isinstance(node, ast.DictComp)
                    and isinstance(node.key, ast.Name)
                    and isinstance(node.value, ast.Name)
                    and isinstance(node.generators[0].target, ast.Tuple)
                    and len(node.generators[0].target.elts) == 2
                    and isinstance(node.generators[0].target.elts[0], ast.Name)
                    and node.generators[0].target.elts[0].id == node.key.id
                    and isinstance(node.generators[0].target.elts[1], ast.Name)
                    and node.generators[0].target.elts[1].id == node.value.id
                ):
                    self.addErrorFromNode(node, "M-196", compType[node.__class__])

                elif (
                    isinstance(node, ast.DictComp)
                    and isinstance(node.key, ast.Name)
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.generators[0].target, ast.Name)
                    and node.key.id == node.generators[0].target.id
                ):
                    self.addErrorFromNode(node, "M-200", compType[node.__class__])

            # flake8_no_comprehensions
            if (
                isinstance(
                    node, (ast.DictComp, ast.ListComp, ast.SetComp, ast.GeneratorExp)
                )
                and len(node.generators) > comprehensionArgs["MaxComprehensions"]
            ):
                self.addErrorFromNode(node, "M-201")

    def __dictShouldBeChecked(self, node):
        """
        Private function to test, if the node should be checked.

        @param node reference to the AST node
        @type ast.Dict
        @return flag indicating to check the node
        @rtype bool
        """
        if not all(AstUtilities.isString(key) for key in node.keys):
            return False

        if (
            "__IGNORE_WARNING__" in self.source[node.lineno - 1]
            or "__IGNORE_WARNING_M-251__" in self.source[node.lineno - 1]
            or "noqa: M-251" in self.source[node.lineno - 1]
        ):
            return False

        lineNumbers = [key.lineno for key in node.keys]
        return len(lineNumbers) == len(set(lineNumbers))

    def __checkDictWithSortedKeys(self):
        """
        Private method to check, if dictionary keys appear in sorted order.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Dict) and self.__dictShouldBeChecked(node):
                for key1, key2 in zip(node.keys, node.keys[1:]):
                    if key2.value < key1.value:
                        self.addErrorFromNode(key2, "M-251", key2.value, key1.value)

    def __checkGettext(self):
        """
        Private method to check the 'gettext' import statement.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom) and any(
                name.asname == "_" for name in node.names
            ):
                self.addErrorFromNode(node, "M-711", node.names[0].name)

    def __checkBugBear(self):
        """
        Private method for bugbear checks.
        """
        visitor = BugBearVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)

    def __checkReturn(self):
        """
        Private method to check return statements.
        """
        visitor = ReturnVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)

    def __checkDateTime(self):
        """
        Private method to check use of naive datetime functions.
        """
        # step 1: generate an augmented node tree containing parent info
        #         for each child node
        tree = copy.deepcopy(self.tree)
        for node in ast.walk(tree):
            for childNode in ast.iter_child_nodes(node):
                childNode._dtCheckerParent = node

        # step 2: perform checks and report issues
        visitor = DateTimeVisitor()
        visitor.visit(tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)

    def __checkSysVersion(self):
        """
        Private method to check the use of sys.version and sys.version_info.
        """
        visitor = SysVersionVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)

    def __checkProperties(self):
        """
        Private method to check for issue with property related methods.
        """
        properties = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                properties.clear()

            elif isinstance(node, ast.FunctionDef):
                propertyCount = 0
                for decorator in node.decorator_list:
                    # property getter method
                    if isinstance(decorator, ast.Name) and decorator.id == "property":
                        propertyCount += 1
                        properties.append(node.name)
                        if len(node.args.args) != 1:
                            self.addErrorFromNode(node, "M-260", len(node.args.args))

                    if isinstance(decorator, ast.Attribute):
                        # property setter method
                        if decorator.attr == "setter":
                            propertyCount += 1
                            if node.name != decorator.value.id:
                                if node.name in properties:
                                    self.addErrorFromNode(
                                        node, "M-265", node.name, decorator.value.id
                                    )
                                else:
                                    self.addErrorFromNode(
                                        node, "M-263", decorator.value.id, node.name
                                    )
                            if len(node.args.args) != 2:
                                self.addErrorFromNode(
                                    node, "M-261", len(node.args.args)
                                )

                        # property deleter method
                        if decorator.attr == "deleter":
                            propertyCount += 1
                            if node.name != decorator.value.id:
                                if node.name in properties:
                                    self.addErrorFromNode(
                                        node, "M-266", node.name, decorator.value.id
                                    )
                                else:
                                    self.addErrorFromNode(
                                        node, "M-264", decorator.value.id, node.name
                                    )
                            if len(node.args.args) != 1:
                                self.addErrorFromNode(
                                    node, "M-262", len(node.args.args)
                                )

                if propertyCount > 1:
                    self.addErrorFromNode(node, "M-267", node.name)

    #######################################################################
    ## The following methods check for implicitly concatenated strings.
    ##
    ## These methods are adapted from: flake8-implicit-str-concat v0.5.0
    ## Original: Copyright (c) 2023 Dylan Turner
    #######################################################################

    if sys.version_info < (3, 12):

        def __isImplicitStringConcat(self, first, second):
            """
            Private method to check, if the given strings indicate an implicit string
            concatenation.

            @param first first token
            @type tuple
            @param second second token
            @type tuple
            @return flag indicating an implicit string concatenation
            @rtype bool
            """
            return first.type == second.type == tokenize.STRING

    else:

        def __isImplicitStringConcat(self, first, second):
            """
            Private method to check, if the given strings indicate an implicit string
            concatenation.

            @param first first token
            @type tuple
            @param second second token
            @type tuple
            @return flag indicating an implicit string concatenation
            @rtype bool
            """
            return (
                (first.type == second.type == tokenize.STRING)
                or (
                    first.type == tokenize.STRING
                    and second.type == tokenize.FSTRING_START
                )
                or (
                    first.type == tokenize.FSTRING_END
                    and second.type == tokenize.STRING
                )
                or (
                    first.type == tokenize.FSTRING_END
                    and second.type == tokenize.FSTRING_START
                )
            )

    def __checkImplicitStringConcat(self):
        """
        Private method to check for implicitly concatenated strings.
        """
        tokensWithoutWhitespace = (
            tok
            for tok in self.__tokens
            if tok.type
            not in (
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
            )
        )
        for a, b in pairwise(tokensWithoutWhitespace):
            if self.__isImplicitStringConcat(a, b):
                self.addError(
                    a.end[0],
                    a.end[1],
                    "M-851" if a.end[0] == b.start[0] else "M-852",
                )

    def __checkExplicitStringConcat(self):
        """
        Private method to check for explicitly concatenated strings.
        """
        for node in ast.walk(self.tree):
            if (
                isinstance(node, ast.BinOp)
                and isinstance(node.op, ast.Add)
                and all(
                    AstUtilities.isBaseString(operand)
                    or isinstance(operand, ast.JoinedStr)
                    for operand in (node.left, node.right)
                )
            ):
                self.addErrorFromNode(node, "M-853")

    #################################################################################
    ## The following method checks default match cases.
    #################################################################################

    def __checkDefaultMatchCase(self):
        """
        Private method to check the default match case.
        """
        visitor = DefaultMatchCaseVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)

    #################################################################################
    ## The following method checks constant modifications.
    #################################################################################

    def __checkConstantModification(self):
        """
        Private method to check constant modifications.
        """
        visitor = ConstantModificationVisitor()
        visitor.visit(self.tree)
        for violation in visitor.violations:
            self.addErrorFromNode(*violation)
