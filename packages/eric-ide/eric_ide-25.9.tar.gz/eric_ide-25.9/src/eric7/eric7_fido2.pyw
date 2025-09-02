# -*- coding: utf-8 -*-

# Copyright (c) 2024 - 2025 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing the Windows entry point.
"""

if __name__ == "__main__":
    from command_runner.elevate import elevate
    from eric7_fido2 import main

    elevate(main)
