# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the security checker.
"""

import collections

from CodeStyleTopicChecker import CodeStyleTopicChecker

from . import Checks
from .SecurityNodeVisitor import SecurityNodeVisitor


class SecurityChecker(CodeStyleTopicChecker):
    """
    Class implementing a checker for security issues.
    """

    Codes = [
        # assert used
        "S-101",
        # exec used
        "S-102",
        # bad file permissions
        "S-103",
        # bind to all interfaces
        "S-104",
        # hardcoded passwords
        "S-105",
        "S-106",
        "S-107"
        # hardcoded tmp directory
        "S-108",
        # try-except
        "S-110",
        "S-112",
        # flask app
        "S-201",
        # insecure function calls (prohibited)
        "S-301",
        "S-302",
        "S-303",
        "S-304",
        "S-305",
        "S-306",
        "S-307",
        "S-308",
        "S-310",
        "S-311",
        "S-312",
        "S-313",
        "S-314",
        "S-315",
        "S-316",
        "S-317",
        "S-318",
        "S-319",
        "S-321",
        "S-323",
        # hashlib functions
        "S-331",
        "S-332"
        # insecure imports (prohibited)
        "S-401",
        "S-402",
        "S-403",
        "S-404",
        "S-405",
        "S-406",
        "S-407",
        "S-408",
        "S-409",
        "S-411",
        "S-412",
        "S-413",
        # insecure certificate usage
        "S-501",
        # insecure SSL/TLS protocol version
        "S-502",
        "S-503",
        "S-504",
        # weak cryptographic keys
        "S-505",
        # YAML load
        "S-506",
        # SSH host key verification
        "S-507",
        # Shell injection
        "S-601",
        "S-602",
        "S-603",
        "S-604",
        "S-605",
        "S-606",
        "S-607",
        # SQL injection
        "S-608",
        # Wildcard injection
        "S-609",
        # Django SQL injection
        "S-610",
        "S-611",
        # insecure logging.config.listen()
        "S-612",
        "S-613",
        "S-614",
        # unsafe huggingface download
        "S-615",
        # Jinja2 templates
        "S-701",
        # Mako templates
        "S-702",
        # Django XSS vulnerability
        "S-703",
        # hardcoded AWS passwords
        "S-801",
        "S-802",
    ]
    Category = "S"

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
        @param args dictionary of arguments for the security checks
        @type dict
        """
        super().__init__(
            SecurityChecker.Category,
            source,
            filename,
            tree,
            select,
            ignore,
            expected,
            repeat,
            args,
        )

        checkersWithCodes = Checks.generateCheckersDict()

        self.__checkers = collections.defaultdict(list)
        for checkType, checkersList in checkersWithCodes.items():
            for checker, codes in checkersList:
                if any(
                    not (msgCode and self._ignoreCode(msgCode)) for msgCode in codes
                ):
                    self.__checkers[checkType].append(checker)

    def addError(self, lineNumber, offset, msgCode, severity, confidence, *args):
        """
        Public method to record an issue.

        @param lineNumber line number of the issue
        @type int
        @param offset position within line of the issue
        @type int
        @param msgCode message code
        @type str
        @param severity severity code (H = high, M = medium, L = low,
            U = undefined)
        @type str
        @param confidence confidence code (H = high, M = medium, L = low,
            U = undefined)
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
                    "line": lineNumber + 1,
                    "offset": offset,
                    "code": msgCode,
                    "args": args,
                    "severity": severity,
                    "confidence": confidence,
                }
            )

    def getConfig(self):
        """
        Public method to get the configuration dictionary.

        @return dictionary containing the configuration
        @rtype dict
        """
        return self.args

    def run(self):
        """
        Public method to check the given source against security related
        conditions.
        """
        if not self.filename:
            # don't do anything, if essential data is missing
            return

        if not self.__checkers:
            # don't do anything, if no codes were selected
            return

        securityNodeVisitor = SecurityNodeVisitor(
            self, self.__checkers, self.filename, self.source
        )
        securityNodeVisitor.generic_visit(self.tree)
        securityNodeVisitor.checkFile()
