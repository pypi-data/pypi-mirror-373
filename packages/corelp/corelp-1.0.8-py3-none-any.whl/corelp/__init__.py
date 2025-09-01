#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP

"""
A library that gathers core functions for python programming.
"""



from pathlib import Path

# %% Lazy imports
if __name__ == "__main__":
    from modules.getmodule_LP.getmodule import getmodule # type: ignore
else :
    from .modules.getmodule_LP.getmodule import getmodule
__getattr__, __all__ = getmodule(__file__)
icon = Path(__file__).parent / "icon_pythonLP.ico"



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)