#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-28
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : main

"""
This file allows to test main

main : This function can decorate the main function of a script.
"""



# %% Libraries
from corelp import print, debug, main
from time import sleep
import pytest
debug_folder = debug(__file__)



# %% User inputs
search = False # True to apply manual search
global import_path
global export_path
import_path = None if search else debug_folder # Path to the imported data
export_path = import_path # Path to the exported data
new = False # True to create new result folder at each run
bulk = None # function(import_path) that returns a dictionnary of {import_subfolder:export_subfolder} for multiple decorated function run.
overnight= False # If True and exception occurs, will skip and pass to the next run in bulk processing.
myparam = "Hello from main!"
apply_error = False



@main()
def mainfunc() :
    if apply_error :
        1/0
    print(myparam)
    result = section_1()
    print(f"import_path = {import_path}")
    return result

@mainfunc.section()
def section_1() :
    print('> Hello from section!')
    return True



# %% Function test
def test_function() :
    '''
    Test main function
    '''
    mainfunc()
    sleep(2) # Ensure new folder
    mainfunc(myparam="Hello changed!!")
    sleep(2) # Ensure new folder
    mainfunc(new=True)
    sleep(2) # Ensure new folder
    with pytest.raises(ZeroDivisionError, match="division by zero") :
        mainfunc(apply_error=True)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)