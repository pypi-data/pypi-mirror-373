#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : folder

"""
This file allows to test folder

folder : This function creates a new folder, while crushing previous instances if already exists.
"""



# %% Libraries
from corelp import debug, folder
import pytest
debug_folder = debug(__file__)



# %% Test function
def test_function() :
    path = debug_folder / 'test_folder'
    subpath = path / "test_subfolder"
    folder(subpath, False)
    assert path.exists()
    assert subpath.exists()
    folder(path, False, new=False)
    assert path.exists()
    assert subpath.exists()
    folder(path, False, new=True)
    assert path.exists()
    assert not subpath.exists()



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)