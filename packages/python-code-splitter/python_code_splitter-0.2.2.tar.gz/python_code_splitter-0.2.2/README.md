# python-code-splitter

A tool to split Python code by classes and functions.

## Install

```sh
pip install python-code-splitter
```

## Usage

```sh
python-code-splitter path/to/file.py
```

Class and function definitions are extracted from the target file and written into separate new files (including decorators and comments). The new file name will be `{class name or function name converted to snake_case}.py`. The remaining content of the target file is moved to `__init__.py`. Necessary import statements are added to the top of each file.

The command has a `--git` option.

```sh
python-code-splitter path/to/file.py --git
```

It automatically creates a git branch based on the target file path, and commits in review-friendly units.

You can also use the `--targets` option to move only classes or functions.

```sh
python-code-splitter path/to/file.py --targets class
```
