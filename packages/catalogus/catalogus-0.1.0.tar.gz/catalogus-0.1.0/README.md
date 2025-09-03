# Catalogus

A Python library providing classes for name-to-object registry-like support.

## Overview

Catalogus provides a simple and extensible registry system that allows you to:
- Register objects by name
- Retrieve objects by name
- Support lazy loading of objects
- Maintain type safety with generic support

This library was extracted from the Breezy version control system to provide a reusable registry implementation.

## Installation

```bash
pip install catalogus
```

## Quick Start

```python
from catalogus import Registry

# Create a registry
my_registry = Registry()

# Register objects directly
my_registry.register('item1', some_object)

# Register with lazy loading
my_registry.register_lazy('item2', 'my.module', 'MyClass')

# Retrieve objects
obj = my_registry.get('item1')
```

## Features

- **Type-safe**: Full generic type support with TypeVar
- **Lazy loading**: Objects can be loaded on-demand from modules
- **Flexible registration**: Support for direct objects and lazy imports
- **Iterator support**: Iterate over registered items
- **Python 3.9+**: Modern Python support

## Development

Install development dependencies:

```bash
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Format code:

```bash
ruff format
```

Check code style:

```bash
ruff check
mypy catalogus
```

## License

This project is licensed under the GNU General Public License v2 or later (GPLv2+).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.