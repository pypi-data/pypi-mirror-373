#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : prop

"""
This function serves as an improved property decorator.
"""



# %% Function
def prop(*, cache=False, link=None) :
    '''
    This function serves as an improved property decorator.
    By default, calls the function as a normal property.
    However if the readonly attribute of same name (starting with "_") exists and is not None, it returns this value.
    This function can also be used to link the property to another object attribute, then the return value should be this linked name.
    
    Parameters
    ----------
    cache : bool
        True to set readonly attribute at first call.
    link : bool
        True to link property to another object attribute.

    Returns
    -------
    decorator : property
        This is the decorator to apply.

    Examples
    --------
    >>> from corelp import prop
    ...
    >>> class MyClass :
    ...
    ...     # Set default value
    ...     @prop()
    ...     def defaultattr(self) :
    ...         return "MyDefaultValue" # --> is overriden if "_defaultattr" exists
    ...
    ...     # Set initialization value
    ...     @prop(cache=True)
    ...     def cachedattr(self) :
    ...         return "MyCachedValue" # --> called once and cached in "_cachedattr"
    ...
    ...
    ...
    >>> instance = MyClass() # Creates instance of MyClass
    >>> class MyTwin :
    ...
    ...     # The following properties do the same thing
    ...
    ...     mytwin = instance
    ...     # Links on attribute name
    ...     @prop(link="mytwin") # --> links to self.mytwin
    ...     def attrlink(self) :
    ...         return "defaultattr" # --> calls the "defaultattr" attribute of the linked object
    ...
    ...     # Links on object
    ...     @prop(link=instance) # --> links to an object
    ...     def objectlink(self) :
    ...         return "defaultattr" # --> calls the "defaultattr" attribute of the linked object
    '''
    
    if link is not None :
        return linkproperty(link)
    return defaultproperty(cache)



def defaultproperty(cache):
    def decorator(func) :
        attribut = func.__name__

        def getter(self):
            _attribut = getattr(self, f'_{attribut}',None)
            if _attribut is not None :
                return _attribut
            result = func(self)
            if cache :
                setattr(self, f'_{attribut}', result)
            return result

        def setter(self, value):
            setattr(self, f'_{attribut}', value)

        def deleter(self):
            setattr(self, f'_{attribut}', None)

        prop = property(getter, setter, deleter)

        return prop
    return decorator



def linkproperty(link):
    def decorator(func) :

        def getter(self):
            obj = getattr(self, link) if isinstance(link, str) else link
            attribut = func(self)
            return getattr(obj, f'{attribut}')

        def setter(self, value):
            obj = getattr(self, link) if isinstance(link, str) else link
            attribut = func(self)
            setattr(obj, f'{attribut}', value)

        prop = property(getter, setter)

        return prop
    return decorator



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)