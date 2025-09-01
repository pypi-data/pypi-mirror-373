#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : selfkwargs

"""
This function takes a dictionnary and sets all its values to an object (self).
"""



# %% Function
def selfkwargs(self, kwargs) :
    '''
    This function takes a dictionnary (kwargs) and sets all its values to an object (self).
    
    Parameters
    ----------
    self : object
        Object instance where to set attributes.
    kwargs : object
        Dictionnary defining which attributes to set and its values.

    Examples
    --------
    >>> from corelp import selfkwargs
    ...
    >>> # Typicall use is in __init__ function :
    >>> class MyClass :
    ...     def __init__(self, **kwargs) :
    ...         selkwargs(self, kwargs) # Sets all the keyword arguments to self
    ...
    >>> instance = MyClass(a=1, b=2)
    >>> print(instance.a)
    1
    >>> print(instance.b)
    2
    '''

    for key, value in kwargs.items() :
        setattr(self, key, value)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)