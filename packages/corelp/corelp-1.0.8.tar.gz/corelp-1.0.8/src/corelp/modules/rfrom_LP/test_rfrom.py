#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-29
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : rfrom

"""
This file allows to test rfrom

rfrom : This function allows to do a relative import that works in module and script modes.
"""



# %% Libraries
from corelp import print, debug
import pytest
from corelp import rfrom
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test rfrom function
    '''
    print('Hello world!')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)