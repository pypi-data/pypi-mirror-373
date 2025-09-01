#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : print

"""
This file allows to test print

print : This function overrides python built in print function to add functionnalities.
"""



# %% Libraries
from corelp import print, debug
import pytest
from time import sleep
debug_folder = debug(__file__)


# %% test prints
def test_print() :
    '''
    Test print
    '''
    string = "# TEST\nHello *world*!\n\nThis is 1 print **example**"
    print(string, style="magenta")
    print.print(string, style="magenta")
    print.log(string, style="magenta")
    print.pyprint(string)
    print.richprint(string)



# %% test verbose
def test_verbose() :
    '''
    Test verbose
    '''
    print.verbose = False # Muting
    print("Should not print") # Does not print
    print("Should print", verbose=True) # Does print
    print("Should not print") # Does not print
    print.verbose = True # Unmuting
    print("Should print") # Does print
    print("Should not print", verbose=False) # Does not print
    print("Should print") # Does print



# %% test logging
def test_logging() :
    '''
    Test logging
    '''
    print.theme = {"success" : "green"}
    string = "# TEST\nHello *world*!\n\nThis is 1 print **example**"
    print(string, style="success")
    print.print_locals()
    try :
        1/0
    except Exception :
        print.error()
    file = debug_folder / "log.html"
    print.export_html(file)



# %% test console
def test_console() :
    '''
    Test console
    '''
    file = debug_folder / 'log.md'
    print.file = file
    string = "# TEST\nHello *world*!\n\nThis is 1 print **example**"
    print(string, style="magenta")
    assert file.exists()



# %% test clock
def test_clock() :
    '''
    Test clock
    '''
    for i in print.clock(5, "Outer loop") :
        print("Should not print")
        for j in print.clock(5, "Inner loop") :
            sleep(1)
            print("Should not print")
    
    for i in print.clock(10, "Other loop") :
        sleep(1)
        print("Should not print")






# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)