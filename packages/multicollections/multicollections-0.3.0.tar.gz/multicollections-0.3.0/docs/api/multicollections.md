# MultiDict

The main `multicollections` module provides the `MultiDict` class, a fully generic dictionary that allows multiple values with the same key while preserving insertion order.

## Overview

`MultiDict` is a mutable multi-mapping that inherits from `multicollections.abc.MutableMultiMapping`. It provides all the functionality you'd expect from a dictionary, plus the ability to store multiple values for the same key.

## Key Features

- **Multiple values per key**: Store multiple values for the same key
- **Insertion order preservation**: Keys and values maintain their insertion order
- **Dictionary-like interface**: Familiar API similar to built-in `dict`
- **Abstract base class compliance**: Inherits from `MutableMultiMapping`

## Quick Start

```python
from multicollections import MultiDict

# Create a MultiDict
md = MultiDict([('a', 1), ('b', 2), ('a', 3)])

# Access first value for a key
print(md['a'])  # 1

# Add more values
md.add('b', 4)

# Set a single value (replaces all existing values)
md['a'] = 999

# Iterate over all key-value pairs
for key, value in md.items():
    print(f"{key}: {value}")
```

## API Reference

::: multicollections