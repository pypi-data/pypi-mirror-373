"""Fully generic `MultiDict` class."""

from __future__ import annotations

import itertools
import sys
from typing import TypeVar

if sys.version_info >= (3, 9):
    from collections.abc import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )
else:
    from typing import (
        Iterable,
        Iterator,
        Mapping,
        Sequence,
    )

from ._util import override
from .abc import MutableMultiMapping, with_default

_K = TypeVar("_K")
_V = TypeVar("_V")


class MultiDict(MutableMultiMapping[_K, _V]):
    """A fully generic dictionary that allows multiple values with the same key.

    Preserves insertion order.
    """

    def __init__(
        self, iterable: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (), **kwargs: _V
    ) -> None:
        """Create a MultiDict."""
        self._items: list[tuple[_K, _V]] = []
        self._key_indices: dict[_K, list[int]] = {}

        # Batch initialization: collect all items first, then build indices once
        if isinstance(iterable, Mapping):
            self._items.extend((key, value) for key, value in iterable.items())
        else:
            self._items.extend((key, value) for key, value in iterable)

        # Add kwargs items
        self._items.extend((key, value) for key, value in kwargs.items())

        # Build indices in one pass for better performance
        if self._items:
            self._rebuild_indices()

    @override
    @with_default
    def getall(self, key: _K) -> list[_V]:
        """Get all values for a key.

        Raises a `KeyError` if the key is not found and no default is provided.
        """
        ret = [self._items[i][1] for i in self._key_indices.get(key, [])]
        if not ret:
            raise KeyError(key)
        return ret

    @override
    def __setitem__(self, key: _K, value: _V) -> None:
        """Set the value for a key.

        Replaces the first value for a key if it exists; otherwise, it adds a new item.
        Any other items with the same key are removed.
        """
        if key in self._key_indices:
            # Key exists, replace first occurrence and remove others
            indices = self._key_indices[key]
            first_index = indices[0]

            # Update the first occurrence
            self._items[first_index] = (key, value)

            if len(indices) > 1:
                # Remove duplicates efficiently by marking items as None and filtering
                for idx in indices[1:]:
                    self._items[idx] = None

                # Filter out None items and rebuild indices
                self._items = [item for item in self._items if item is not None]
                self._rebuild_indices()
        else:
            # Key doesn't exist, add it
            self.add(key, value)

    def _rebuild_indices(self) -> None:
        """Rebuild the key indices after items list has been modified."""
        self._key_indices = {}
        for i, (key, _) in enumerate(self._items):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    @override
    def add(self, key: _K, value: _V) -> None:
        """Add a new value for a key."""
        index = len(self._items)
        self._items.append((key, value))
        if key not in self._key_indices:
            self._key_indices[key] = []
        self._key_indices[key].append(index)

    @override
    @with_default
    def popone(self, key: _K) -> _V:
        """Remove and return the first value for a key."""
        if key not in self._key_indices:
            raise KeyError(key)

        indices = self._key_indices[key]
        first_index = indices[0]
        value = self._items[first_index][1]

        # Mark the first item for removal
        self._items[first_index] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

        return value

    @override
    def __delitem__(self, key: _K) -> None:
        """Remove all values for a key.

        Raises a `KeyError` if the key is not found.
        """
        if key not in self._key_indices:
            raise KeyError(key)

        # Mark items for removal
        indices_to_remove = self._key_indices[key]
        for idx in indices_to_remove:
            self._items[idx] = None

        # Filter out None items and rebuild indices
        self._items = [item for item in self._items if item is not None]
        self._rebuild_indices()

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys, in insertion order.

        Keys with multiple values will be yielded multiple times.
        """
        return (k for k, _ in self._items)

    @override
    def __len__(self) -> int:
        """Return the total number of items."""
        return len(self._items)

    @override
    def clear(self) -> None:
        """Remove all items from the multi-mapping."""
        self._items.clear()
        self._key_indices.clear()

    def _collect_update_items(
        self,
        all_items: list[tuple[_K, _V]],
        existing_keys: set[_K],
    ) -> tuple[dict[_K, list[_V]], list[tuple[_K, _V]]]:
        """Separate items into updates and additions."""
        updates_by_key = {}  # key -> list of values to replace with
        additions = []  # list of (key, value) for new keys

        for key, value in all_items:
            if key in existing_keys:
                if key not in updates_by_key:
                    updates_by_key[key] = []
                updates_by_key[key].append(value)
            else:
                additions.append((key, value))

        return updates_by_key, additions

    def _process_updates(self, updates_by_key: dict[_K, list[_V]]) -> None:
        """Process updates efficiently by batch removing and adding."""
        # Mark items for removal that need to be replaced
        items_to_remove = set()
        for key in updates_by_key:
            items_to_remove.update(self._key_indices[key])

        # Mark items for removal
        for idx in items_to_remove:
            self._items[idx] = None

        # Filter out None items
        self._items = [item for item in self._items if item is not None]

        # Add updated items (all values for each key)
        for key, values in updates_by_key.items():
            for value in values:
                self._items.append((key, value))

    @override
    def update(
        self,
        other: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (),
        **kwargs: _V,
    ) -> None:
        """Update the multi-mapping with items from another object.

        This replaces existing values for keys found in the other object.
        This is optimized for batch operations.
        """
        # Collect all items first
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        all_items = list(items)

        if not all_items:
            return

        # Get existing keys once for efficiency
        existing_keys = set(self._key_indices.keys())

        # Separate items into updates and additions
        updates_by_key, additions = self._collect_update_items(all_items, existing_keys)

        # Process updates efficiently
        if updates_by_key:
            self._process_updates(updates_by_key)

        # Add new items
        if additions:
            self._items.extend(additions)

        # Rebuild indices once at the end
        if updates_by_key or additions:
            self._rebuild_indices()

    @override
    def merge(
        self,
        other: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (),
        **kwargs: _V,
    ) -> None:
        """Merge another object into the multi-mapping.

        Keys from `other` that already exist in the multi-mapping will not be added.
        This is optimized for batch operations.
        """
        # Get existing keys once for efficiency
        existing_keys = set(self._key_indices.keys())

        # Collect all items and filter out existing keys
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        new_items = [(key, value) for key, value in items if key not in existing_keys]

        if not new_items:
            return

        # Add all items to the list at once
        start_index = len(self._items)
        self._items.extend(new_items)

        # Update indices incrementally for better performance
        for i, (key, _) in enumerate(new_items, start_index):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    @override
    def extend(
        self,
        other: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (),
        **kwargs: _V,
    ) -> None:
        """Extend the multi-mapping with items from another object.

        This is optimized for batch operations to avoid rebuilding indices
        multiple times.
        """
        # Collect all new items first
        items = other.items() if isinstance(other, Mapping) else other
        items = itertools.chain(items, kwargs.items())
        new_items = list(items)

        if not new_items:
            return

        # Add all items to the list at once
        start_index = len(self._items)
        self._items.extend(new_items)

        # Update indices incrementally for better performance
        for i, (key, _) in enumerate(new_items, start_index):
            if key not in self._key_indices:
                self._key_indices[key] = []
            self._key_indices[key].append(i)

    def copy(self) -> MultiDict[_K, _V]:
        """Return a shallow copy of the MultiDict."""
        new_md = MultiDict.__new__(MultiDict)
        new_md._items = self._items.copy()  # noqa: SLF001
        new_md._key_indices = {k: v.copy() for k, v in self._key_indices.items()}  # noqa: SLF001
        return new_md

    def __repr__(self) -> str:
        """Return a string representation of the MultiDict."""
        return f"{self.__class__.__name__}({list(self._items)!r})"
