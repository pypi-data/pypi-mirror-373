# -*- coding: utf-8 -*-

# Copyright (c) 2011 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module to check for the presence of PySide by importing it.
"""

import importlib.util
import sys

if __name__ == "__main__":
    pySideVariant = "6"
    if len(sys.argv) == 2:
        pySideVariant = sys.argv[1].replace("--variant=", "")

    if pySideVariant in ("1", "2"):
        # no PySide support anymore
        ret = 10

    elif pySideVariant == "6":
        ret = 10 if importlib.util.find_spec("PySide6") is None else 0

    else:
        ret = 10

    sys.exit(ret)
