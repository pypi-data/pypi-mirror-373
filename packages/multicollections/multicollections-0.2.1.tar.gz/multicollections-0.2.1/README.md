# multicollections

A fully generic [`MultiDict`](https://multicollections.readthedocs.io/en/latest/api/multicollections/) class that allows multiple values for the same key while preserving insertion order.

[![Documentation](https://img.shields.io/readthedocs/multicollections)](https://multicollections.readthedocs.io/)
[![CI](https://github.com/gerlero/multicollections/actions/workflows/ci.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/gerlero/multicollections/branch/main/graph/badge.svg)](https://codecov.io/gh/gerlero/multicollections)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Publish](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/gerlero/multicollections/actions/workflows/pypi-publish.yml)
[![PyPI](https://img.shields.io/pypi/v/multicollections)](https://pypi.org/project/multicollections/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/multicollections)](https://pypi.org/project/multicollections/)

## ✨ Features

- **🔑 Multiple values per key**: Store multiple values for the same key, perfect for handling data like HTTP headers, form data, or configuration files
- **📝 Insertion order preserved**: Maintains the order in which items are added
- **🧩 Fully generic**: Accepts any types for both keys and values
- **✅ Thoroughly tested**: 100% code coverage
- **⚡ Type-safe**: Fully typed with generics
- **🪶 Lightweight**: Zero dependencies, pure Python implementation
- **🎯 Rich, compatible API**: Implements the [`multidict` API](https://multidict.aio-libs.org/en/stable/multidict/#multidict)
- **📐 Abstract base classes**: The [`multicollections.abc`](https://multicollections.readthedocs.io/en/latest/api/abc/) module provides a common interface for other custom multi-value collections

## 📦 Installation

### pip

```bash
pip install multicollections
```

### conda

```bash
conda install -c conda-forge multicollections
```

## 🚀 Quick Start

```python
from multicollections import MultiDict

# Create a MultiDict with duplicate keys
headers = MultiDict([
    ('Accept', 'text/html'),
    ('Accept-Encoding', 'gzip'),
    ('Accept', 'application/json'),  # Same key, different value
    ('User-Agent', 'MyApp/1.0')
])

# Access the first value for a key
print(headers['Accept'])  # 'text/html'

# Get ALL values for a key
print(headers.getall('Accept'))  # ['text/html', 'application/json']

# See all key-value pairs (duplicates preserved)
print(list(headers.items()))
# [('Accept', 'text/html'), ('Accept-Encoding', 'gzip'), 
#  ('Accept', 'application/json'), ('User-Agent', 'MyApp/1.0')]

# Add more values for existing keys
headers.add('Accept', 'text/xml')
print(headers.getall('Accept'))  # ['text/html', 'application/json', 'text/xml']
print(len(headers))  # 5 items total

# Remove and return the first value
first_accept = headers.popone('Accept')
print(first_accept)  # 'text/html'
print(headers.getall('Accept'))  # ['application/json', 'text/xml']

# Remove and return all values for a key
all_accepts = headers.popall('Accept')
print(all_accepts)  # ['application/json', 'text/xml']
print('Accept' in headers)  # False

# Create from keyword arguments
config = MultiDict(host='localhost', port=8080, debug=True)

# Mix iterable and keyword arguments
mixed = MultiDict([('a', 1), ('b', 2)], c=3, d=4)
```

## 📖 Why MultiDict?

Standard Python dictionaries can only hold one value per key. When you need to handle data formats that naturally allow multiple values for the same key, [`MultiDict`](https://multicollections.readthedocs.io/en/latest/api/multicollections/) is the perfect solution:

- **HTTP headers**: Multiple `Accept` or `Set-Cookie` headers
- **URL query parameters**: `?tag=python&tag=web&tag=api`
- **Form data**: Multiple form fields with the same name
- **Configuration files**: Multiple values for the same configuration key

As opposed to the popular [`multidict`](https://github.com/aio-libs/multidict) package, `multicollections`'s [`MultiDict`](https://multicollections.readthedocs.io/en/latest/api/multicollections/) implementation allows both keys and values to be of any type, providing greater flexibility.

## 🔗 Documentation

For detailed documentation, examples, and API reference, visit: https://multicollections.readthedocs.io/
