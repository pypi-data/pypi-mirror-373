# -*- coding: utf-8 -*-

# Copyright (c) 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing checks for unsafe Hugging Face Hub downloads.
"""

#
# This is a modified version of the one found in the bandit package.
#
# SPDX-License-Identifier: Apache-2.0
#

################################################################################
## This plugin checks for unsafe downloads from Hugging Face Hub without proper
## integrity verification. Downloading models, datasets, or files without
## specifying a revision based on an immmutable revision (commit) can
## lead to supply chain attacks where malicious actors could
## replace model files and use an existing tag or branch name
## to serve malicious content.
##
## The secure approach is to:
##
## 1. Pin to specific revisions/commits when downloading models, files or datasets.
##
## Common unsafe patterns:
## - AutoModel.from_pretrained("org/model-name")
## - AutoModel.from_pretrained("org/model-name", revision="main")
## - AutoModel.from_pretrained("org/model-name", revision="v1.0.0")
## - load_dataset("org/dataset-name")
## - load_dataset("org/dataset-name", revision="main")
## - load_dataset("org/dataset-name", revision="v1.0")
## - AutoTokenizer.from_pretrained("org/model-name")
## - AutoTokenizer.from_pretrained("org/model-name", revision="main")
## - AutoTokenizer.from_pretrained("org/model-name", revision="v3.3.0")
## - hf_hub_download(repo_id="org/model_name", filename="file_name")
## - hf_hub_download(repo_id="org/model_name", filename="file_name", revision="main")
## - hf_hub_download(repo_id="org/model_name", filename="file_name", revision="v2.0.0")
## - snapshot_download(repo_id="org/model_name")
## - snapshot_download(repo_id="org/model_name", revision="main")
## - snapshot_download(repo_id="org/model_name", revision="refs/pr/1")
################################################################################

import string


def getChecks():
    """
    Public method to get a dictionary with checks handled by this module.

    @return dictionary containing checker lists containing checker function and
        list of codes
    @rtype dict
    """
    return {
        "Call": [
            (checkHuggingfaceUnsafeDownload, ("S-615",)),
        ],
    }


def checkHuggingfaceUnsafeDownload(reportError, context, _config):
    """
    Function to check for unsafe artifact download from Hugging Face Hub
    without immutable/reproducible revision pinning.

    @param reportError function to be used to report errors
    @type func
    @param context security context object
    @type SecurityContext
    @param _config dictionary with configuration data (unused)
    @type dict
    """
    # Check if any HuggingFace-related modules are imported
    hfModules = [
        "transformers",
        "datasets",
        "huggingface_hub",
    ]

    # Check if any HF modules are imported
    hfImported = any(context.isModuleImportedLike(module) for module in hfModules)

    if not hfImported:
        return

    qualname = context.callFunctionNameQual
    if not isinstance(qualname, str):
        return

    unsafePatterns = {
        # transformers library patterns
        "from_pretrained": ["transformers"],
        # datasets library patterns
        "load_dataset": ["datasets"],
        # huggingface_hub patterns
        "hf_hub_download": ["huggingface_hub"],
        "snapshot_download": ["huggingface_hub"],
        "repository_id": ["huggingface_hub"],
    }

    qualnameParts = qualname.split(".")
    funcName = qualnameParts[-1]

    if funcName not in unsafePatterns:
        return

    requiredModules = unsafePatterns[funcName]
    if not any(module in qualnameParts for module in requiredModules):
        return

    # Check for revision parameter (the key security control)
    revisionValue = context.getCallArgValue("revision")
    commitIdValue = context.getCallArgValue("commit_id")

    # Check if a revision or commit_id is specified
    revisionToCheck = revisionValue or commitIdValue

    if revisionToCheck is not None and isinstance(revisionToCheck, str):
        # Check if it's a secure revision (looks like a commit hash)
        # Commit hashes: 40 chars (full SHA) or 7+ chars (short SHA)

        revisionStr = str(revisionToCheck).strip("\"'")  # Remove quotes if present

        # Check if it looks like a commit hash (hexadecimal string)
        # Must be at least 7 characters and all hexadecimal
        isHex = all(c in string.hexdigits for c in revisionStr)
        if len(revisionStr) >= 7 and isHex:
            # This looks like a commit hash, which is secure
            return

    # Edge case: check if this is a local path (starts with ./ or /)
    firstArg = context.getCallArgAtPosition(0)
    if (
        firstArg
        and isinstance(firstArg, str)
        and firstArg.startswith(("./", "/", "../"))
    ):
        # Local paths are generally safer
        return

    if revisionValue:
        lineno = context.getLinenoForCallArg("revision")
        colOffset = context.getOffsetForCallArg("revision")
    elif commitIdValue:
        lineno = context.getLinenoForCallArg("commit_id")
        colOffset = context.getOffsetForCallArg("commit_id")
    else:
        lineno = context.node.lineno
        colOffset = context.node.col_offset

    reportError(
        lineno - 1,
        colOffset,
        "S-615",
        "M",
        "H",
        funcName,
    )
