#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : debug

"""
This function will give and create the debug folder for a given python file.
"""



# %% Libraries
from corelp import folder
from pathlib import Path
import os




# %% Function
def debug(file, new=True) :
    '''
    This function will give and create the debug folder for a given python file.
    
    Parameters
    ----------
    file : str
        __file__ string in the current python file to be debugged.
    new : bool
        True to create new folder at each call.

    Returns
    -------
    debug_folder : Path
        Path to the debug folder.

    Examples
    --------
    >>> from corelp import debug
    ...
    >>> debug_folder = debug(__file__)
    '''

    # Get paths
    file = Path(file)
    module_name = file.stem.replace("test_", "")
    lib_name = file.parents[2].name
    debug_parent = Path.home() / 'pythonLP/.debug'
    debug_folder = debug_parent / f'{lib_name}_{module_name}'

    # Create folders
    if not debug_parent.exists() : # Create parent folder if does not exist yet
        os.makedirs(debug_parent)
    return folder(debug_folder, False, new=new)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)