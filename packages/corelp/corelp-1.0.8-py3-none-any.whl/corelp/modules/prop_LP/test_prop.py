#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : prop

"""
This file allows to test prop

prop : This function serves as an improved property decorator.
"""



# %% Libraries
from corelp import debug, prop
import pytest
debug_folder = debug(__file__)



# %% testclass
class MyClass :
    # Set default value
    @prop()
    def defaultattr(self) :
        return "MyDefaultValue" # --> is overriden if "_defaultattr" exists
    
    # Set initialization value
    @prop(cache=True)
    def cachedattr(self) :
        return "MyCachedValue" # --> called once and cached in "_cachedattr"
    


class MyTwin :
    def __init__(self, twin) :
        self.mytwin = twin

    # Links on attribute name
    @prop(link="mytwin") # --> links to self.mytwin
    def attrlink(self) :
        return "defaultattr" # --> calls the "defaultattr" attribute of the linked object



# %% Instance fixture
@pytest.fixture()
def instance() :
    '''
    Create a new instance at each test function
    '''

    instance = MyClass()
    return instance, MyTwin(instance)



# %% Default values test
def test_default(instance) :
    '''
    Test default values
    '''
    person, twin = instance
    assert person.defaultattr == "MyDefaultValue"
    person.defaultattr = "NotMyDefaultValue"
    assert person.defaultattr == "NotMyDefaultValue"
    assert person._defaultattr == "NotMyDefaultValue"



# %% Default values cached
def test_cached(instance) :
    '''
    Test default values
    '''
    person, twin = instance
    assert getattr(person, "_cachedattr", None) is None
    assert person.cachedattr == "MyCachedValue"
    assert person._cachedattr == "MyCachedValue"
    assert person.cachedattr == "MyCachedValue"



# %% Link values test
def test_link(instance) :
    '''
    Test link values
    '''
    person, twin = instance
    assert person.defaultattr == "MyDefaultValue"
    assert twin.attrlink == "MyDefaultValue"
    twin.attrlink = "MyLinkedValue"
    assert person.defaultattr == "MyLinkedValue"
    assert twin.attrlink == "MyLinkedValue"



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)