
# AviTwilTools

**Unified Python Package for Folder and File Management**

AT_tools is a Python package designed to simplify filesystem management. It provides a unified interface to work with folders and multiple file types, offering robust features for creating, reading, writing, moving, copying, and deleting files and folders.

**Author:** Avi Twil
**GitHub:** [https://github.com/avitwil/AT\_tools](https://github.com/avitwil/AT_tools)

---

## Features

### Folder Management (`AviTwilTools.folder`)

* Create and manage nested folders with automatic hierarchy tracking.
* Add, remove, move, or copy folders safely.
* Recursively delete folders and all contents.
* Print folder tree structures for visualization.
* Automatically register all subfolders in the internal mapping.

### File Management (`AviTwilTools.file`)

* Unified interface for multiple file formats:

  * `TxtFile` – Plain text (.txt)
  * `JsonFile` – JSON (.json)
  * `CsvFile` – CSV (.csv)
  * `DillFile` – Python serialized objects (.dill)
  * `XmlFile` – XML files (.xml)
  * `YamlFile` – YAML files (.yml, .yaml)
  * `ByteFile` – Binary files (.bin, .exe, .img, .jpg)
  * `VarDBFile` – Custom VariableDB files (.db)
* Factory function `file()` automatically returns the correct file type instance based on the file extension.
* Supports `read()`, `write()`, `append()`, `copy()`, `move()`, and `delete()`.

---

## Installation

Install directly from PyPI:

```bash
pip install AviTwilTools
```

---

## Quick Start

### Folder Example

```python
from AviTwilTools import Folder

# Create or access a folder
root = Folder("data")

# Create nested folders automatically
sub = Folder("data/names/avi")

# Add folder manually
root.add(sub)

# Print folder structure
root.print_tree()

# List contents
print(root.list_dir())
```

### File Example

```python
from AviTwilTools import file

# Text file
txt = file("data/names/avi/info.txt")
txt.write("Hello Avi!")
print(txt.read())  # -> Hello Avi!

# JSON file
json_file = file("data/config.json")
json_file.write({"key": "value"})
data = json_file.read()
print(data)  # -> {"key": "value"}

# Database append
db_file = file("data/config.db", scope={"x": 1}, data={"a": 10})
db_file.append({"b": 20})
print(db_file.read())  # -> {"a": 10, "b": 20}
```

### Folder + File Example

```python
from AviTwilTools import Folder, file

# Create folder
root = Folder("projects")
root._map_folder()  # Automatically map all subfolders

# Create a file inside the folder
f = file("projects/demo/readme.txt")
f.write("This is a demo file.")
print(f.read())  # -> This is a demo file.
```

---

## Documentation

* Folder Management: `Folder` class
* File Management: `file()` factory and all file subclasses (`TxtFile`, `JsonFile`, etc.)

For full API reference, see the source code in [`AT_tools`](https://github.com/avitwil/AT_tools).

---

## Notes

* All file classes ensure the file and parent directories exist.
* Folder operations are hierarchical and automatically track child folders.
* Designed for Python 3.10+.

---

## License

MIT License


