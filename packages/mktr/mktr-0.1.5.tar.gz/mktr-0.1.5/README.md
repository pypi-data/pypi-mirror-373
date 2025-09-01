# mktr

[![PyPI Version](https://img.shields.io/pypi/v/mktr.svg)](https://pypi.org/project/mktr/)
[![Python Version](https://img.shields.io/pypi/pyversions/mktr.svg)](https://pypi.org/project/mktr/)
[![License](https://img.shields.io/pypi/l/mktr.svg)](https://opensource.org/licenses/MIT)

**mktr** is a Python utility to create or destroy filesystem structures from a tree-like text representation. It provides both a graphical user interface (GUI) and command-line interface (CLI).


## Features

* Interactive GUI for easy filesystem creation
* CLI mode for automation and scripting
* Generate directory and file structures from a tree format
* Safe recursive files/directories deletion with `--destroy` supporting glob patterns
* Cross-platform support (Windows, macOS, Linux)

## Installation

```bash
pip install mktr
```

## Usage

### GUI

Run the GUI without arguments:

```bash
mktr
```

### CLI

Create filesystem from a tree structure file:

```bash
mktr some_tree.txt
```

Destroy files or directories recursively (supports glob patterns):

```bash
mktr --destroy path/to/directory
mktr --destroy partial-name-*
```



## Tree Structure Format

* Use tree characters (`├`, `└`, `│`, `─`) or slash `/` to denote directories.
* Files are lines without trailing slash.

Example:

```
project/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## Development

* Python 3.7+
* Requires `customtkinter` (installed automatically via `install_requires`) for GUI mode

## License

MIT License

