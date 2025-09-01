#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-28
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : Section

"""
This file allows to test Section

Section : This class defines decorator instances allowing to create section functions.
"""



# %% Libraries
from corelp import debug, Section
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test Section function
    '''
    section = Section(path=debug_folder)

    @section()
    def add(a, b=0) :
        return a+b
    assert add(3) == 3
    assert add(3, 0) == 3
    assert add(1, 3) == 4
    assert add(1, b=3) == 4



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)