
# AviTwilTools

**AviTwilTools** is a Python utility library that provides a **unified API for handling multiple file formats** and an **in-memory folder graph** that mirrors your filesystem.
It makes working with files and directories simple, consistent, and Pythonic.

**Author:** Avi Twil
**GitHub:** [avitwil/AT\_tools](https://github.com/avitwil/AT_tools)
**PyPI:** [AviTwilTools](https://pypi.org/project/AviTwilTools/)

---

## ✨ Features

* **Unified File API**
  All file types support:
  `read()`, `write(data)`, `append(data)`, `copy(dst)`, `move(dst)`, `delete()`, `exist()`

* **Supported file formats**

  * `TxtFile` → `.txt`
  * `JsonFile` → `.json`
  * `CsvFile` → `.csv`
  * `YamlFile` → `.yml`, `.yaml`
  * `XmlFile` → `.xml`
  * `ByteFile` → `.bin`, `.img`, `.exe`, `.jpg`
  * `DillFile` → `.dill`
  * `VarDBFile` → `.db` (**default scope = `globals()`**)

* **Folder abstraction**

  * Each `Folder` object represents a real directory.
  * Instances are cached (singleton-per-path).
  * Auto-creates directories if missing.
  * Navigate with attributes (`folder.sub`) or indexing (`folder["file.txt"]`).
  * Print tree structure with `print_tree()`.
  * Supports `copy()`, `move()`, `remove()`, `recursive_delete()`, etc.

* **Factory function**
  `file("name.ext")` returns the correct `File` subclass automatically.

---

## 📦 Installation

Install directly from PyPI:

```bash
pip install AviTwilTools
```

No extra dependencies required.

---

## ⚡ Quick Examples

### Text and JSON

```python
from AviTwilTools import TxtFile, JsonFile

# TXT
txt = TxtFile("hello.txt")
txt.write("Hello")
txt.append(" World")
print(txt.read())   # -> "Hello World"

# JSON
j = JsonFile("data.json")
j.write({"a": 1})
j.append({"b": 2})
print(j.read())     # -> {"a": 1, "b": 2}
```

---

### CSV, YAML, XML

```python
from AviTwilTools import CsvFile, YamlFile, XmlFile
import xml.etree.ElementTree as ET

# CSV
c = CsvFile("table.csv")
c.write([["id", "name"], [1, "Alice"]])
c.append([2, "Bob"])
print(c.read())

# YAML
y = YamlFile("config.yaml")
y.write({"debug": True})
y.append({"workers": 4})
print(y.read())

# XML
root = ET.Element("root")
x = XmlFile("doc.xml")
x.write(root)
x.append(ET.Element("child"))
print(x.read().tag)   # -> "root"
```

---

### Binary & Dill (Python objects)

```python
from AviTwilTools import ByteFile, DillFile

# Binary file
b = ByteFile("blob.bin")
b.write(b"\x00\xFF")
b.append(b"\x10")
print(len(b.read()))

# Dill (Python object serialization)
d = DillFile("obj.dill")
d.write({"k": [1, 2, 3]})
print(d.read())
```

---

### VarDBFile 

```python
from AviTwilTools import VarDBFile

x = 1
y = 2
db = VarDBFile("store.db",scope=globals())
db.write(x)
db.append(y)

print(db.read())   # -> {"x": 1, "y": 2}
print(x)           # x is injected into globals()
```



---

### Folder Navigation

```python
from AviTwilTools import Folder, TxtFile

root = Folder("project")
sub = Folder("project/folder1/folder2")

TxtFile("myfile.txt", sub).write("Nested Hello")

print(root.folder1.folder2["myfile.txt"].read())
# -> "Nested Hello"

root.print_tree()
```

---

### Factory Function

```python
from AviTwilTools import file

f = file("notes.txt")    # Returns TxtFile
f.write("Hello from factory")
print(f.read())
```

---

## 🧩 Mini Project Example

```python
from AviTwilTools import Folder, TxtFile, JsonFile, CsvFile, YamlFile, file

root = Folder("project")
data = Folder("project/data")
reports = Folder("project/reports")

# Create files in different formats
TxtFile("readme.txt", root).write("This is my project")
JsonFile("config.json", root).write({"version": "1.0", "author": "Avi Twil"})
CsvFile("users.csv", data).write([["id", "name"], [1, "Alice"], [2, "Bob"]])
YamlFile("settings.yaml", data).write({"debug": True, "workers": 4})
file("log.txt", reports).write("System started...")

# Read files using folder navigation
print(root["readme.txt"].read())         
print(root["config.json"].read())        
print(root.data["users.csv"].read())     
print(root.data["settings.yaml"].read()) 
print(root.reports["log.txt"].read())    

# Show tree
root.print_tree()
```

Example output:

```
project/
├─ data/
│  ├─ users.csv
│  └─ settings.yaml
├─ reports/
│  └─ log.txt
├─ readme.txt
└─ config.json
```

---

## 📚 API Reference

### 📂 Folder

Represents a filesystem folder mirrored in memory.
Each path is cached (singleton-per-path). Auto-creates directories if missing.

**Constructor**

```python
Folder(path: str = None)
```

**Key methods**

* `add(item: File | Folder)`
* `remove(folder_name: str)`
* `move(target_folder: Folder)`
* `copy(target_folder: Folder) -> Folder`
* `recursive_delete()`
* `parent() -> Folder`
* `list_dir() -> dict`
* `print_tree(prefix="", is_last=True)`
* `_map_folder()`

**Special access**

* `folder.subfolder`
* `folder["file.txt"]`
* `item in folder`

---

### 📄 File (base class)

Defines a unified interface for all file types.

**Common methods**

* `read() -> Any`
* `write(data: Any) -> None`
* `append(data: Any) -> None`
* `exist() -> bool`
* `copy(destination: str) -> str`
* `move(destination: str) -> str`
* `delete() -> None`

---

### 📑 TxtFile

* `read() -> str`
* `write(data: str)`
* `append(data: str)`

### 📑 JsonFile

* `read() -> Any`
* `write(data: Any)`
* `append(data: dict | list)`

### 📑 CsvFile

* `read() -> List[List[str]]`
* `write(data: List[List[str]])`
* `append(data: List[str])`

### 📑 YamlFile

* `read() -> Any`
* `write(data: Any)`
* `append(data: dict | list)`

### 📑 XmlFile

* `read() -> Element`
* `write(data: Element)`
* `append(data: Element)`

### 📑 ByteFile

* `read() -> bytes`
* `write(data: bytes)`
* `append(data: bytes)`

### 📑 DillFile

* `read() -> Any`
* `write(data: Any)`
* `append(data: Any)`

### 📑 VarDBFile

* **Default scope = `globals()`**
* `read(scope=None) -> dict`
* `write(data: Any)` – clears and writes.
* `append(data: Any)` – adds to VariableDB.

---

### 🏭 Factory Function

```python
from AviTwilTools import file

f = file("notes.txt")     # TxtFile
f2 = file("data.json")    # JsonFile
f3 = file("store.db")     # VarDBFile
```

---

## 📝 License

MIT License. See [GitHub repo](https://github.com/avitwil/AT_tools) for details.
