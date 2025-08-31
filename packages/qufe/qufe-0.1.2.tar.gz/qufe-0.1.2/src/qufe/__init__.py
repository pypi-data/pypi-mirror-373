"""
qufe - A comprehensive Python utility library

A collection of utilities for data processing, file handling, database management, 
automation tasks, and more.
"""

__version__ = "0.1.2"
__author__ = "Bongtae Jeon"
__email__ = "bongtae.jeon@gmail.com"

# Import main classes and functions for easy access
from . import base
from . import dbhandler
from . import excludebracket
from . import filehandler
from . import interactionhandler
from . import pdhandler
from . import texthandler
from . import wbhandler

# Commonly used classes and functions
from .base import TS, diff_codes, import_script, flatten, flatten_gen
from .filehandler import FileHandler, PathFinder
from .dbhandler import PostGreSQLHandler
from .texthandler import print_dict, print_in_columns, list_to_doku_wiki_table
from .excludebracket import eb2, check_eb

__all__ = [
    # Modules
    'base',
    'dbhandler', 
    'excludebracket',
    'filehandler',
    'interactionhandler',
    'pdhandler',
    'texthandler',
    'wbhandler',
    
    # Classes
    'TS',
    'FileHandler',
    'PathFinder', 
    'PostGreSQLHandler',
    
    # Functions
    'diff_codes',
    'import_script',
    'flatten',
    'flatten_gen',
    'print_dict',
    'print_in_columns',
    'list_to_doku_wiki_table',
    'eb2',
    'check_eb',
]