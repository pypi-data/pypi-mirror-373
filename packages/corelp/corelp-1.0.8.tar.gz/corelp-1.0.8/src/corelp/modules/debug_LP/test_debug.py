#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : debug

"""
This file allows to test debug

debug : This function will give and create the debug folder for a given python file.
"""



# %% Libraries
from corelp import debug
from pathlib import Path
debug_folder = debug(__file__)



# %% Test folder exists
def test_path() :
    assert debug_folder.exists(), "Debug folder should exist"
    assert debug_folder == (Path.home() / 'pythonLP/.debug/corelp_debug')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)