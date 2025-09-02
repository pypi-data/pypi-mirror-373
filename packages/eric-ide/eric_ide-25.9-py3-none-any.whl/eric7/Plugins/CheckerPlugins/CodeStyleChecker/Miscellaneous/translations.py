# -*- coding: utf-8 -*-

# Copyright (c) 2020 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#


"""
Module implementing message translations for the code style plugin messages
(miscellaneous part).
"""

from PyQt6.QtCore import QCoreApplication

_miscellaneousMessages = {
    ## Coding line
    "M-101": QCoreApplication.translate(
        "MiscellaneousChecker",
        "coding magic comment not found",
    ),
    "M-102": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unknown encoding ({0}) found in coding magic comment",
    ),
    ## Copyright
    "M-111": QCoreApplication.translate(
        "MiscellaneousChecker",
        "copyright notice not present",
    ),
    "M-112": QCoreApplication.translate(
        "MiscellaneousChecker",
        "copyright notice contains invalid author",
    ),
    ## Shadowed Builtins
    "M-131": QCoreApplication.translate(
        "MiscellaneousChecker",
        '"{0}" is a Python builtin and is being shadowed; '
        "consider renaming the variable",
    ),
    "M-132": QCoreApplication.translate(
        "MiscellaneousChecker",
        '"{0}" is used as an argument and thus shadows a '
        "Python builtin; consider renaming the argument",
    ),
    ## Comprehensions
    "M-180": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary generator - rewrite as a list comprehension",
    ),
    "M-181": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary generator - rewrite as a set comprehension",
    ),
    "M-182": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary generator - rewrite as a dict comprehension",
    ),
    "M-183": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary list comprehension - rewrite as a set comprehension",
    ),
    "M-184": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary list comprehension - rewrite as a dict comprehension",
    ),
    "M-185": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} literal - rewrite as a {1} literal",
    ),
    "M-186": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} literal - rewrite as a {1} literal",
    ),
    "M-188": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} call - rewrite as a literal",
    ),
    "M-189a": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} passed to tuple() - remove the outer call to {1}()",
    ),
    "M-189b": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} passed to tuple() - rewrite as a {1} literal",
    ),
    "M-190a": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} passed to list() - remove the outer call to {1}()",
    ),
    "M-190b": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} passed to list() - rewrite as a {1} literal",
    ),
    "M-191": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary list call - remove the outer call to list()",
    ),
    "M-193a": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} call around {1}() - toggle reverse argument to sorted()",
    ),
    "M-193b": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} call around {1}() - use sorted(..., reverse={2!r})",
    ),
    "M-193c": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} call around {1}()",
    ),
    "M-194": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} call within {1}()",
    ),
    "M-195": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary subscript reversal of iterable within {0}()",
    ),
    "M-196": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} comprehension - rewrite using {0}()",
    ),
    "M-197": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary use of map - use a {0} instead",
    ),
    "M-198": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} passed to dict() - remove the outer call to dict()",
    ),
    "M-199": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary list comprehension passed to {0}() prevents short-circuiting"
        " - rewrite as a generator",
    ),
    "M-200": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unnecessary {0} comprehension - rewrite using dict.fromkeys()",
    ),
    "M-201": QCoreApplication.translate(
        "MiscellaneousChecker",
        "maximum number of comprehensions exceeded",
    ),
    ## Dictionaries with sorted keys
    "M-251": QCoreApplication.translate(
        "MiscellaneousChecker",
        "sort keys - '{0}' should be before '{1}'",
    ),
    ## Property
    "M-260": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the number of arguments for property getter method is wrong"
        " (should be 1 instead of {0})",
    ),
    "M-261": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the number of arguments for property setter method is wrong"
        " (should be 2 instead of {0})",
    ),
    "M-262": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the number of arguments for property deleter method is wrong"
        " (should be 1 instead of {0})",
    ),
    "M-263": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the name of the setter method is wrong (should be '{0}' instead of '{1}')",
    ),
    "M-264": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the name of the deleter method is wrong (should be '{0}' instead of '{1}')",
    ),
    "M-265": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the name of the setter decorator is wrong (should be '{0}' instead of '{1}')",
    ),
    "M-266": QCoreApplication.translate(
        "MiscellaneousChecker",
        "the name of the deleter decorator is wrong (should be '{0}' instead of '{1}')",
    ),
    "M-267": QCoreApplication.translate(
        "MiscellaneousChecker",
        "multiple decorators were used to declare property '{0}'",
    ),
    ## Naive datetime usage
    "M-301": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime()' without 'tzinfo' argument should be avoided",
    ),
    "M-302": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.today()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=)' instead.",
    ),
    "M-303": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.utcnow()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=datetime.timezone.utc)' instead.",
    ),
    "M-304": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.utcfromtimestamp()' should be avoided.\n"
        "Use 'datetime.datetime.fromtimestamp(..., tz=datetime.timezone.utc)' instead.",
    ),
    "M-305": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.now()' without 'tz' argument should be avoided",
    ),
    "M-306": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.fromtimestamp()' without 'tz' argument"
        " should be avoided",
    ),
    "M-307": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.strptime()' should be followed by"
        " '.replace(tzinfo=)'",
    ),
    "M-308": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.datetime.fromordinal()' should be avoided",
    ),
    "M-311": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date()' should be avoided.\n"
        "Use 'datetime.datetime(, tzinfo=).date()' instead.",
    ),
    "M-312": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.today()' should be avoided.\n"
        "Use 'datetime.datetime.now(tz=).date()' instead.",
    ),
    "M-313": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromtimestamp()' should be avoided.\n"
        "Use 'datetime.datetime.fromtimestamp(tz=).date()' instead.",
    ),
    "M-314": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromordinal()' should be avoided",
    ),
    "M-315": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.date.fromisoformat()' should be avoided",
    ),
    "M-321": QCoreApplication.translate(
        "MiscellaneousChecker",
        "use of 'datetime.time()' without 'tzinfo' argument should be avoided",
    ),
    ## sys.version and sys.version_info usage
    "M-401": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[:3]' referenced (Python 3.10), use 'sys.version_info'",
    ),
    "M-402": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[2]' referenced (Python 3.10), use 'sys.version_info'",
    ),
    "M-403": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version' compared to string (Python 3.10), use 'sys.version_info'",
    ),
    "M-411": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info[0] == 3' referenced (Python 4), use '>='",
    ),
    "M-412": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'six.PY3' referenced (Python 4), use 'not six.PY2'",
    ),
    "M-413": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info[1]' compared to integer (Python 4),"
        " compare 'sys.version_info' to tuple",
    ),
    "M-414": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version_info.minor' compared to integer (Python 4),"
        " compare 'sys.version_info' to tuple",
    ),
    "M-421": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[0]' referenced (Python 10), use 'sys.version_info'",
    ),
    "M-422": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version' compared to string (Python 10), use 'sys.version_info'",
    ),
    "M-423": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'sys.version[:1]' referenced (Python 10), use 'sys.version_info'",
    ),
    ## Bugbear
    "M-501": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Do not use bare 'except:', it also catches unexpected events like memory"
        " errors, interrupts, system exit, and so on. Prefer excepting specific"
        " exceptions. If you're sure what you're doing, be explicit and write"
        " 'except BaseException:'.",
    ),
    "M-502": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Python does not support the unary prefix increment",
    ),
    "M-503": QCoreApplication.translate(
        "MiscellaneousChecker",
        "assigning to 'os.environ' does not clear the environment -"
        " use 'os.environ.clear()'",
    ),
    "M-504": QCoreApplication.translate(
        "MiscellaneousChecker",
        """using 'hasattr(x, "__call__")' to test if 'x' is callable is"""
        """ unreliable. Use 'callable(x)' for consistent results.""",
    ),
    "M-505": QCoreApplication.translate(
        "MiscellaneousChecker",
        "using .strip() with multi-character strings is misleading. Use .replace(),"
        " .removeprefix(), .removesuffix(), or regular expressions to remove string"
        " fragments.",
    ),
    "M-506": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Do not use mutable data structures for argument defaults. They are created"
        " during function definition time. All calls to the function reuse this one"
        " instance of that data structure, persisting changes between them.",
    ),
    "M-507": QCoreApplication.translate(
        "MiscellaneousChecker",
        "loop control variable {0} not used within the loop body -"
        " start the name with an underscore",
    ),
    "M-508": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Do not perform function calls in argument defaults. The call is performed"
        " only once at function definition time. All calls to your function will reuse"
        " the result of that definition-time function call.  If this is intended,"
        " assign the function call to a module-level variable and use that variable as"
        " a default value.",
    ),
    "M-509": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call getattr with a constant attribute value",
    ),
    "M-510": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call setattr with a constant attribute value",
    ),
    "M-511": QCoreApplication.translate(
        "MiscellaneousChecker",
        "do not call assert False since python -O removes these calls",
    ),
    "M-512": QCoreApplication.translate(
        "MiscellaneousChecker",
        "return/continue/break inside finally blocks cause exceptions to be silenced."
        " Exceptions should be silenced in except{0} blocks. Control statements can be"
        " moved outside the finally block.",
    ),
    "M-513": QCoreApplication.translate(
        "MiscellaneousChecker",
        "A length-one tuple literal is redundant. Write 'except{1} {0}:' instead of"
        " 'except{1} ({0},):'.",
    ),
    "M-514": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Redundant exception types in 'except{3} ({0}){1}:'. Write 'except{3} {2}{1}:',"
        " which catches exactly the same exceptions.",
    ),
    "M-515": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Result of comparison is not used. This line doesn't do anything. Did you"
        " intend to prepend it with assert?",
    ),
    "M-516": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Cannot raise a literal. Did you intend to return it or raise an Exception?",
    ),
    "M-517": QCoreApplication.translate(
        "MiscellaneousChecker",
        "'assertRaises(Exception)' and 'pytest.raises(Exception)' should "
        "be considered evil. They can lead to your test passing even if the "
        "code being tested is never executed due to a typo. Assert for a more "
        "specific exception (builtin or custom), or use 'assertRaisesRegex' "
        "(if using 'assertRaises'), or add the 'match' keyword argument (if "
        "using 'pytest.raises'), or use the context manager form with a target.",
    ),
    "M-518": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Found useless {0} expression. Consider either assigning it to a variable or"
        " removing it.",
    ),
    "M-519": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Use of 'functools.lru_cache' or 'functools.cache' on methods can lead to"
        " memory leaks. The cache may retain instance references, preventing garbage"
        " collection.",
    ),
    "M-520": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Found for loop that reassigns the iterable it is iterating with each"
        " iterable value.",
    ),
    "M-521": QCoreApplication.translate(
        "MiscellaneousChecker",
        "f-string used as docstring. This will be interpreted by python as a joined"
        " string rather than a docstring.",
    ),
    "M-522": QCoreApplication.translate(
        "MiscellaneousChecker",
        "No arguments passed to 'contextlib.suppress'. No exceptions will be"
        " suppressed and therefore this context manager is redundant.",
    ),
    "M-523": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Function definition does not bind loop variable '{0}'.",
    ),
    "M-524": QCoreApplication.translate(
        "MiscellaneousChecker",
        "{0} is an abstract base class, but none of the methods it defines are"
        " abstract. This is not necessarily an error, but you might have forgotten to"
        " add the @abstractmethod decorator, potentially in conjunction with"
        " @classmethod, @property and/or @staticmethod.",
    ),
    "M-525": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Exception '{0}' has been caught multiple times. Only the first except{1} will"
        " be considered and all other except{1} catches can be safely removed.",
    ),
    "M-526": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Star-arg unpacking after a keyword argument is strongly discouraged,"
        " because it only works when the keyword parameter is declared after all"
        " parameters supplied by the unpacked sequence, and this change of ordering can"
        " surprise and mislead readers.",
    ),
    "M-527": QCoreApplication.translate(
        "MiscellaneousChecker",
        "{0} is an empty method in an abstract base class, but has no abstract"
        " decorator. Consider adding @abstractmethod.",
    ),
    "M-528": QCoreApplication.translate(
        "MiscellaneousChecker",
        "No explicit stacklevel argument found. The warn method from the"
        " warnings module uses a stacklevel of 1 by default. This will only show a"
        " stack trace for the line on which the warn method is called."
        " It is therefore recommended to use a stacklevel of 2 or"
        " greater to provide more information to the user.",
    ),
    "M-529": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Using 'except{0} ():' with an empty tuple does not handle/catch "
        "anything. Add exceptions to handle.",
    ),
    "M-530": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Except handlers should only be names of exception classes",
    ),
    "M-531": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Using the generator returned from 'itertools.groupby()' more than once"
        " will do nothing on the second usage. Save the result to a list, if the"
        " result is needed multiple times.",
    ),
    "M-532": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Possible unintentional type annotation (using ':'). Did you mean to"
        " assign (using '=')?",
    ),
    "M-533": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Set should not contain duplicate item '{0}'. Duplicate items will be replaced"
        " with a single item at runtime.",
    ),
    "M-534": QCoreApplication.translate(
        "MiscellaneousChecker",
        "re.{0} should get '{1}' and 'flags' passed as keyword arguments to avoid"
        " confusion due to unintuitive argument positions.",
    ),
    "M-535": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Static key in dict comprehension: {0!r}.",
    ),
    "M-536": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Don't except 'BaseException' unless you plan to re-raise it.",
    ),
    "M-537": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Class '__init__' methods must not return or yield any values.",
    ),
    "M-539": QCoreApplication.translate(
        "MiscellaneousChecker",
        "ContextVar with mutable literal or function call as default. This is only"
        " evaluated once, and all subsequent calls to `.get()` will return the same"
        " instance of the default.",
    ),
    "M-540": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Exception with added note not used. Did you forget to raise it?",
    ),
    "M-541": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Repeated key-value pair in dictionary literal.",
    ),
    ## Bugbear, opininonated
    "M-569": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Editing a loop's mutable iterable often leads to unexpected results/bugs.",
    ),
    ## Bugbear++
    "M-581": QCoreApplication.translate(
        "MiscellaneousChecker",
        "unncessary f-string",
    ),
    "M-582": QCoreApplication.translate(
        "MiscellaneousChecker",
        "cannot use 'self.__class__' as first argument of 'super()' call",
    ),
    ## Format Strings
    "M-601": QCoreApplication.translate(
        "MiscellaneousChecker",
        "found {0} formatter",
    ),
    "M-611": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format string does contain unindexed parameters",
    ),
    "M-612": QCoreApplication.translate(
        "MiscellaneousChecker",
        "docstring does contain unindexed parameters",
    ),
    "M-613": QCoreApplication.translate(
        "MiscellaneousChecker",
        "other string does contain unindexed parameters",
    ),
    "M-621": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses too large index ({0})",
    ),
    "M-622": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses missing keyword ({0})",
    ),
    "M-623": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses keyword arguments but no named entries",
    ),
    "M-624": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses variable arguments but no numbered entries",
    ),
    "M-625": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call uses implicit and explicit indexes together",
    ),
    "M-631": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call provides unused index ({0})",
    ),
    "M-632": QCoreApplication.translate(
        "MiscellaneousChecker",
        "format call provides unused keyword ({0})",
    ),
    ## Future statements
    "M-701": QCoreApplication.translate(
        "MiscellaneousChecker",
        "expected these __future__ imports: {0}; but only got: {1}",
    ),
    "M-702": QCoreApplication.translate(
        "MiscellaneousChecker",
        "expected these __future__ imports: {0}; but got none",
    ),
    ## Gettext
    "M-711": QCoreApplication.translate(
        "MiscellaneousChecker",
        "gettext import with alias _ found: {0}",
    ),
    ##~ print() statements
    "M-801": QCoreApplication.translate(
        "MiscellaneousChecker",
        "print statement found",
    ),
    ## one element tuple
    "M-811": QCoreApplication.translate(
        "MiscellaneousChecker",
        "one element tuple found",
    ),
    ## Mutable Defaults
    "M-821": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of type {0}",
    ),
    "M-822": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of type {0}",
    ),
    "M-823": QCoreApplication.translate(
        "MiscellaneousChecker",
        "mutable default argument of function call '{0}'",
    ),
    ##~ return statements
    "M-831": QCoreApplication.translate(
        "MiscellaneousChecker",
        "None should not be added at any return if function has no return"
        " value except None",
    ),
    "M-832": QCoreApplication.translate(
        "MiscellaneousChecker",
        "an explicit value at every return should be added if function has"
        " a return value except None",
    ),
    "M-833": QCoreApplication.translate(
        "MiscellaneousChecker",
        "an explicit return at the end of the function should be added if"
        " it has a return value except None",
    ),
    "M-834": QCoreApplication.translate(
        "MiscellaneousChecker",
        "a value should not be assigned to a variable if it will be used as a"
        " return value only",
    ),
    ## line continuation
    "M-841": QCoreApplication.translate(
        "MiscellaneousChecker",
        "prefer implied line continuation inside parentheses, "
        "brackets and braces as opposed to a backslash",
    ),
    ## implicitly concatenated strings
    "M-851": QCoreApplication.translate(
        "MiscellaneousChecker",
        "implicitly concatenated string or bytes literals on one line",
    ),
    "M-852": QCoreApplication.translate(
        "MiscellaneousChecker",
        "implicitly concatenated string or bytes literals over continuation line",
    ),
    "M-853": QCoreApplication.translate(
        "MiscellaneousChecker",
        "explicitly concatenated string or bytes should be implicitly concatenated",
    ),
    ## commented code
    "M-891": QCoreApplication.translate(
        "MiscellaneousChecker",
        "commented code lines should be removed",
    ),
    ## structural pattern matching
    "M-901": QCoreApplication.translate(
        "MiscellaneousChecker",
        "matching a default value should raise a `ValueError` exception",
    ),
    "M-902": QCoreApplication.translate(
        "MiscellaneousChecker",
        "matching a default value should not contain a `return` statement before "
        "raising a `ValueError` exception",
    ),
    ## constant modification
    "M-911": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Reassignment of constant '{0}' in scope '{1}'",
    ),
    "M-912": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Modification of class constant '{0}'",
    ),
    "M-913": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Augmented assignment to constant '{0}' in scope '{1}'",
    ),
    "M-914": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Augmented assignment to class constant '{0}'",
    ),
    "M-915": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Potential modification of constant '{0}' through method call in scope '{1}'",
    ),
    "M-916": QCoreApplication.translate(
        "MiscellaneousChecker",
        "Constant '{0}' is defined as a mutable type",
    ),
}

_miscellaneousMessagesSampleArgs = {
    ## Coding line
    "M-102": ["enc42"],
    ## Shadowed Builtins
    "M-131": ["list"],
    "M-132": ["list"],
    ## Comprehensions
    "M-185": ["list", "set"],
    "M-186": ["list", "dict"],
    "M-188": ["list"],
    "M-189a": ["tuple", "tuple"],
    "M-189b": ["list", "tuple"],
    "M-190a": ["list", "list"],
    "M-190b": ["tuple", "list"],
    "M-193a": ["reversed", "sorted"],
    "M-193b": ["reversed", "sorted", "True"],
    "M-193c": ["list", "sorted"],
    "M-194": ["list", "sorted"],
    "M-195": ["sorted"],
    "M-196": ["list"],
    "M-197": ["list"],
    "M-198": ["dict comprehension"],
    "M-199": ["any"],
    "M-200": ["dict"],
    ## Dictionaries with sorted keys
    "M-251": ["bar", "foo"],
    ## Property
    "M-260": [2],
    "M-261": [1],
    "M-262": [2],
    "M-263": ["foo", "bar"],
    "M-264": ["foo", "bar"],
    "M-265": ["foo", "bar"],
    "M-266": ["foo", "bar"],
    "M-267": ["foo"],
    ## Bugbear
    "M-507": ["x"],
    "M-512": [""],
    "M-513": ["Exception", ""],
    "M-514": ["OSError, IOError", " as err", "OSError", ""],
    "M-518": ["List"],
    "M-523": ["x"],
    "M-524": ["foobar"],
    "M-525": ["OSError", ""],
    "M-527": ["foo"],
    "M-529": [""],
    "M-533": ["foo"],
    "M-534": ["split", "maxsplit"],
    "M-535": ["foo"],
    ## Format Strings
    "M-601": ["%s"],
    "M-621": [5],
    "M-622": ["foo"],
    "M-631": [5],
    "M-632": ["foo"],
    ## Future statements
    "M-701": ["print_function, unicode_literals", "print_function"],
    "M-702": ["print_function, unicode_literals"],
    ## Gettext
    "M-711": ["lgettext"],
    ## Mutable Defaults
    "M-821": ["Dict"],
    "M-822": ["Call"],
    "M-823": ["dict"],
    ## constant modification
    "M-911": ["FOO", "bar.baz"],
    "M-912": ["FOO"],
    "M-913": ["FOO", "bar.baz"],
    "M-914": ["FOO"],
    "M-915": ["FOO", "bar.baz"],
    "M-916": ["FOO"],
}
