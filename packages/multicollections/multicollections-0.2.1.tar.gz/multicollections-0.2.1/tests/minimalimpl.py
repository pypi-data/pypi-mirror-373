from __future__ import annotations

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

from multicollections._util import override
from multicollections.abc import MutableMultiMapping, with_default

_K = TypeVar("_K")
_V = TypeVar("_V")


class ListMultiDict(MutableMultiMapping[_K, _V]):
    def __init__(
        self, iterable: Mapping[_K, _V] | Iterable[Sequence[_K | _V]] = (), **kwargs: _V
    ) -> None:
        self._items: list[tuple[_K, _V]] = []
        if isinstance(iterable, Mapping):
            for key, value in iterable.items():
                self._items.append((key, value))
        else:
            for key, value in iterable:
                self._items.append((key, value))
        for key, value in kwargs.items():
            self._items.append((key, value))

    @override
    @with_default
    def getall(self, key: _K) -> list[_V]:
        ret = [v for k, v in self._items if k == key]
        if not ret:
            raise KeyError(key)
        return ret

    @override
    def __setitem__(self, key: _K, value: _V) -> None:
        replaced: int | None = None
        for i, (k, _) in enumerate(self._items):
            if k == key:
                self._items[i] = (key, value)
                replaced = i
                break

        if replaced is not None:
            self._items = [
                (k, v)
                for i, (k, v) in enumerate(self._items)
                if i == replaced or k != key
            ]
        else:
            self._items.append((key, value))

    @override
    def add(self, key: _K, value: _V) -> None:
        self._items.append((key, value))

    @override
    @with_default
    def popone(self, key: _K) -> _V:
        for i, (k, v) in enumerate(self._items):
            if k == key:
                del self._items[i]
                return v
        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[_K]:
        return (k for k, _ in self._items)

    @override
    def __len__(self) -> int:
        return len(self._items)
