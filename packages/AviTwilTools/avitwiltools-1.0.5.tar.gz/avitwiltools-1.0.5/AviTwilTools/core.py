
import os
import json
import csv
import dill
import shutil
from avi_tools import VariableDB
import xml.etree.ElementTree as ET
import yaml
from typing import Any, List, Dict, Union, Optional


class Folder:
    pass




class File:
    """
    Abstract base class for file handling.
    Provides a unified interface for different file formats and common operations.
    """

    def __init__(self, name: str, path: str | Folder = None, *, scope: Dict[str, Any] = None,
                 data: Optional[Dict[str, Any]] = None):
        """
        Initialize a file object with a given directory path.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str
            Path to the directory.

        Raises
        ------
        ValueError
            If name or path are empty.

        Examples
        --------
        f = File("example.txt", "/tmp")
        """
        if not name:
            raise ValueError("File name cannot be empty.")
        self.name = name
        if isinstance(path, Folder):
            self.path = path.full_path
            self.__folder = path

        elif not path:
            self.__folder = Folder(os.getcwd())
            self.path = self.__folder.full_path
        else:
            self.__folder = Folder(path)

            self.path = self.__folder.full_path
        self.full_path = os.path.join(self.path, name)
        self.__add_to_folder()
        if type(self) == VarDBFile :
            self.scope = scope or {}
            self.data = data or {}


    def __add_to_folder(self):
        self.__folder.add(self)

    def read(self) -> Any:
        """
        Read data from the file.

        Raises
        ------
        NotImplementedError
            If not implemented in subclass.
        """
        raise NotImplementedError

    def write(self, data: Any) -> None:
        """
        Write data to the file.

        Parameters
        ----------
        data : Any
            Data to write.

        Raises
        ------
        NotImplementedError
            If not implemented in subclass.
        """
        raise NotImplementedError

    def append(self, data: Any) -> None:
        """
        Append data to the file.

        Parameters
        ----------
        data : Any
            Data to append.

        Raises
        ------
        NotImplementedError
            If not implemented in subclass.
        """
        raise NotImplementedError

    def exist(self) -> bool:
        """
        Check if the file exists.

        Returns
        -------
        bool
            True if the file exists, False otherwise.

        Examples
        --------
        f = TxtFile("example.txt")
        f.exist()
        """
        return os.path.exists(self.full_path)

    def copy(self, destination: str) -> str:
        """
        Copy the file to a destination path.

        Parameters
        ----------
        destination : str
            Destination directory or file path.

        Returns
        -------
        str
            Full path of the copied file.

        Raises
        ------
        FileNotFoundError
            If the source file does not exist.
        PermissionError
            If the operation is not permitted.
        OSError
            For other I/O errors.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        new_path = f.copy("/tmp")
        """
        if not self.exist():
            raise FileNotFoundError(f"Source file does not exist: {self.full_path}")
        copied_path = shutil.copy(self.full_path, destination)
        return copied_path

    def move(self, destination: str) -> str:
        """
        Move the file to a new directory.

        Parameters
        ----------
        destination : str
            Directory to move the file to.

        Returns
        -------
        str
            New file path after move.

        Raises
        ------
        FileNotFoundError
            If the source file does not exist.
        ValueError
            If destination is not a directory.
        PermissionError
            If the operation is not permitted.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        new_path = f.move("/tmp")
        """
        if not os.path.exists(self.full_path):
            raise FileNotFoundError(f"Source file does not exist: {self.full_path}")
        if not os.path.isdir(destination):
            raise ValueError(f"Destination is not a directory: {destination}")
        moved_path = shutil.move(self.full_path, destination)
        self.full_path = moved_path
        return moved_path

    def delete(self) -> None:
        """
        Delete the file.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        OSError
            If deletion fails.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        f.delete()
        """
        if not self.exist():
            raise FileNotFoundError(f"File does not exist: {self.full_path}")
        os.remove(self.full_path)


class TxtFile(File):
    """Class for handling plain text files."""

    def __new__(cls, name: str, path: str | Folder = None):
        """
        Create a new TxtFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        TxtFile
            A new instance of TxtFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path,Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> str:
        """
        Read text from file.

        Returns
        -------
        str
            File contents.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        content = f.read()
        """
        with open(self.full_path, "rt", encoding="utf-8") as file:
            return file.read()

    def write(self, data: str) -> None:
        """
        Write text to file (overwrite).

        Parameters
        ----------
        data : str
            Text to write.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        """
        with open(self.full_path, "wt", encoding="utf-8") as file:
            file.write(data)

    def append(self, data: str) -> None:
        """
        Append text to file.

        Parameters
        ----------
        data : str
            Text to append.

        Examples
        --------
        f = TxtFile("example.txt")
        f.write("Hello")
        f.append(" World")
        """
        with open(self.full_path, "at", encoding="utf-8") as file:
            file.write(data)


class JsonFile(File):
    """Class for handling JSON files."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new JsonFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        JsonFile
            A new instance of JsonFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> Any:
        """
        Read JSON data from file.

        Returns
        -------
        Any
            Parsed JSON object.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        json.JSONDecodeError
            If the JSON is invalid.

        Examples
        --------
        f = JsonFile("data.json")
        f.write({"a":1})
        data = f.read()
        """
        with open(self.full_path, "rt", encoding="utf-8") as file:
            return json.load(file)

    def write(self, data: Any) -> None:
        """
        Write JSON data to file.

        Parameters
        ----------
        data : Any
            JSON serializable object.

        Examples
        --------
        f = JsonFile("data.json")
        f.write([1,2,3])
        """
        with open(self.full_path, "wt", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def append(self, data: Union[Dict, List]) -> None:
        """
        Append data to JSON file.

        Parameters
        ----------
        data : dict or list
            Data to append.

        Examples
        --------
        f = JsonFile("data.json")
        f.write([])
        f.append({"a":1})
        """
        if self.exist():
            content = self.read()
            if isinstance(content, list):
                content.append(data)
            elif isinstance(content, dict) and isinstance(data, dict):
                content.update(data)
            else:
                content = [content, data]
        else:
            content = data
        self.write(content)


class CsvFile(File):
    """Class for handling CSV files."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new CsvFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        CsvFile
            A new instance of CsvFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> List[List[str]]:
        """
        Read CSV file.

        Returns
        -------
        List[List[str]]
            CSV content as list of rows.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        Examples
        --------
        f = CsvFile("data.csv")
        f.write([["a","b"],["1","2"]])
        data = f.read()
        """
        with open(self.full_path, "rt", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            return list(reader)

    def write(self, data: List[List[str]]) -> None:
        """
        Write data to CSV file.

        Parameters
        ----------
        data : list of list of str
            Rows to write.

        Examples
        --------
        f = CsvFile("data.csv")
        f.write([["a","b"],["1","2"]])
        """
        with open(self.full_path, "wt", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def append(self, data: List[str]) -> None:
        """
        Append a row to CSV file.

        Parameters
        ----------
        data : list of str
            Row to append.

        Examples
        --------
        f = CsvFile("data.csv")
        f.write([["a","b"]])
        f.append(["1","2"])
        """
        with open(self.full_path, "at", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)


class DillFile(File):
    """Class for handling serialized Python objects using Dill."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new DillFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        DillFile
            A new instance of DillFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> Any:
        """
        Read a Python object from file.

        Returns
        -------
        Any
            Deserialized Python object.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        Examples
        --------
        f = DillFile("obj.dill")
        f.write({"a":1})
        data = f.read()
        """
        with open(self.full_path, "rb") as file:
            return dill.load(file)

    def write(self, data: Any) -> None:
        """
        Serialize and write a Python object to file.

        Parameters
        ----------
        data : Any
            Python object to serialize.

        Examples
        --------
        f = DillFile("obj.dill")
        f.write([1,2,3])
        """
        with open(self.full_path, "wb") as file:
            dill.dump(data, file)

    def append(self, data: Any) -> None:
        """
        Append object to Dill file.

        Parameters
        ----------
        data : Any
            Python object to append.

        Examples
        --------
        f = DillFile("obj.dill")
        f.write([])
        f.append(42)
        """
        if self.exist():
            content = self.read()
            if isinstance(content, list):
                content.append(data)
            else:
                content = [content, data]
        else:
            content = [data]
        self.write(content)


class XmlFile(File):
    """Class for handling XML files."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new XmlFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        XmlFile
            A new instance of XmlFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> ET.Element:
        """
        Read XML data from file.

        Returns
        -------
        xml.etree.ElementTree.Element
            Root XML element.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ET.ParseError
            If XML is invalid.

        Examples
        --------
        f = XmlFile("data.xml")
        root = ET.Element("root")
        f.write(root)
        root2 = f.read()
        """
        tree = ET.parse(self.full_path)
        return tree.getroot()

    def write(self, data: ET.Element) -> None:
        """
        Write XML data to file.

        Parameters
        ----------
        data : xml.etree.ElementTree.Element
            Root XML element.

        Examples
        --------
        f = XmlFile("data.xml")
        root = ET.Element("root")
        f.write(root)
        """
        tree = ET.ElementTree(data)
        tree.write(self.full_path, encoding="utf-8", xml_declaration=True)

    def append(self, data: ET.Element) -> None:
        """
        Append an element to the XML root.

        Parameters
        ----------
        data : xml.etree.ElementTree.Element
            Child element to append.

        Examples
        --------
        f = XmlFile("data.xml")
        root = ET.Element("root")
        f.write(root)
        f.append(ET.Element("child"))
        """
        if self.exist():
            root = self.read()
            root.append(data)
            self.write(root)
        else:
            self.write(data)


class YamlFile(File):
    """Class for handling YAML files."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new YamlFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        YamlFile
            A new instance of YamlFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> Any:
        """
        Read YAML data from file.

        Returns
        -------
        Any
            Parsed YAML object.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        yaml.YAMLError
            If YAML is invalid.

        Examples
        --------
        f = YamlFile("data.yaml")
        f.write({"a":1})
        data = f.read()
        """
        with open(self.full_path, "rt", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def write(self, data: Any) -> None:
        """
        Write YAML data to file.

        Parameters
        ----------
        data : Any
            YAML-serializable object.

        Examples
        --------
        f = YamlFile("data.yaml")
        f.write([1,2,3])
        """
        with open(self.full_path, "wt", encoding="utf-8") as file:
            yaml.safe_dump(data, file, allow_unicode=True)

    def append(self, data: Union[Dict, List]) -> None:
        """
        Append data to YAML file.

        Parameters
        ----------
        data : dict or list
            Data to append.

        Examples
        --------
        f = YamlFile("data.yaml")
        f.write([])
        f.append({"a":1})
        """
        if self.exist():
            content = self.read()
            if isinstance(content, dict) and isinstance(data, dict):
                content.update(data)
            elif isinstance(content, list):
                content.append(data)
            else:
                content = [content, data]
        else:
            content = data
        self.write(content)


class ByteFile(File):
    """Class for handling binary files."""

    def __new__(cls, name: str, path: str = None):
        """
        Create a new ByteFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.

        Returns
        -------
        ByteFile
            A new instance of ByteFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with open(os.path.join(path, name), "wb") as f:
                pass
        return super().__new__(cls)

    def read(self) -> bytes:
        """
        Read binary data from file.

        Returns
        -------
        bytes
            File contents.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.

        Examples
        --------
        f = ByteFile("data.bin")
        f.write(b"abc")
        data = f.read()
        """
        with open(self.full_path, "rb") as file:
            return file.read()

    def write(self, data: bytes) -> None:
        """
        Write binary data to file.

        Parameters
        ----------
        data : bytes
            Data to write.

        Examples
        --------
        f = ByteFile("data.bin")
        f.write(b"123")
        """
        with open(self.full_path, "wb") as file:
            file.write(data)

    def append(self, data: bytes) -> None:
        """
        Append binary data to file.

        Parameters
        ----------
        data : bytes
            Data to append.

        Examples
        --------
        f = ByteFile("data.bin")
        f.write(b"abc")
        f.append(b"123")
        """
        with open(self.full_path, "ab") as file:
            file.write(data)


class VarDBFile(File):
    def __new__(cls, name: str, path: str = None, *, scope: Dict[str, Any] = None,
                data: Optional[Dict[str, Any]] = None):
        """
        Create a new VarDBFile instance, ensuring the directory and file exist.

        Parameters
        ----------
        name : str
            Name of the file.
        path : str, optional
            Path to the directory. Defaults to current working directory.
        scope : Dict[str, Any], optional
            Scope dictionary.
        data : Optional[Dict[str, Any]], optional
            Initial data.

        Returns
        -------
        VarDBFile
            A new instance of VarDBFile.
        """
        if not path:
            folder = Folder(os.getcwd())
            path = folder.full_path
        elif isinstance(path, Folder):
            path = path.full_path
        elif not os.path.exists(path):
            folder = Folder(path)
            path = folder.full_path
        if not os.path.exists(os.path.join(path, name)):
            with VariableDB(os.path.join(path, name), scope=scope, data=data) as f:
                pass
        return super().__new__(cls)

    def write(self, data: Any, ) -> None:
        """
        Write data to the VarDB file, clearing existing content.

        Parameters
        ----------
        data : Any
            Data to write.
        """
        with VariableDB(self.full_path, scope=self.scope, data=self.data) as f:
            f.clear()
            f.add(data)

    def read(self, scope=None):
        """
        Read data from the VarDB file.

        Parameters
        ----------
        scope : Any, optional
            Scope to use for reading. Defaults to None.

        Returns
        -------
        Dict[str, Any]
            The data from the file.
        """
        with VariableDB(self.full_path, scope=self.scope, data=self.data) as f:
            f.load()
            return f.data

    def append(self, data: Any, ) -> None:
        """
        Append data to the VarDB file.

        Parameters
        ----------
        data : Any
            Data to append.
        """
        with VariableDB(self.full_path, scope=self.scope, data=self.data) as f:
            f.add(data)


def file(name: str, path: str | Folder = None, *, scope: Dict[str, Any] = None, data: Optional[Dict[str, Any]] = None):
    """
    Factory function to create an appropriate File subclass
    based on the file extension.

    Parameters
    ----------
    name : str
        Name of the file (including extension).
    path : str | Folder optional
        Directory where the file should be stored.
    scope : dict, optional
        Variable scope (used only for VarDBFile).
    data : dict, optional
        Initial data (used only for VarDBFile).

    Returns
    -------
    File or None
        An instance of a File subclass matching the extension,
        or None if the extension is not supported.

    Supported Extensions
    --------------------
    - .txt   -> TxtFile
    - .json  -> JsonFile
    - .csv   -> CsvFile
    - .dill  -> DillFile
    - .xml   -> XmlFile
    - .yml / .yaml -> YamlFile
    - .img / .exe / .bin / .jpg -> ByteFile
    - .db    -> VarDBFile

    Examples
    --------
    f = file("notes.txt")
    f.write("Hello World")

    f2 = file("data.json")
    f2.write({"a": 1})

    f3 = file("config.db", scope={"x": 1}, data={"a": 10})
    f3.append({"b": 20})
    """
    if name.endswith(".txt"):
        return TxtFile(name, path)
    if name.endswith(".json"):
        return JsonFile(name, path)
    if name.endswith(".csv"):
        return CsvFile(name, path)
    if name.endswith(".dill"):
        return DillFile(name, path)
    if name.endswith(".xml"):
        return XmlFile(name, path)
    if name.endswith(".yml") or name.endswith(".yaml"):
        return YamlFile(name, path)
    if name.endswith(".img") or name.endswith(".exe") or name.endswith(".bin") or name.endswith(".jpg"):
        return ByteFile(name, path)
    if name.endswith(".db"):
        return VarDBFile(name, path, scope=scope, data=data)
    else:
        return None




class Folder:
    """
    Represents a filesystem folder that tracks its files and subfolders in memory.
    Ensures automatic linkage of newly created folders to their parent folders
    and maintains hierarchy consistency.

    Attributes:
        full_path (str): Absolute path of this folder.
        name (str): Name of the folder (last component of the path).
        __folders (dict): Maps child folder names to Folder instances.
        __files (dict): Maps file names to File instances.

    Class Attributes:
        __folder_list (dict): Maps absolute folder paths to Folder instances.
    """

    __folder_list = {}

    def __new__(cls, path: str = None):
        """
        Creates or returns an existing Folder instance for the given path.
        Automatically creates the directory on disk if it does not exist.

        Parameters:
            path (str): Absolute or relative path to the folder. Defaults to current working directory.

        Returns:
            Folder: Existing or newly created Folder instance.
        """
        if path in cls.__folder_list:
            return cls.__folder_list[path]

        if not path:
            path = os.getcwd()
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)

        obj = super().__new__(cls)
        cls.__folder_list[path] = obj
        return obj

    def __init__(self, path: str = None):
        """
        Initializes the Folder instance and ensures its parent-child relationships
        are properly registered in __folder_list.

        Parameters:
            path (str): Absolute or relative path to the folder. Defaults to current working directory.

        Attributes:
            full_path (str): Absolute path of the folder.
            name (str): Name of the folder (last component of the path).
            __folders (dict): Child Folder instances.
            __files (dict): File instances inside this folder.
        """
        self.full_path = os.path.abspath(path) if path else os.getcwd()
        self.name = os.path.basename(self.full_path)
        self.__folders = {}
        self.__files = {}
        self._ensure_path()
        self._map_folder()

    def add(self, item: Any):
        """
        Adds a File or Folder to this folder.

        Parameters:
            item (File or Folder): The object to add.

        Raises:
            ValueError: If the file already exists in this folder.
            TypeError: If the item is not a File or Folder.
        """
        if isinstance(item, File):
            self.__check_in(item)
            if os.path.basename(item.full_path) not in self.__files:
                self.__files[os.path.basename(item.full_path)] = item
        elif isinstance(item, Folder):
            self.__check_in(item)
            if os.path.basename(item.full_path) not in self.__folders:
                self.__folders[os.path.basename(item.full_path)] = item
        else:
            raise TypeError("Folder can only contain File or Folder instances")

    def __check_in(self, item):
        """
        Checks if the item belongs to this folder.

        Parameters:
            item (File or Folder): Object to check.

        Raises:
            ValueError: If the item's parent directory does not match this folder.
        """
        if os.path.dirname(os.path.abspath(item.full_path)) != self.full_path:
            raise ValueError(f"{os.path.basename(item.full_path)} is not inside {self.name}")

    def __getattr__(self, item):
        """
        Access child folders as attributes.

        Parameters:
            item (str): Name of the folder.

        Returns:
            Folder: Child folder instance if exists.

        Raises:
            AttributeError: If folder does not exist.
        """
        if item in self.__folders:
            return self.__folders[item]
        return self.__dict__[item]

    def __getitem__(self, item):
        """
        Access child files or folders like a dictionary.

        Parameters:
            item (str): Name of the file or folder.

        Returns:
            File or Folder: Corresponding object if exists, otherwise None.
        """
        if item in self.__files:
            return self.__files[item]
        if item in self.__folders:
            return self.__folders[item]
        return None

    def folders(self):
        """
        Returns the names of all child folders.

        Returns:
            list: List of folder names.
        """
        return self.__folders.keys()

    def __contains__(self, item):
        """
        Checks if a file or folder exists in this folder.

        Parameters:
            item (str or File or Folder): Item name or object.

        Returns:
            bool: True if item exists, otherwise False.
        """
        return item in self.__folders or item in self.__files or item in self.__folders.values() or item in self.__files.values()

    @classmethod
    def get_all_folders(cls):
        """
        Returns all Folder instances tracked by the class.

        Returns:
            dict: Mapping of folder paths to Folder instances.
        """
        return cls.__folder_list

    def _ensure_path(self):
        """ Ensures that all parent folders in the path exist in __folder_list.
        Automatically links child folders to their parents.
        """
        parts = self.full_path.split(os.sep)
        for i in range(len(parts)):
            current_path = os.sep.join(parts[:i + 1])
            parent_path = os.path.dirname(current_path)
            if parent_path in Folder.__folder_list and current_path in Folder.__folder_list:
                parent_obj = Folder.__folder_list[parent_path]
                if os.path.basename(current_path) in parent_obj.folders():
                    continue
                current_obj = Folder.__folder_list[current_path]
                parent_obj.add(current_obj)
            if current_path not in Folder.__folder_list and parent_path in Folder.__folder_list:
                current_obj = Folder(os.path.abspath(current_path))
                parent_obj = Folder.__folder_list[parent_path]
                parent_obj.add(current_obj)
            # Fix: Always set current_obj if the path exists before handling children
            if current_path in Folder.__folder_list:
                current_obj = Folder.__folder_list[current_path]
            else:
                continue  # Should not happen, but skip children if not
            for child_path, child_obj in Folder.__folder_list.items():
                if os.path.dirname(child_path) == current_path and os.path.basename(
                        child_path) not in current_obj.folders():
                    current_obj.add(child_obj)

    def remove(self, folder_name: str):
        """
        Removes a child folder if it is empty (has no files or subfolders).

        Parameters:
            folder_name (str): Name of the child folder to remove.

        Raises:
            ValueError: If the folder does not exist, or if it is not empty.
        """
        if folder_name not in self.__folders:
            raise ValueError(f"No folder named '{folder_name}' exists in '{self.name}'")

        folder_to_remove = self.__folders[folder_name]

        if folder_to_remove.__folders or folder_to_remove.__files:
            raise ValueError(f"Folder '{folder_name}' is not empty and cannot be removed")

        # Remove from internal dictionary and global folder list
        del self.__folders[folder_name]
        if folder_to_remove.full_path in Folder.__folder_list:
            del Folder.__folder_list[folder_to_remove.full_path]

        # Optionally remove the folder from disk
        if os.path.exists(folder_to_remove.full_path):
            os.rmdir(folder_to_remove.full_path)

    def move(self, target_folder: "Folder"):
        """
        Moves the current folder into another target folder.

        Parameters:
            target_folder (Folder): The folder to move this folder into.

        Raises:
            TypeError: If target_folder is not an instance of Folder.
            ValueError: If a folder with the same name already exists in the target folder.
        """
        if not isinstance(target_folder, Folder):
            raise TypeError("target_folder must be a Folder instance")

        if self.name in target_folder.__folders:
            raise ValueError(f"A folder named '{self.name}' already exists in '{target_folder.name}'")

        # Remove from old parent if exists
        parent_path = os.path.dirname(self.full_path)
        if parent_path in Folder.__folder_list:
            old_parent = Folder.__folder_list[parent_path]
            if self.name in old_parent.__folders:
                del old_parent.__folders[self.name]

        # Update folder path
        new_full_path = os.path.join(target_folder.full_path, self.name)
        old_full_path = self.full_path
        self.full_path = new_full_path

        # Move on disk
        if os.path.exists(old_full_path):
            os.rename(old_full_path, new_full_path)

        # Add to target folder
        target_folder.__folders[self.name] = self

        # Update global folder list
        del Folder.__folder_list[old_full_path]
        Folder.__folder_list[new_full_path] = self

    def copy(self, target_folder: "Folder") -> "Folder":
        """
        Copies the current folder and its contents into another target folder.

        Parameters:
            target_folder (Folder): The folder to copy this folder into.

        Returns:
            Folder: The new copied folder object.

        Raises:
            TypeError: If target_folder is not an instance of Folder.
            ValueError: If a folder with the same name already exists in the target folder.
        """
        if not isinstance(target_folder, Folder):
            raise TypeError("target_folder must be a Folder instance")

        if self.name in target_folder.__folders:
            raise ValueError(f"A folder named '{self.name}' already exists in '{target_folder.name}'")

        # Determine new folder path
        new_full_path = os.path.join(target_folder.full_path, self.name)

        # Copy folder contents on disk
        shutil.copytree(self.full_path, new_full_path)

        # Create new Folder object
        new_folder = Folder(new_full_path)

        # Add to target folder
        target_folder.__folders[new_folder.name] = new_folder

        return new_folder

    def recursive_delete(self):
        """
        Recursively deletes the folder and all its contents from disk,
        and removes all child folders from the global folder list.
        """
        # Remove from parent __folders
        parent_path = os.path.dirname(self.full_path)
        if parent_path in Folder.__folder_list:
            parent_obj = Folder.__folder_list[parent_path]
            if self.name in parent_obj.__folders:
                del parent_obj.__folders[self.name]

        # Remove all entries in __folder_list that start with this folder path
        to_delete = [path for path in Folder.__folder_list if path.startswith(self.full_path)]
        for path in to_delete:
            del Folder.__folder_list[path]

        # Delete folder and all contents on disk
        if os.path.exists(self.full_path):
            shutil.rmtree(self.full_path)

    def parent(self):
        """
        Returns the parent Folder instance of this folder.
        If the parent does not exist in __folder_list, it will be created.

        Returns:
            Folder: Parent folder object.
        """
        parent_path = os.path.dirname(self.full_path)
        if parent_path not in Folder.__folder_list:
            Folder(parent_path)
        return Folder.__folder_list[parent_path]

    def list_dir(self):
        """
        Returns all files and folders in this folder according to the internal dictionaries.

        Returns:
            dict: Dictionary with two keys: 'folders' and 'files'.
                  'folders' maps to a list of folder names.
                  'files' maps to a list of file names.
        """
        return {
            "folders": list(self.__folders.keys()),
            "files": list(self.__files.keys())
        }

    def print_tree(self, prefix: str = "", is_last: bool = True):
        """ Prints the folder structure as a tree, including files, correctly handling empty folders.
        Parameters:
            prefix (str): Used internally for formatting recursion.
            is_last (bool): True if the folder is the last item in its parent folder.
        """
        branch = "└─ " if is_last else "├─ "
        if prefix == "":
            print(f"{self.name}/")
        else:
            print(f"{prefix}{branch}{self.name}/")
        # Arrangement of folders then files
        entries = list(self.__folders.values()) + list(self.__files.keys())
        count = len(entries)
        for i, entry in enumerate(entries):
            last = i == count - 1
            if isinstance(entry, Folder):
                new_prefix = prefix + ("   " if is_last else "│  ")
                entry.print_tree(prefix=new_prefix, is_last=last)
            else:
                file_branch = "└─ " if last else "├─ "
                file_prefix = prefix + ("   " if is_last else "│  ")
                print(f"{file_prefix}{file_branch}{entry}")

    def _map_folder(self):
        """ Recursively registers this folder and all its subfolders into the class's __folder_list.
        Ensures that even subfolders that were not previously added are tracked.
        Also maps existing files on disk if they match supported extensions.
        Example usage:
            root = Folder("data")
            root._map_folder()  # All subfolders and supported files under "data" are now tracked
        """
        if self.full_path not in Folder.__folder_list:
            Folder.__folder_list[self.full_path] = self
        # Check all entries on disk
        for entry in os.listdir(self.full_path):
            entry_path = os.path.join(self.full_path, entry)
            if os.path.isdir(entry_path):
                if entry_path not in Folder.__folder_list:
                    subfolder = Folder(entry_path)
                    self.__folders[entry] = subfolder
                subfolder = Folder.__folder_list[entry_path]
                subfolder._map_folder()
            elif os.path.isfile(entry_path):
                if entry not in self.__files:
                    f = file(entry, self)
                    if f is not None:
                        # The file is automatically added via __init__
                        pass
