# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for potential XSS on markupsafe.Markup use.
"""

#
# This is a modified version of the one found in the bandit package.
#
# Copyright (c) 2025 David Salvisberg
#
# SPDX-License-Identifier: Apache-2.0
#

import ast

from Security import SecurityUtils
from Security.SecurityDefaults import SecurityDefaults


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Call": [
            (markupsafeMarkupXss, ("S-704",)),
        ],
    }


def markupsafeMarkupXss(reportError, context, config):
    """
    Function to check for potential XSS on markupsafe.Markup use.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param config dictionary with configuration data (unused)
    @type dict
    """
    qualname = context.callFunctionNameQual
    if qualname not in (
        "markupsafe.Markup",
        "flask.Markup",
    ) and qualname not in config.get(
        "extend_markup_names", SecurityDefaults["extend_markup_names"]
    ):
        # not a Markup call
        return

    args = context.node.args
    if not args or isinstance(args[0], ast.Constant):
        # both no arguments and a constant are fine
        return

    allowedCalls = config.get("allowed_calls", SecurityDefaults["allowed_calls"])
    if (
        allowedCalls
        and isinstance(args[0], ast.Call)
        and SecurityUtils.getCallName(args[0], context.importAliases) in allowedCalls
    ):
        # the argument contains a whitelisted call
        return

    reportError(
        context.node.lineno - 1,
        context.node.col_offset,
        "S-704",
        "M",
        "H",
        qualname,
        context.callFunctionName,
    )
