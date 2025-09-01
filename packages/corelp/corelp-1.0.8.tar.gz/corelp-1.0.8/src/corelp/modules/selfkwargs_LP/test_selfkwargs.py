#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : selfkwargs

"""
This file allows to test selfkwargs

selfkwargs : This function takes a dictionnary and sets all its values to an object (self).
"""



# %% Libraries
from corelp import debug, selfkwargs
import pytest
debug_folder = debug(__file__)



# %% Function test
def test_function() :
    '''
    Test selfkwargs
    '''
    class MyClass() :
        def __init__(self, **kwargs) :
            selfkwargs(self, kwargs)
    instance = MyClass(a="a", b="b")
    assert instance.a == "a"
    assert instance.b == "b"



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)