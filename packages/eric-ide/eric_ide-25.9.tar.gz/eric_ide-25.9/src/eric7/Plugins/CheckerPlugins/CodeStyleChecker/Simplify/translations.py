# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(simplify part).
"""

from PyQt6.QtCore import QCoreApplication

_simplifyMessages = {
    # Python-specifics
    "Y-101": QCoreApplication.translate(
        "SimplifyChecker",
        """Multiple "isinstance()" calls which can be merged into a single """
        '''call for variable "{0}"''',
    ),
    "Y-102": QCoreApplication.translate(
        "SimplifyChecker",
        """Use a single if-statement instead of nested if-statements""",
    ),
    "Y-103": QCoreApplication.translate(
        "SimplifyChecker", """Return the condition "{0}" directly"""
    ),
    "Y-104": QCoreApplication.translate("SimplifyChecker", '''Use "yield from {0}"'''),
    "Y-105": QCoreApplication.translate(
        "SimplifyChecker", '''Use "with contextlib.suppress({0}):"'''
    ),
    "Y-106": QCoreApplication.translate(
        "SimplifyChecker", """Handle error-cases first"""
    ),
    "Y-107": QCoreApplication.translate(
        "SimplifyChecker", """Don't use return in try/except and finally"""
    ),
    "Y-108": QCoreApplication.translate(
        "SimplifyChecker",
        """Use ternary operator "{0} = {1} if {2} else {3}" """
        """instead of if-else-block""",
    ),
    "Y-109": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} in {1}" instead of "{2}"'''
    ),
    "Y-110": QCoreApplication.translate(
        "SimplifyChecker", '''Use "any({0} for {1} in {2})"'''
    ),
    "Y-111": QCoreApplication.translate(
        "SimplifyChecker", '''Use "all({0} for {1} in {2})"'''
    ),
    "Y-112": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-113": QCoreApplication.translate(
        "SimplifyChecker", '''Use enumerate instead of "{0}"'''
    ),
    "Y-114": QCoreApplication.translate(
        "SimplifyChecker", """Use logical or ("({0}) or ({1})") and a single body"""
    ),
    "Y-115": QCoreApplication.translate(
        "SimplifyChecker", """Use context handler for opening files"""
    ),
    "Y-116": QCoreApplication.translate(
        "SimplifyChecker",
        """Use a dictionary lookup instead of 3+ if/elif-statements: """
        """return {0}""",
    ),
    "Y-117": QCoreApplication.translate(
        "SimplifyChecker", """Use "{0}" instead of multiple with statements"""
    ),
    "Y-118": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} in {1}" instead of "{0} in {1}.keys()"'''
    ),
    "Y-119": QCoreApplication.translate(
        "SimplifyChecker", '''Use a dataclass for "class {0}"'''
    ),
    "Y-120": QCoreApplication.translate(
        "SimplifyChecker", '''Use "class {0}:" instead of "class {0}(object):"'''
    ),
    "Y-121": QCoreApplication.translate(
        "SimplifyChecker",
        '''Use "class {0}({1}):" instead of "class {0}({1}, object):"''',
    ),
    "Y-122": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}.get({1})" instead of "if {1} in {0}: {0}[{1}]"'''
    ),
    "Y-123": QCoreApplication.translate(
        "SimplifyChecker", """Use "{0} = {1}.get({2}, {3})" instead of an if-block"""
    ),
    # Python-specifics not part of flake8-simplify
    "Y-181": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-182": QCoreApplication.translate(
        "SimplifyChecker", '''Use "super()" instead of "{0}"'''
    ),
    # Comparations
    "Y-201": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} != {1}" instead of "not {0} == {1}"'''
    ),
    "Y-202": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} == {1}" instead of "not {0} != {1}"'''
    ),
    "Y-203": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} not in {1}" instead of "not {0} in {1}"'''
    ),
    "Y-204": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} >= {1}" instead of "not ({0} < {1})"'''
    ),
    "Y-205": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} > {1}" instead of "not ({0} <= {1})"'''
    ),
    "Y-206": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} <= {1}" instead of "not ({0} > {1})"'''
    ),
    "Y-207": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0} < {1}" instead of "not ({0} >= {1})"'''
    ),
    "Y-208": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "not (not {0})"'''
    ),
    "Y-211": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{1}" instead of "True if {0} else False"'''
    ),
    "Y-212": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{1}" instead of "False if {0} else True"'''
    ),
    "Y-213": QCoreApplication.translate(
        "SimplifyChecker",
        '''Use "{0} if {0} else {1}" instead of "{1} if not {0} else {0}"''',
    ),
    "Y-221": QCoreApplication.translate(
        "SimplifyChecker", '''Use "False" instead of "{0} and not {0}"'''
    ),
    "Y-222": QCoreApplication.translate(
        "SimplifyChecker", '''Use "True" instead of "{0} or not {0}"'''
    ),
    "Y-223": QCoreApplication.translate(
        "SimplifyChecker", '''Use "True" instead of "... or True"'''
    ),
    "Y-224": QCoreApplication.translate(
        "SimplifyChecker", '''Use "False" instead of "... and False"'''
    ),
    # Opinionated
    "Y-301": QCoreApplication.translate(
        "SimplifyChecker",
        """Use "{1} == {0}" instead of "{0} == {1}" (Yoda-condition)""",
    ),
    # General Code Style
    "Y-401": QCoreApplication.translate(
        "SimplifyChecker", """Use keyword-argument instead of magic boolean"""
    ),
    "Y-402": QCoreApplication.translate(
        "SimplifyChecker", """Use keyword-argument instead of magic number"""
    ),
    # f-Strings
    "Y-411": QCoreApplication.translate("SimplifyChecker", "Do not nest f-strings"),
    # Additional Checks
    "Y-901": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-904": QCoreApplication.translate(
        "SimplifyChecker", """Initialize dictionary "{0}" directly"""
    ),
    "Y-905": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-906": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-907": QCoreApplication.translate(
        "SimplifyChecker", '''Use "Optional[{0}]" instead of "{1}"'''
    ),
    "Y-909": QCoreApplication.translate(
        "SimplifyChecker", '''Remove reflexive assignment "{0}"'''
    ),
    "Y-910": QCoreApplication.translate(
        "SimplifyChecker", '''Use "{0}" instead of "{1}"'''
    ),
    "Y-911": QCoreApplication.translate(
        "SimplifyChecker",
        '''Use "{0}.items()" instead of "zip({0}.keys(), {0}.values())"''',
    ),
}

_simplifyMessagesSampleArgs = {
    # Python-specifics
    "Y-101": ["foo"],
    "Y-103": ["foo != bar"],
    "Y-104": ["iterable"],
    "Y-105": ["Exception"],
    "Y-108": ["foo", "bar", "condition", "baz"],
    "Y-109": ["foo", "[1, 42]", "foo == 1 or foo == 42"],
    "Y-110": ["check", "foo", "iterable"],
    "Y-111": ["check", "foo", "iterable"],
    "Y-112": ["FOO", "foo"],
    "Y-113": ["foo"],
    "Y-114": ["foo > 42", "bar < 42"],
    "Y-116": ["bar_dict.get(foo, 42)"],
    "Y-117": ["with Foo() as foo, Bar() as bar:"],
    "Y-118": ["foo", "bar_dict"],
    "Y-119": ["Foo"],
    "Y-120": ["Foo"],
    "Y-121": ["FooBar", "Foo"],
    "Y-122": ["bar_dict", "'foo'"],
    "Y-123": ["foo", "fooDict", "bar", "default"],
    "Y-124": ["foo", "bar"],
    # Python-specifics not part of flake8-simplify
    "Y-181": ["foo += 42", "foo = foo + 42"],
    "Y-182": ["super()"],
    # Comparations
    "Y-201": ["foo", "bar"],
    "Y-202": ["foo", "bar"],
    "Y-203": ["foo", "bar"],
    "Y-204": ["foo", "bar"],
    "Y-205": ["foo", "bar"],
    "Y-206": ["foo", "bar"],
    "Y-207": ["foo", "bar"],
    "Y-208": ["foo"],
    "Y-211": ["foo", "bool(foo)"],
    "Y-212": ["foo", "not foo"],
    "Y-213": ["foo", "bar"],
    "Y-221": ["foo"],
    "Y-222": ["foo"],
    # Opinionated
    "Y-301": ["42", "foo"],
    # General Code Style
    # Additional checks
    "Y-901": ["foo == bar", "bool(foo == bar)"],
    "Y-904": ["foo"],
    "Y-905": [
        """["de", "com", "net", "org"]""",
        """domains = "de com net org".split()""",
    ],
    "Y-906": ["os.path.join(a, b, c)", "os.path.join(a,os.path.join(b,c))"],
    "Y-907": ["int", "Union[int, None]"],
    "Y-909": ["foo = foo"],
    "Y-911": ["foo"],
}
