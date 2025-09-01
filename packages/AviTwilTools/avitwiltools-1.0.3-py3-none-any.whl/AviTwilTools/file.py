"""
File Management Submodule
=========================

Provides unified file abstractions and the file() factory function.
Includes support for various file types: Txt, Json, Csv, Dill, Xml, Yaml, Byte, VarDB.
"""

from .ATmulti_file_handler import (
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
