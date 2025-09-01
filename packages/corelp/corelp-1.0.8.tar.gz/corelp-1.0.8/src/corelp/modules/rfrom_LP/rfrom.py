#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-29
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : rfrom

"""
This function allows to do a relative import that works in module and script modes.
"""



# %% Libraries
import importlib
import sys


# %% Function
def rfrom(module, *functions) :
    '''
    This function allows to do a relative import that works in module and script modes.
    
    Parameters
    ----------
    module : str
        Name of relative module (with the point).
    functions : str
        Names of objects to import from module.

    Returns
    -------
    imported : object
        objects imported.

    Examples
    --------
    >>> from corelp import rfrom
    ...
    >>> func = rfrom(".module", "func")
    >>> func1, func2 = rfrom(".module", "func1", "func2")
    '''

    caller_globals = sys._getframe(1).f_globals
    package = caller_globals.get("__package__")

    mod = None
    if module.startswith(".") and package:
        # Only attempt relative import if inside a package
        try:
            mod = importlib.import_module(module, package)
        except ImportError:
            pass

    if mod is None:
        # fallback to absolute import (strip leading dots)
        mod = importlib.import_module(module.lstrip("."))

    # If no functions asked, returns module
    if len(functions) == 0 :
        return mod

    imported = tuple(getattr(mod, f) for f in functions)
    return imported[0] if len(imported) == 1 else imported



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)