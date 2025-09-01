"""
File Handling Abstraction Module
================================

This module provides a unified abstraction layer for working with various
file formats. It defines a common `File` base class and multiple subclasses
for specific formats, enabling a consistent interface for reading, writing,
appending, copying, moving, and deleting files.

Supported File Types
--------------------
- TxtFile   : Plain text files (.txt)
- JsonFile  : JSON files (.json)
- CsvFile   : CSV files (.csv)
- DillFile  : Python objects serialized with dill (.dill)
- XmlFile   : XML files (.xml)
- YamlFile  : YAML files (.yml, .yaml)
- ByteFile  : Binary files (.bin, .exe, .img, .jpg)
- VarDBFile : Custom VariableDB database files (.db)

Factory Function
----------------
The `file()` function acts as a factory to automatically return the
appropriate subclass instance based on the file extension.

Examples
--------
Create and use a text file:
    f = file("notes.txt")
    f.write("Hello")
    content = f.read()
    print(content)   # -> Hello

Work with JSON:
    f = file("data.json")
    f.write({"a": 1})
    data = f.read()
    print(data)      # -> {"a": 1}

Append data to a database:
    f = file("config.db", scope={"x": 1}, data={"a": 10})
    f.append({"b": 20})
    db_data = f.read()
    print(db_data)   # -> {"a": 10, "b": 20}

Notes
-----
- All file classes ensure the file and its parent directory are created if they
  do not exist.
- Subclasses override `read`, `write`, and `append` with format-specific logic.
- The base `File` class also provides utilities for `exist`, `copy`, `move`,
  and `delete`.
"""

from .core import (
    File,
    TxtFile,
    JsonFile,
    CsvFile,
    DillFile,
    XmlFile,
    YamlFile,
    ByteFile,
    VarDBFile,
    file
)

__all__ = [
    "File",
    "TxtFile",
    "JsonFile",
    "CsvFile",
    "DillFile",
    "XmlFile",
    "YamlFile",
    "ByteFile",
    "VarDBFile",
    "file"
]