#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : getmodule

"""
This function is to be used in a library __init__ file. It creates lazy imports of the module imported and defines __getattr__ and __all__ for this library.
"""



# %% Libraries
from pathlib import Path
import json
import importlib



# %% Function
def getmodule(file) :
    '''
    This function is to be used in a library __init__ file. It creates lazy imports of the module imported and defines __getattr__ and __all__ for this library.
    
    Parameters
    ----------
    file : str
        __file__ string in the __init__.py file.

    Returns
    -------
    _getattr : function
        Function to replace __getattr__ variable.
    _all : list
        list of module names corresponding to __all__.

    Raises
    ------
    AttributeError
        When trying to import a module which is not in the library.

    Examples
    --------
    >>> from corelp import getmodule
    ...
    >>> # In __init__.py file
    ... __getattr__, __all__ = getmodule(__file__)
    '''

    # Get paths
    file = Path(file)
    libfolder = file.parent
    name = libfolder.name
    modulesjson = libfolder / 'modules.json'
    scriptsjson = libfolder / 'scripts.json'

    # Get dicts
    with open(modulesjson, "r") as file :
        modules = json.load(file)
    with open(scriptsjson, "r") as file :
        scripts = json.load(file)

    # Objects to return
    _lazy = {}
    _all = [module for module in modules] + [script for script in scripts]
    def _getattr(attr) :
        
        # Cached
        if attr in _lazy:
            return _lazy[attr]

        try :
            module = modules.get(attr, None)
            funcstring = "module"
            if module is None :
                module = scripts.get(attr, None)
                funcstring = "script"
            if module is None :
                raise KeyError(f"{attr} was not found in json files")
        except KeyError:
            raise AttributeError(f'module {name} has no attribute {attr}')
        path2module = module[funcstring].replace('/', '.')
        obj_name = module["object"]

        mod = importlib.import_module(f"{name}.{path2module}")
        obj = getattr(mod, obj_name, None)
        if obj is None :
            raise AttributeError(f"module {name}.{path2module} has no attribute {obj_name}")
        _lazy[attr] = obj  # Cache it
        return obj

    return _getattr, _all



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)