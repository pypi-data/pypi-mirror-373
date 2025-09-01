# multicollections

Welcome to the documentation for [`multicollections`](https://github.com/gerlero/multicollections)!

A Python library for multi-mapping collections - dictionaries that can hold multiple values for the same key while preserving insertion order.

## Features

- **MultiDict**: A fully generic dictionary that allows multiple values per key
- **Abstract Base Classes**: Well-defined interfaces for implementing multi-mapping types
- **Type Safety**: Full type annotations and generic support
- **Familiar API**: Dictionary-like interface that's easy to learn and use

## Installation

```bash
pip install multicollections
```

## Quick Example

```python
from multicollections import MultiDict

# Create a MultiDict with duplicate keys
md = MultiDict([('fruit', 'apple'), ('fruit', 'banana'), ('color', 'red')])

# Access the first value
print(md['fruit'])  # 'apple'

# Add more values
md.add('fruit', 'orange')
```

## Documentation

- **[MultiDict API](api/multicollections.md)** - Complete reference for the main MultiDict class
- **[Abstract Base Classes](api/abc.md)** - Documentation for the abc module interfaces
