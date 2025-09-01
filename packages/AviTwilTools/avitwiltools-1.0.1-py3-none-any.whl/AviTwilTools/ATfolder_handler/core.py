import os
import shutil
from typing import Any

from AviTwilTools.ATmulti_file_handler import File
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
            if os.path.basename(item.full_path) in self.__files:
                raise ValueError(f"{os.path.basename(item.full_path)} already exists in {self.name}")
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
        """
        Ensures that all parent folders in the path exist in __folder_list.
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

                for child_path, child_obj in Folder.__folder_list.items():
                    if os.path.dirname(child_path) == current_path and os.path.basename(child_path) not in current_obj.folders():
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
        """
        Prints the folder structure as a tree, including files, correctly handling empty folders.

        Parameters:
            prefix (str): Used internally for formatting recursion.
            is_last (bool): True if the folder is the last item in its parent folder.
        """
        branch = "└─ " if is_last else "├─ "
        if prefix == "":
            # root folder
            print(f"{self.name}/")
        else:
            print(f"{prefix}{branch}{self.name}/")

        # הסידור של תיקיות ואז קבצים
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
        """
        Recursively registers this folder and all its subfolders into the class's __folder_list.
        Ensures that even subfolders that were not previously added are tracked.

        Example usage:
            root = Folder("data")
            root.map_folder()  # All subfolders under "data" are now in __folder_list
        """
        if self.full_path not in Folder.__folder_list:
            Folder.__folder_list[self.full_path] = self

        # Check all subdirectories on disk and add missing ones
        for entry in os.listdir(self.full_path):
            entry_path = os.path.join(self.full_path, entry)
            if os.path.isdir(entry_path):
                if entry_path not in Folder.__folder_list:
                    subfolder = Folder(entry_path)
                    self.__folders[entry] = subfolder
                    subfolder._map_folder()
