# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the topic checker base class containing common methods.
"""

import copy


class CodeStyleTopicChecker:
    """
    Class implementing the topic checker base class.
    """

    def __init__(
        self, category, source, filename, tree, select, ignore, expected, repeat, args
    ):
        """
        Constructor

        @param category checker category code (one to three uppercase characters
        @type str
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
        self.__category = category

        codeFilter = f"{category}-"
        self.selected = tuple(x for x in select if x.startswith(codeFilter))
        self.ignored = tuple(
            x for x in ignore if x.startswith(codeFilter) or x == category
        )
        self.expected = [x for x in expected if x.startswith(codeFilter)]

        self.repeat = repeat
        self.filename = filename
        self.source = source[:]
        self.tree = copy.deepcopy(tree)
        self.args = args

        # statistics counters
        self.counters = {}

        # collection of detected errors
        self.errors = []

    def _initializeCheckers(self, checkersWithCodes):
        """
        Protected method to determine the list of check methods to be run.

        This list is determined considering the list if selected and ignored issue
        codes.

        @param checkersWithCodes DESCRIPTION
        @type TYPE
        """
        # checkers to be run
        self.__checkers = []

        for checker, msgCodes in checkersWithCodes:
            if any(not (msgCode and self._ignoreCode(msgCode)) for msgCode in msgCodes):
                self.__checkers.append(checker)

    def _ignoreCode(self, code):
        """
        Protected method to check if the message code should be ignored.

        @param code message code to check for
        @type str
        @return flag indicating to ignore the given code
        @rtype bool
        """
        return code in self.ignored or (
            code.startswith(self.ignored) and not code.startswith(self.selected)
        )

    def addError(self, lineNumber, offset, msgCode, *args):
        """
        Public method to record an issue.

        @param lineNumber line number of the issue (one based)
        @type int
        @param offset position within line of the issue
        @type int
        @param msgCode message code
        @type str
        @param args arguments for the message
        @type list
        """
        if self._ignoreCode(msgCode):
            return

        if msgCode in self.counters:
            self.counters[msgCode] += 1
        else:
            self.counters[msgCode] = 1

        # Don't care about expected codes
        if msgCode in self.expected:
            return

        if msgCode and (self.counters[msgCode] == 1 or self.repeat):
            # record the issue with one based line number
            self.errors.append(
                {
                    "file": self.filename,
                    "line": lineNumber,
                    "offset": offset,
                    "code": msgCode,
                    "args": args,
                }
            )

    def addErrorFromNode(self, node, msgCode, *args):
        """
        Public method to record an issue given the faulty ast node.

        @param node reference to the node containing the issue
        @type ast.AST
        @param msgCode message code
        @type str
        @param args arguments for the message
        @type list
        """
        self.addError(node.lineno, node.col_offset, msgCode, *args)

    def run(self):
        """
        Public method to execute the relevant checks.
        """
        if not self.filename:
            # don't do anything, if essential data is missing
            return

        if not self.__checkers:
            # don't do anything, if no codes were selected
            return

        for check in self.__checkers:
            check()
