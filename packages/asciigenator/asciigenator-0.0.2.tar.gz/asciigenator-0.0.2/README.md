# asciigenator <!-- omit in toc -->

A lightweight Python library for generating ASCII art from text.

[![PyPI version](https://img.shields.io/pypi/v/asciigenator.svg?color=blue)](https://pypi.org/project/asciigenator/)
[![Python Versions](https://img.shields.io/pypi/pyversions/asciigenator.svg)](https://pypi.org/project/asciigenator/)
[![License](https://img.shields.io/github/license/bhatishan2003/asciigenator)](LICENSE)
[![Python application](https://github.com/bhatishan2003/asciigenator/actions/workflows/python-app.yml/badge.svg)](https://github.com/bhatishan2003/asciigenator/actions/workflows/python-app.yml)
[![Coverage](https://img.shields.io/codecov/c/github/bhatishan2003/asciigenator)](https://codecov.io/gh/bhatishan2003/asciigenator)

## Table of Contents <!-- omit in toc -->

- [Installation](#installation)
- [Usage](#usage)
  - [Basic Python Usage](#basic-python-usage)
  - [Command Line Usage](#command-line-usage)
- [Testing](#testing)
- [Development Notes](#development-notes)

---

## Installation

-   Clone the repository:

    ```bash
    git clone https://github.com/bhatishan2003/asciigenator.git
    cd asciigenator
    ```

-   Install the package:

    ```bash
    pip install .
    ```

-   For development (editable mode):

    ```bash
    pip install -e .
    ```

## Usage

### Basic Python Usage

```python
import asciigenator

# Test simple font
print("=== Simple Font ===")
print(asciigenator.generate("Hello", font="simple"))

# === Simple Font ===
#  *   **  ** *** ***  ** *** *   *
# * * *   *    *   *  *   *   **  *
# ***  *  *    *   *  * * **  * * *
# * *   * *    *   *  * * *   *  **
# * * **   ** *** ***  ** *** *   *

print("\n=== Block Font ===")
print(asciigenator.generate("Ishan", font="block"))

# === Block Font ===
#   █
#  █ █  ████  ████ █████ █████  ████ █████  █   █
#  █ █  █     █       █     █   █     █     ██  █
# █████  ███  █       █     █   █  ██ ████  █ █ █
# █   █     █ █       █     █   █   █ █     █  ██
# █   █ ████   ████ █████ █████  ████ █████ █   █

print("\n=== Available Fonts ===")
print(asciigenator.list_fonts())

# === Available Fonts ===
# ['block', 'simple']

```

### Command Line Usage

```bash
asciigenator "Hello World"
asciigenator "Hello World" --font block
asciigenator --list-fonts
asciigenator "Hello World" --font block  --border "#"
asciigenator "Hello World"  --font block --color magenta
```

## Testing

Run all tests:

```bash
pytest -v
```

## Development Notes

-   Pre-commit

    We use pre-commit to automate linting of our codebase.

    -   Install hooks:
        ```bash
        pre-commit install
        ```
    -   Run Hooks manually (optional):
        ```bash
        pre-commit run --all-files
        ```

-   Ruff:

    -   Lint and format:
        ```bash
        ruff check --fix
        ruff format
        ```
