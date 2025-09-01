#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-25
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : folder

"""
This function creates a new folder, while crushing previous instances if already exists.
"""



# %% Libraries
from pathlib import Path
import shutil
import os



# %% Function
def folder(path, /, warning=True, *, new=True) :
    '''
    This function creates a new folder, while crushing previous instances if already exists.
    
    Parameters
    ----------
    path : str or Path
        Full path to folder to create.
    warning : bool
        True to print a warning if a folder already exist.
    new : bool
        True to crush folder if already exists.

    Returns
    -------
    folder_path : Path
        Path object to created folder.

    Raises
    ------
    SyntaxError
        If user answers *no* to crush existing folder when warning asked.

    Examples
    --------
    >>> from corelp import folder
    ...
    >>> folder_path = folder(path) # Creates folder
    >>> folder_path = folder(path) # Launch warning before crushing
    >>> folder_path = folder(path, warning=False) # Crushes without warning
    >>> folder_path = folder(path, new=False) # Does not crush old folder
    '''

    path = Path(path)

    # Folder already exists
    if path.exists() :
        if not new : # Nothing to do
            return path
        
        # Decide if crushing
        if warning :
            print('\n**********************')
            print("FOLDER WILL BE DELETED")
            print(str(path))
            erase = input('Continue? [y]/n >>> ')
            crush = str(erase).lower() in ["yes", "y", "true", "1"]
        else :
            crush = True
        
        # Error
        if not crush :
            raise SyntaxError(f"Folder {path} already exists and cannot be crushed")
        
        # Removes folder
        def remove_protection(func, directory, info):
            if os.name == "nt":
                os.system(f'attrib -h -s -r "{directory}"')
                if os.path.isdir(directory):
                    shutil.rmtree(directory, onexc=remove_protection)
                else:
                    os.remove(directory)
        shutil.rmtree(path, onexc=remove_protection)
    
    # End
    os.makedirs(path)
    return path



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)