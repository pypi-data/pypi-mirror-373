"""
ATfolder_handler Package
------------------------

This package provides utilities for managing filesystem folders with
automatic hierarchy tracking, recursive mapping, and helper methods
for copying, moving, and deleting directories.

Modules:
- core: Contains the Folder class with all folder-related operations.
"""

from .core import Folder

__all__ = ["Folder"]
