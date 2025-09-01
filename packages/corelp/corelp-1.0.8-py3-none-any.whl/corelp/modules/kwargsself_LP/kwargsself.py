#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : kwargsself

"""
This function will return all the attributes of an object (self) into a dictionnary (kwargs)
"""



# %% Function
def kwargsself(self) :
    '''
    This function will return all the attributes of an object (self) into a dictionnary (kwargs)
    
    Parameters
    ----------
    self : object
        Object instance where to retrieve attributs.

    Returns
    -------
    kwargs : dict
        Dictionnary containing all the attributes and values.

    Raises
    ------
    TypeError
        If instance has not __dict__ nore __slots__ attributes.

    Examples
    --------
    >>> from corelp import selfkwargs, kwargsself
    ...
    >>> # Typicall use is to store instance's state :
    >>> class MyClass :
    ...     def __init__(self, **kwargs) :
    ...         selkwargs(self, kwargs) # Sets all the keyword arguments to self
    ...
    >>> instance = MyClass(a=1, b=2)
    >>> print(instance.a)
    1
    >>> print(instance.b)
    2
    ...
    >>> # Store state
    >>> kwargs = kwargsself(instance)
    >>> print(kwargs)
    {"a": 1, "b": 2}
    ...
    >>> # Change state
    >>> instance.a = 0
    >>> print(instance.a)
    0
    ...
    >>> # Restore state
    >>> selfkwargs(instance, kwargs)
    >>> print(instance.a)
    1
    '''

    if hasattr(self, "__dict__") :
        return {key: value for key, value in self.__dict__.items()}

    elif hasattr(self, "__slots__") :
        return {key : getattr(self, key) for key in self.__slots__}

    else :
        raise TypeError('Object has not __dict__ nore __slots__')



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)