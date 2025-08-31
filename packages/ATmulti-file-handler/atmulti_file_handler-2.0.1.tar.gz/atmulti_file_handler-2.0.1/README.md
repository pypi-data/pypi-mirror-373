
# ATmulti_file_handler

A unified **file handling abstraction layer** for multiple file formats. This Python package provides a consistent interface to work with various file types including text, JSON, CSV, YAML, XML, Dill, binary files, and a custom VariableDB database.  

## Features

- Unified `File` base class with consistent interface.
- Format-specific subclasses:
  - `TxtFile`   → `.txt`
  - `JsonFile`  → `.json`
  - `CsvFile`   → `.csv`
  - `DillFile`  → `.dill`
  - `XmlFile`   → `.xml`
  - `YamlFile`  → `.yml` / `.yaml`
  - `ByteFile`  → `.bin` / `.exe` / `.img` / `.jpg`
  - `VarDBFile` → `.db` (requires `avi_tools` package)
- Common operations: `read`, `write`, `append`, `exist`, `copy`, `move`, `delete`.
- Automatic directory and file creation if missing.
- Factory function `file()` to automatically choose the right subclass based on extension.

---

## Installation

You can install the package directly from **PyPI**:

```bash
pip install ATmulti_file_handler
````

This will also install all required dependencies:
`dill`, `PyYAML`, `avi_tools`.

---

## Usage

### Import the package

```python
from ATmulti_file_handler import file
```

---

### Working with Text Files

```python
f = file("notes.txt")
f.write("Hello World")
print(f.read())   # -> "Hello World"
f.append("\nAppended text")
```

---

### Working with JSON

```python
f = file("data.json")
f.write({"a": 1})
print(f.read())   # -> {"a": 1}
f.append({"b": 2})
print(f.read())   # -> {"a": 1, "b": 2}
```

---

### Working with CSV

```python
f = file("table.csv")
f.write([["Name","Age"],["Alice","30"]])
f.append(["Bob","25"])
print(f.read())   # -> [["Name","Age"],["Alice","30"],["Bob","25"]]
```

---

### Working with Dill (Python objects)

```python
f = file("data.dill")
f.write([1,2,3])
f.append(4)
print(f.read())   # -> [1,2,3,4]
```

---

### Working with YAML

```python
f = file("config.yaml")
f.write({"setting": True})
f.append({"debug": False})
print(f.read())   # -> {"setting": True, "debug": False}
```

---

### Working with XML

```python
import xml.etree.ElementTree as ET

f = file("data.xml")
root = ET.Element("root")
f.write(root)
child = ET.Element("child")
root.append(child)
f.append(ET.Element("another_child"))
```

---

### Working with Binary Files

```python
f = file("data.bin")
f.write(b"Hello")
f.append(b" World")
print(f.read())  # -> b"Hello World"
```

---

### Working with VariableDB Files

```python
b = 20
f = file("config.db", scope=globals(), data={"a": 10})
f.append(b)
print(f.read())   # -> {"a": 10, "b": 20}
```

---

### Common Operations

```python
f = file("notes.txt")
print(f.exist())           # True/False
f.copy("/tmp")             # Copies file to /tmp
f.move("/tmp")             # Moves file to /tmp
f.delete()                 # Deletes the file
```

---

## Author

**Avi Twil**

GitHub: [https://github.com/avitwil/ATmulti\_file\_handler](https://github.com/avitwil/ATmulti_file_handler)

---

## License

MIT License

