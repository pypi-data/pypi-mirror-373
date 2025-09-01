"""
AviTwilTools
============

A Python utility library that provides a **unified API for handling multiple file formats**
and an **in-memory folder graph** that mirrors your filesystem.

Author: Avi Twil
GitHub: https://github.com/avitwil/AT_tools
PyPI:   https://pypi.org/project/AviTwilTools/

Main Features
-------------
- Unified File API for reading, writing, appending, copying, moving, and deleting.
- Supported formats:
    * TxtFile   → .txt
    * JsonFile  → .json
    * CsvFile   → .csv
    * YamlFile  → .yml / .yaml
    * XmlFile   → .xml
    * ByteFile  → .bin / .img / .exe / .jpg
    * DillFile  → .dill
    * VarDBFile → .db  (default scope = globals())
- Folder class for managing directories in memory:
    * Tracks subfolders and files.
    * Attribute-style navigation (folder.subfolder).
    * Dictionary-style access (folder["file.txt"]).
    * Utilities: print_tree(), list_dir(), recursive_delete(), move(), copy().

Version: 1.0.5
"""

__version__ = "1.0.5"
__author__ = "Avi Twil"
__all__ = [
    "File",
    "TxtFile",
    "JsonFile",
    "CsvFile",
    "YamlFile",
    "XmlFile",
    "ByteFile",
    "DillFile",
    "VarDBFile",
    "Folder",
    "file"
]

# Import core classes into package namespace
from .core import (
    File,
    TxtFile,
    JsonFile,
    CsvFile,
    YamlFile,
    XmlFile,
    ByteFile,
    DillFile,
    VarDBFile,
    Folder,
    file
)
