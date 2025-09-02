# -*- coding: utf-8 -*-

# Copyright (c) 2024 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for the use of 'torch.load' and 'torch.save'.
"""

#
# This is a modified version of the one found in the bandit package.
#
# Original Copyright (c) 2024 Stacklok, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Call": [
            (checkPytorchLoad, ("S-614",)),
        ],
    }


def checkPytorchLoad(reportError, context, _config):
    """
    Function to check for the use of 'torch.load'.

    Using `torch.load` with untrusted data can lead to arbitrary code
    execution. The safe alternative is to use `weights_only=True` or
    the safetensors library.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param _config dictionary with configuration data (unused)
    @type dict
    """
    imported = context.isModuleImportedExact("torch")
    qualname = context.callFunctionNameQual
    if not imported and isinstance(qualname, str):
        return

    qualnameList = qualname.split(".")
    func = qualnameList[-1]
    if all(
        [
            "torch" in qualnameList,
            func == "load",
        ]
    ):
        # For torch.load, check if weights_only=True is specified
        weightsOnly = context.getCallArgValue("weights_only")
        if weightsOnly == "True" or weightsOnly is True:
            return

        reportError(
            context.node.lineno - 1,
            context.node.col_offset,
            "S-614",
            "M",
            "H",
        )
