#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : kwargsself

"""
This file allows to test kwargsself

kwargsself : This function will return all the attributes of an object (self) into a dictionnary (kwargs)
"""



# %% Libraries
from corelp import debug, kwargsself, selfkwargs
from dataclasses import dataclass, field
import pytest
debug_folder = debug(__file__)



# %% Class test
def test_class() :
    '''
    Test kwargsself on classes
    '''
    class MyClass :
        def __init__(self, **kwargs) :
            selfkwargs(self, kwargs)
    dic = {"a":"a", "b":"b"}
    instance = MyClass(**dic)
    kwargs = kwargsself(instance)
    assert kwargs == dic



# %% Dataclass test
def test_dataclass() :
    '''
    Test kwargsself on dataclasses
    '''
    @dataclass(slots=True, kw_only=True)
    class MyDataClass :
        a: str = "a"
        b : str = "b"
    dic = {"a":"a", "b":"b"}
    instance = MyDataClass()
    kwargs = kwargsself(instance)
    assert kwargs == dic



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)