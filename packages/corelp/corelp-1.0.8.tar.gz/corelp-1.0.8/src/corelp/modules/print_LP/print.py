#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-08-27
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : coreLP
# Module        : print

"""
This function overrides python built in print function to add functionnalities.
"""



# %% Libraries



# %% Libraries
from corelp import prop
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from rich import print as richprint
from rich.console import Console
from rich.theme import Theme
from rich.markdown import Markdown
from rich.traceback import Traceback
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    ProgressColumn,
)
import traceback as tb_module
from time import perf_counter
from pathlib import Path
pyprint = print



# %% Class
@dataclass(slots=True, kw_only=True)
class Print() :
    '''
    This function overrides python built in print function to add functionnalities.

    Call
    ----
    string : object
        will take the __str__() of the object and print it.
    verbose : bool
        True to do print, False will just immediately return None.
    return_string : bool
        True to return the string after transformation, False for default behavior None.
    file : str or Path or None
        Override the file attribute (see below) if not None.
    mode : str
        defines the mode to write in file (most common are "w" for write and "a" for append).
    end : str
        defines the mode how the string ends, default is "\\n".
    **kwargs :
        all other key-word attributes will be passed to the console print.
    >>> from corelp import print
    >>> mystring = "Hello *world*!\\nThis is 1 print **example**"
    ...
    >>> print(mystring)

    Muting
    ------
    verbose : bool
        True to do prints, False to mute all prints
    
    >>> print.verbose = False # Muting
    >>> print(mystring) # Does not print
    >>> print(mystring, verbose=True) # Forces printing even with muting
    >>> print(mystring) # Does not print
    ...
    >>> print.verbose = True # Unmuting
    >>> print(mystring) # Does print
    >>> print(mystring, verbose=False) # Forces no printing even without muting
    >>> print(mystring) # Does print

    Prints
    ------
    pyprint : function
        python built-in print function (to still have access after override).
    richprint : function
        rich library print function.
    print : function
        rich library console print function (for enhancing styles).
    log : function
        rich library console log function (for debugging).

    >>> print.pyprint(mystring) # python print
    >>> print.richprint(mystring) # python print
    >>> print.print(mystring) # rich console print
    >>> print.log(mystring) # rich console log

    Logging
    -------
    file : Path
        Path to file.

    >>> print.file = "log.txt" # defining log file
    >>> print(mystring) # Also writes into file

    Console
    -------
    theme : dict
        Dictionnary containing the added styles.
    console : Console
        Rich library console object to use with printing mode "console".

    >>> print.theme = {"success" : "green"} # defining new kind of style
    >>> print(mystring, style="success") # Writes in green
    >>> try :
    ...     1/0
    ... except Exception :
    ...     print.error() # Prints pretty error
    >>> print.export_html("log.html") # Creates html with all the logs

    Clock
    -------
    progress : Progress
        Current Progress object from rich library.
    bars : dict
        Stores the current bars existing in progress object.

    >>> from time import sleep
    >>> for i in print.clock(15, "Outer loop") : # First argument is iterable, if int --> range(int)
    ...     for j in print.clock(10, "Inner loop") 
    ...         sleep(1.)
    '''

    # Main function
    def __call__(self, string, verbose=None, *, return_string=False, file=None, mode='a', end='\n', **kwargs) :
        # Muting
        verbose = verbose if verbose is not None else self.verbose
        if not verbose :
            return None
        
        # Printing markdown
        string = str(string) + end
        self.print(Markdown(string), **kwargs)

        # Writting to file
        file = file if file is not None else self.file
        if file is not None :
            with open(Path(file), mode) as file :
                file.write(string)

        # Return
        if return_string :
            return string


    # MUTING
    verbose : bool = True # True to print



    # PRINT

    @property
    def print(self) :
        return self.console.print
    @property
    def log(self) :
        return self.console.log
    pyprint = pyprint # python print
    richprint = richprint # rich print



    # LOGGING

    _file : Path = None
    @property
    def file(self) :
        return self._file
    @file.setter
    def file(self, value) :
        self._file = Path(value)



    # CONSOLE

    _theme = {}
    @property
    def theme(self) :
        return self._theme
    @theme.setter
    def theme(self, value) :
        self._theme.update(value)
        self._console = None

    _console : Console = field(default=None, repr=False)
    @prop(cache=True)
    def console(self) :
        theme = Theme(self.theme)
        return Console(theme=theme, record=True)

    def error(self) :
        rich_tb = Traceback.from_exception(*tb_module.sys.exc_info())
        self.console.print(rich_tb)
    
    def print_locals(self) :
        self.console.log(log_locals=True)
    
    def export_html(self, path) :
        if path is None :
            return
        path = Path(path)
        html_content = self.console.export_html(inline_styles=True)
        with open(path, "w", encoding="utf-8") as file:
            file.write(html_content)
    


    # CLOCK

    def clock(self, iterable, title="Working...") :

        # Get iterable
        iterable = range(iterable) if isinstance(iterable, int) else iterable
        iterable = list(iterable)

        # Detect if progressbar already exists
        first_bar = getattr(self, "_progress", None) is None
        progress = self.progress
        bars = self.bars
        
        # Opens progress
        if first_bar :
            verbose = self.verbose
            self.verbose = False

            # Write to file
            if self.file is not None :
                with open(Path(self.file), "a") as file :
                    file.write(f'{title}...\n')
            progress.start()
        
        # Create new task
        task = bars.get(title, None)
        if task is None : # No bar with this name exists
            task = progress.add_task(title, total=len(iterable), avg_time=0.0)
            bars[title] = task # store it
        else :
            progress.reset(task)
        
        # Loop
        loop_counter = 0
        start = perf_counter()
        for item in iterable :
            yield item
            loop_counter += 1
            elapsed = perf_counter() - start
            avg_time = elapsed / loop_counter if loop_counter else 0
            progress.update(task, advance=1, avg_time=avg_time)
        
        # Clean up
        if first_bar :
            progress.stop()
            del(self.bars)
            del(self.progress)
            self.verbose = verbose

    _progress : Progress = field(default=None, repr=False)
    @prop(cache=True)
    def progress(self) :
        return Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TextColumn("[magenta]/{task.total}[/]"),
        TimeElapsedColumn(),
        AvgLoopTimeColumn(),
        TimeRemainingColumn(),
        EndTimeColumn(),
        transient=False
        )
    
    _bars : dict = field(default=None, repr=False)
    @prop(cache=True)
    def bars(self) :
        return {}



# Get instance
print = Print() # Instance to use everywhere

# Custom Progress bar columns
class AvgLoopTimeColumn(ProgressColumn):
    def render(self, task):
        avg_time = task.fields.get("avg_time", None)
        if avg_time is not None and task.completed > 0:
            string = f"[yellow]↻ {avg_time:.2f}s[/]" if avg_time > 1 else f"[yellow]↻ {avg_time*1000:.2f}ms[/]"
            return string
        return ""
class EndTimeColumn(ProgressColumn):
    def render(self, task):
        if task.time_remaining is not None:
            end_time = datetime.now() + timedelta(seconds=task.time_remaining)
            return f"[cyan]{end_time:%m-%d %H:%M:%S}[/] "
        return ""



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)