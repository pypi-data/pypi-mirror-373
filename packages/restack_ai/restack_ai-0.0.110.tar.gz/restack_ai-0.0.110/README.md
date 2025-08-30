# Restack AI libraries

This is the Python Restack AI libraries.

## Installation

You can install the Restack AI libraries using pip:

### Using pip

```bash
pip install restack_ai
```

### Using Poetry

```bash
poetry add restack_ai
```

### Using uv

```bash
uv add restack_ai
```

## Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

## Usage

To use the libraries in your project, you can import it like this:

```python
from restack_ai import Restack
```

## Initialize the Restack client

```python
client = Restack()
```

## Documentation

For detailed usage instructions, please visit our examples repository at [https://github.com/restackio/examples-python](https://github.com/restackio/examples-python).

## Development

If you want to contribute to the libraries development:

### Clone the repository and navigate to the `engine/libraries/python` directory.

### Install Poetry/uv if you haven't already: [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation) or use pip

### Activate the virtual environment:

If using uv:

```bash
uv venv && source .venv/bin/activate
```

If using poetry:

```bash
poetry env use 3.12 && poetry shell
```

If using pip:

```bash
python -m venv .venv && source .venv/bin/activate
```

### Install the project dependencies:

If using uv:

```bash
uv sync
```

If using Poetry:

```bash
poetry install
```

If using pip:

```bash
pip install -e .
```
