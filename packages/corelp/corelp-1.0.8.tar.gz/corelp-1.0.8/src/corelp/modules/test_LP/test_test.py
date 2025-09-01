#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : template_moduledate
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : test

"""
This file allows to test test

test : This function will launch the testfile for the current file using pytest library.
"""



# %% Libraries
from corelp import debug
import pytest
debug_folder = debug(__file__)



# %% Test function
def test_function() :
    print('Hello world!')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)