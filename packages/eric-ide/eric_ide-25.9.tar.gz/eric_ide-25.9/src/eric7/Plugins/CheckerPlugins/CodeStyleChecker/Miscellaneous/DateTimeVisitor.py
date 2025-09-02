# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing a node visitor to check datetime function calls.
"""

import ast

import AstUtilities


class DateTimeVisitor(ast.NodeVisitor):
    """
    Class implementing a node visitor to check datetime function calls.

    Note: This class is modeled after flake8_datetimez v20.10.0 checker.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

        self.violations = []

    def __getFromKeywords(self, keywords, name):
        """
        Private method to get a keyword node given its name.

        @param keywords list of keyword argument nodes
        @type list of ast.AST
        @param name name of the keyword node
        @type str
        @return keyword node
        @rtype ast.AST
        """
        for keyword in keywords:
            if keyword.arg == name:
                return keyword

        return None

    def visit_Call(self, node):
        """
        Public method to handle a function call.

        Every datetime related function call is check for use of the naive
        variant (i.e. use without TZ info).

        @param node reference to the node to be processed
        @type ast.Call
        """
        # datetime.something()
        isDateTimeClass = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "datetime"
        )

        # datetime.datetime.something()
        isDateTimeModuleAndClass = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "datetime"
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "datetime"
        )

        if isDateTimeClass:
            if node.func.attr == "datetime":
                # datetime.datetime(2000, 1, 1, 0, 0, 0, 0,
                #                   datetime.timezone.utc)
                isCase1 = len(node.args) >= 8 and not (
                    AstUtilities.isNameConstant(node.args[7])
                    and AstUtilities.getValue(node.args[7]) is None
                )

                # datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
                tzinfoKeyword = self.__getFromKeywords(node.keywords, "tzinfo")
                isCase2 = tzinfoKeyword is not None and not (
                    AstUtilities.isNameConstant(tzinfoKeyword.value)
                    and AstUtilities.getValue(tzinfoKeyword.value) is None
                )

                if not (isCase1 or isCase2):
                    self.violations.append((node, "M-301"))

            elif node.func.attr == "time":
                # time(12, 10, 45, 0, datetime.timezone.utc)
                isCase1 = len(node.args) >= 5 and not (
                    AstUtilities.isNameConstant(node.args[4])
                    and AstUtilities.getValue(node.args[4]) is None
                )

                # datetime.time(12, 10, 45, tzinfo=datetime.timezone.utc)
                tzinfoKeyword = self.__getFromKeywords(node.keywords, "tzinfo")
                isCase2 = tzinfoKeyword is not None and not (
                    AstUtilities.isNameConstant(tzinfoKeyword.value)
                    and AstUtilities.getValue(tzinfoKeyword.value) is None
                )

                if not (isCase1 or isCase2):
                    self.violations.append((node, "M-321"))

            elif node.func.attr == "date":
                self.violations.append((node, "M-311"))

        if isDateTimeClass or isDateTimeModuleAndClass:
            if node.func.attr == "today":
                self.violations.append((node, "M-302"))

            elif node.func.attr == "utcnow":
                self.violations.append((node, "M-303"))

            elif node.func.attr == "utcfromtimestamp":
                self.violations.append((node, "M-304"))

            elif node.func.attr in "now":
                # datetime.now(UTC)
                isCase1 = (
                    len(node.args) == 1
                    and len(node.keywords) == 0
                    and not (
                        AstUtilities.isNameConstant(node.args[0])
                        and AstUtilities.getValue(node.args[0]) is None
                    )
                )

                # datetime.now(tz=UTC)
                tzKeyword = self.__getFromKeywords(node.keywords, "tz")
                isCase2 = tzKeyword is not None and not (
                    AstUtilities.isNameConstant(tzKeyword.value)
                    and AstUtilities.getValue(tzKeyword.value) is None
                )

                if not (isCase1 or isCase2):
                    self.violations.append((node, "M-305"))

            elif node.func.attr == "fromtimestamp":
                # datetime.fromtimestamp(1234, UTC)
                isCase1 = (
                    len(node.args) == 2
                    and len(node.keywords) == 0
                    and not (
                        AstUtilities.isNameConstant(node.args[1])
                        and AstUtilities.getValue(node.args[1]) is None
                    )
                )

                # datetime.fromtimestamp(1234, tz=UTC)
                tzKeyword = self.__getFromKeywords(node.keywords, "tz")
                isCase2 = tzKeyword is not None and not (
                    AstUtilities.isNameConstant(tzKeyword.value)
                    and AstUtilities.getValue(tzKeyword.value) is None
                )

                if not (isCase1 or isCase2):
                    self.violations.append((node, "M-306"))

            elif node.func.attr == "strptime":
                # datetime.strptime(...).replace(tzinfo=UTC)
                parent = getattr(node, "_dtCheckerParent", None)
                pparent = getattr(parent, "_dtCheckerParent", None)
                if not (
                    isinstance(parent, ast.Attribute) and parent.attr == "replace"
                ) or not isinstance(pparent, ast.Call):
                    isCase1 = False
                else:
                    tzinfoKeyword = self.__getFromKeywords(pparent.keywords, "tzinfo")
                    isCase1 = tzinfoKeyword is not None and not (
                        AstUtilities.isNameConstant(tzinfoKeyword.value)
                        and AstUtilities.getValue(tzinfoKeyword.value) is None
                    )

                if not isCase1:
                    self.violations.append((node, "M-307"))

            elif node.func.attr == "fromordinal":
                self.violations.append((node, "M-308"))

        # date.something()
        isDateClass = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "date"
        )

        # datetime.date.something()
        isDateModuleAndClass = (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "date"
            and isinstance(node.func.value.value, ast.Name)
            and node.func.value.value.id == "datetime"
        )

        if isDateClass or isDateModuleAndClass:
            if node.func.attr == "today":
                self.violations.append((node, "M-312"))

            elif node.func.attr == "fromtimestamp":
                self.violations.append((node, "M-313"))

            elif node.func.attr == "fromordinal":
                self.violations.append((node, "M-314"))

            elif node.func.attr == "fromisoformat":
                self.violations.append((node, "M-315"))

        self.generic_visit(node)


#
# eflag: noqa = M-891
