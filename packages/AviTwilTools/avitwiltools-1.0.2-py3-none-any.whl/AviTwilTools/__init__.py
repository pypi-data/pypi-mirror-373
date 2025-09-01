"""
AviTwilTools Package
================

Unified package for folder and file management in Python.

Submodules:
------------
- AviTwilTools.folder : Folder management utilities
- AviTwilTools.file   : File management utilities

Usage:
------
from AviTwilTools.folder import Folder
from AviTwilTools.file import TxtFile, JsonFile, file
"""

# Import submodules
from .folder import *
from .file import *

__all__ = ["Folder", "File", "TxtFile", "JsonFile", "CsvFile", "DillFile",
           "XmlFile", "YamlFile", "ByteFile", "VarDBFile", "file"]
