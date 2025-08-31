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
import os
import json
import csv
import dill
import shutil
from avi_tools import VariableDB
import xml.etree.ElementTree as ET
import yaml
from typing import Any, List, Dict, Union, Optional


class File:
    """
    Abstract base class for file handling.
    Provides a unified interface for different file formats and common operations.
    """

    def __init__(self, name: str, path: str = None, *, scope: Dict[str, Any] = None,
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
        if not path:
            self.path = os.getcwd()
        else:
            self.path = path
        self.full_path = os.path.join(self.path, name)
        self.scope = scope or {}
        self.data = data or {}

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

    def __new__(cls, name: str, path: str = None):
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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
            path = os.getcwd()
        elif not os.path.exists(path):
            os.makedirs(path)
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


def file(name: str, path: str = None, *, scope: Dict[str, Any] = None, data: Optional[Dict[str, Any]] = None):
    """
    Factory function to create an appropriate File subclass
    based on the file extension.

    Parameters
    ----------
    name : str
        Name of the file (including extension).
    path : str, optional
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
