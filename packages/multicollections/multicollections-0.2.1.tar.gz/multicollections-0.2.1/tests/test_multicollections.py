from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import multidict
import pytest
from multicollections import MultiDict

from .minimalimpl import ListMultiDict

if TYPE_CHECKING:
    from multicollections.abc import MutableMultiMapping


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_empty_creation(cls: type[MutableMultiMapping]) -> None:
    md = cls()
    assert len(md) == 0
    assert list(md) == []
    assert list(md.items()) == []
    assert list(md.values()) == []


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_from_pairs(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict from list of pairs."""
    pairs = [("a", 1), ("b", 2), ("a", 3)]
    md = cls(pairs)  # ty: ignore [too-many-positional-arguments]

    assert len(md) == 3
    assert md["a"] == 1  # First value for duplicate key
    assert md["b"] == 2
    assert list(md.items()) == pairs
    assert list(md) == ["a", "b", "a"]
    assert list(md.values()) == [1, 2, 3]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_from_dict(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict from regular dict."""
    d = {"x": 10, "y": 20, "z": 30}
    md = cls(d)  # ty: ignore [too-many-positional-arguments]

    assert len(md) == 3
    for key, value in d.items():
        assert md[key] == value

    # Order is preserved (dict insertion order is preserved in Python 3.7+)
    assert set(md.items()) == set(d.items())


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_with_kwargs(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict with keyword arguments."""
    md = cls(a=1, b=2, c=3)  # ty: ignore [unknown-argument]

    assert len(md) == 3
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_creation_mixed(cls: type[MutableMultiMapping]) -> None:
    """Test creating MultiDict with both iterable and kwargs."""
    pairs = [("a", 1), ("b", 2)]
    md = cls(pairs, c=3, d=4)  # ty: ignore [too-many-positional-arguments, unknown-argument]

    assert len(md) == 4
    assert md["a"] == 1
    assert md["b"] == 2
    assert md["c"] == 3
    assert md["d"] == 4


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getitem(cls: type[MutableMultiMapping]) -> None:
    """Test __getitem__ behavior."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    assert md["a"] == 1  # First value
    assert md["b"] == 2

    with pytest.raises(KeyError):
        _ = md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_new_key(cls: type[MutableMultiMapping]) -> None:
    """Test __setitem__ with new key."""
    md = cls()
    md["new"] = "value"

    assert len(md) == 1
    assert md["new"] == "value"
    assert list(md.items()) == [("new", "value")]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setitem_existing_key(cls: type[MutableMultiMapping]) -> None:
    """Test __setitem__ with existing key."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    md["a"] = 99

    # Should replace and remove all duplicates
    assert len(md) == 2
    assert md["a"] == 99
    assert list(md.items()) == [("a", 99), ("b", 2)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_add_method(cls: type[MutableMultiMapping]) -> None:
    """Test add() method."""
    md = cls()
    md.add("key", "value1")
    md.add("key", "value2")
    md.add("other", "value3")

    assert len(md) == 3
    assert md["key"] == "value1"  # First value
    assert md["other"] == "value3"
    assert list(md.items()) == [
        ("key", "value1"),
        ("key", "value2"),
        ("other", "value3"),
    ]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_delitem(cls: type[MutableMultiMapping]) -> None:
    """Test __delitem__ behavior."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]
    del md["a"]  # Should remove all 'a' items

    assert len(md) == 2
    assert list(md.items()) == [("b", 2), ("c", 4)]

    with pytest.raises(KeyError):
        del md["missing"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_iteration(cls: type[MutableMultiMapping]) -> None:
    """Test iteration over keys."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    keys = list(md)

    assert keys == ["a", "b", "a"]

    # Test that iteration yields duplicate keys
    key_count = {}
    for key in md:
        key_count[key] = key_count.get(key, 0) + 1

    assert key_count == {"a": 2, "b": 1}


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_values_view(cls: type[MutableMultiMapping]) -> None:
    """Test values() view."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    values = md.values()

    assert len(values) == 3
    assert list(values) == [1, 2, 3]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_values_view_contains(cls: type[MutableMultiMapping]) -> None:
    """Test values() view __contains__ method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    values = md.values()

    # Test containment for existing values
    assert 1 in values
    assert 2 in values
    assert 3 in values

    # Test containment for non-existing values
    assert 4 not in values
    assert 0 not in values

    # Test empty case
    empty_md = cls()
    empty_values = empty_md.values()
    assert 1 not in empty_values


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view(cls: type[MutableMultiMapping]) -> None:
    """Test items() view."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    items = md.items()

    assert len(items) == 3
    assert list(items) == [("a", 1), ("b", 2), ("a", 3)]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_items_view_contains(cls: type[MutableMultiMapping]) -> None:
    """Test items() view __contains__ method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    items = md.items()

    # Test containment for existing items
    assert ("a", 1) in items
    assert ("b", 2) in items
    assert ("a", 3) in items

    # Test containment for non-existing items
    assert ("a", 2) not in items  # Key exists but wrong value
    assert ("c", 1) not in items  # Key doesn't exist
    assert ("b", 1) not in items  # Wrong value for existing key

    # Test different type
    assert None not in items

    # Test empty case
    empty_md = cls()
    empty_items = empty_md.items()
    assert ("a", 1) not in empty_items


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_len(cls: type[MutableMultiMapping]) -> None:
    """Test len() behavior."""
    md = cls()
    assert len(md) == 0

    md.add("a", 1)
    assert len(md) == 1

    md.add("a", 2)  # Duplicate key
    assert len(md) == 2

    md["b"] = 3
    assert len(md) == 3

    del md["a"]  # Removes both 'a' items
    assert len(md) == 1


def test_repr() -> None:
    """Test __repr__ method."""
    # Test empty MultiDict
    md_empty = MultiDict()
    assert repr(md_empty) == "MultiDict([])"

    # Test MultiDict with single item
    md_single = MultiDict([("a", 1)])
    assert repr(md_single) == "MultiDict([('a', 1)])"

    # Test MultiDict with multiple items including duplicates
    md_multi = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    assert repr(md_multi) == "MultiDict([('a', 1), ('b', 2), ('a', 3)])"

    # Test that repr can be used to recreate equivalent objects
    original = MultiDict([("x", "hello"), ("y", 42), ("x", "world")])
    repr_str = repr(original)
    recreated = eval(repr_str)  # noqa: S307
    assert list(original.items()) == list(recreated.items())


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_contains(cls: type[MutableMultiMapping]) -> None:
    """Test __contains__ method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    assert "a" in md
    assert "b" in md
    assert "missing" not in md
    if cls is not multidict.MultiDict or sys.version_info >= (3, 9):
        assert None not in md

    # Test with empty MultiDict
    empty_md = cls()
    assert "any" not in empty_md


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getone_method(cls: type[MutableMultiMapping]) -> None:
    """Test getone() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    # Test getting first value for key with multiple values
    assert md.getone("a") == 1  # First value
    assert md.getone("b") == 2

    # Test with default value
    assert md.getone("missing", "default") == "default"
    assert md.getone("missing", None) is None

    # Test KeyError without default
    with pytest.raises(KeyError):
        md.getone("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_getall_method(cls: type[MutableMultiMapping]) -> None:
    """Test getall() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]

    # Test getting all values for key with multiple values
    assert md.getall("a") == [1, 3]
    assert md.getall("b") == [2]
    assert md.getall("c") == [4]

    # Test with default value
    assert md.getall("missing", []) == []
    assert md.getall("missing", "default") == "default"

    # Test KeyError without default
    with pytest.raises(KeyError):
        md.getall("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_get_method(cls: type[MutableMultiMapping]) -> None:
    """Test get() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    # Test getting first value
    assert md.get("a") == 1  # First value
    assert md.get("b") == 2

    # Test with default (should return default, not raise KeyError)
    assert md.get("missing") is None  # Default None
    assert md.get("missing", "default") == "default"
    assert md.get("missing", 42) == 42


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_keys_view(cls: type[MutableMultiMapping]) -> None:
    """Test keys() view."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    keys = md.keys()

    assert len(keys) == 3
    assert list(keys) == ["a", "b", "a"]

    # Test containment
    assert "a" in keys
    assert "b" in keys
    assert "missing" not in keys

    # Test empty case
    empty_md = cls()
    empty_keys = empty_md.keys()
    assert len(empty_keys) == 0
    assert list(empty_keys) == []


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popone_method(cls: type[MutableMultiMapping]) -> None:
    """Test popone() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]

    # Test popping first value for key with multiple values
    result = md.popone("a")
    assert result == 1
    assert len(md) == 3
    assert md.getall("a") == [3]  # Only second value remains

    # Test popping single value
    result = md.popone("b")
    assert result == 2
    assert len(md) == 2
    with pytest.raises(KeyError):
        md.getall("b")

    # Test with default value
    result = md.popone("missing", "default")
    assert result == "default"
    assert len(md) == 2  # No change

    # Test KeyError without default
    with pytest.raises(KeyError):
        md.popone("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popall_method(cls: type[MutableMultiMapping]) -> None:
    """Test popall() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]

    # Test popping all values for key with multiple values
    result = md.popall("a")
    assert result == [1, 3]
    assert len(md) == 2
    with pytest.raises(KeyError):
        md.getall("a")

    # Test popping single value
    result = md.popall("b")
    assert result == [2]
    assert len(md) == 1

    # Test with default value
    result = md.popall("missing", [])
    assert result == []
    assert len(md) == 1  # No change

    result = md.popall("missing", "default")
    assert result == "default"

    # Test KeyError without default
    with pytest.raises(KeyError):
        md.popall("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_pop_method(cls: type[MutableMultiMapping]) -> None:
    """Test pop() method (alias for popone)."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    # Test that pop behaves like popone
    result = md.pop("a")
    assert result == 1
    assert md.getall("a") == [3]

    # Test with default
    result = md.pop("missing", "default")
    assert result == "default"

    # Test KeyError without default
    with pytest.raises(KeyError):
        md.pop("missing")


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_popitem_method(cls: type[MutableMultiMapping]) -> None:
    """Test popitem() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]
    original_len = len(md)

    # Test popping first item (value may differ between implementations)
    key, value = md.popitem()
    assert key == "a"
    assert value in [1, 3]  # Different implementations may return different values
    assert len(md) == original_len - 1

    # Test popping from single-item dict
    single_md = cls([("x", 42)])  # ty: ignore [too-many-positional-arguments]
    key, value = single_md.popitem()
    assert key == "x"
    assert value == 42
    assert len(single_md) == 0

    # Test empty MultiDict
    empty_md = cls()
    with pytest.raises(
        (StopIteration, KeyError)
    ):  # Different implementations may raise different errors
        empty_md.popitem()


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_setdefault_method(cls: type[MutableMultiMapping]) -> None:
    """Test setdefault() method."""
    md = cls([("a", 1), ("b", 2)])  # ty: ignore [too-many-positional-arguments]

    # Test existing key (should return existing value, not set)
    result = md.setdefault("a", 999)
    assert result == 1  # Original value
    assert md["a"] == 1  # Unchanged
    assert len(md) == 2  # No new items added

    # Test new key (should set and return default)
    result = md.setdefault("c", 3)
    assert result == 3
    assert md["c"] == 3
    assert len(md) == 3

    # Test with None default
    result = md.setdefault("d", None)
    assert result is None
    assert md["d"] is None
    assert len(md) == 4

    # Test default None (implicit)
    if cls is not multidict.MultiDict or sys.version_info >= (3, 9):
        # https://github.com/aio-libs/multidict/pull/1160
        result = md.setdefault("e")
        assert result is None
        assert md["e"] is None
        assert len(md) == 5


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_clear_method(cls: type[MutableMultiMapping]) -> None:
    """Test clear() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]

    assert len(md) == 4
    md.clear()

    assert len(md) == 0
    assert list(md.items()) == []
    assert list(md.keys()) == []
    assert list(md.values()) == []

    # Test clearing empty MultiDict
    empty_md = cls()
    empty_md.clear()
    assert len(empty_md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_extend_method(cls: type[MutableMultiMapping]) -> None:
    """Test extend() method."""
    md = cls([("a", 1)])  # ty: ignore [too-many-positional-arguments]

    # Test extending with pairs
    md.extend([("b", 2), ("a", 3), ("c", 4)])
    assert len(md) == 4
    assert list(md.items()) == [("a", 1), ("b", 2), ("a", 3), ("c", 4)]

    # Test extending with dict
    md2 = cls([("x", 10)])  # ty: ignore [too-many-positional-arguments]
    md2.extend({"y": 20, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 10
    assert md2["y"] == 20
    assert md2["z"] == 30

    # Test extending with another MultiDict
    md3 = cls([("m", 100)])  # ty: ignore [too-many-positional-arguments]
    other_md = cls([("n", 200), ("m", 300)])  # ty: ignore [too-many-positional-arguments]
    md3.extend(other_md)
    assert len(md3) == 3
    assert list(md3.items()) == [("m", 100), ("n", 200), ("m", 300)]

    # Test extending with kwargs
    md4 = cls([("a", 1)])  # ty: ignore [too-many-positional-arguments]
    md4.extend(b=2, c=3)
    assert len(md4) == 3
    assert md4["a"] == 1
    assert md4["b"] == 2
    assert md4["c"] == 3

    # Test extending with both iterable and kwargs
    md5 = cls()
    md5.extend([("x", 1)], y=2, z=3)
    assert len(md5) == 3
    assert md5["x"] == 1
    assert md5["y"] == 2
    assert md5["z"] == 3


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_merge_method(cls: type[MutableMultiMapping]) -> None:
    """Test merge() method."""
    if cls is multidict.MultiDict and sys.version_info < (3, 9):
        return

    md = cls([("a", 1), ("b", 2)])  # ty: ignore [too-many-positional-arguments]

    # Test merging with pairs (should not replace existing keys)
    md.merge([("a", 999), ("c", 3), ("d", 4)])
    assert len(md) == 4
    assert md["a"] == 1  # Original value preserved
    assert md["b"] == 2
    assert md["c"] == 3  # New key added
    assert md["d"] == 4  # New key added

    # Test merging with dict
    md2 = cls([("x", 10), ("y", 20)])  # ty: ignore [too-many-positional-arguments]
    md2.merge({"x": 999, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 10  # Original value preserved
    assert md2["y"] == 20
    assert md2["z"] == 30  # New key added

    # Test merging with kwargs
    md3 = cls([("a", 1)])  # ty: ignore [too-many-positional-arguments]
    md3.merge(a=999, b=2, c=3)
    assert len(md3) == 3
    assert md3["a"] == 1  # Original value preserved
    assert md3["b"] == 2  # New key added
    assert md3["c"] == 3  # New key added


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_update_method(cls: type[MutableMultiMapping]) -> None:
    """Test update() method."""
    md = cls([("a", 1), ("b", 2), ("a", 3)])  # ty: ignore [too-many-positional-arguments]

    # Test updating with pairs (should replace existing keys)
    md.update([("a", 999), ("c", 4), ("a", 5)])
    assert len(md) == 4
    assert md["a"] == 999  # Replaced (duplicates removed)
    assert md["b"] == 2  # Unchanged
    assert md["c"] == 4  # New key added
    assert md.getall("a") == [999, 5]  # Both 'a' values present

    # Test updating with dict
    md2 = cls([("x", 10), ("y", 20)])  # ty: ignore [too-many-positional-arguments]
    md2.update({"x": 999, "z": 30})
    assert len(md2) == 3
    assert md2["x"] == 999  # Replaced
    assert md2["y"] == 20  # Unchanged
    assert md2["z"] == 30  # New key added

    # Test updating with kwargs
    md3 = cls([("a", 1), ("b", 2)])  # ty: ignore [too-many-positional-arguments]
    md3.update(a=999, c=3)
    assert len(md3) == 3
    assert md3["a"] == 999  # Replaced
    assert md3["b"] == 2  # Unchanged
    assert md3["c"] == 3  # New key added

    # Test updating with args and kwargs
    md4 = cls([("a", 1), ("b", 2)])  # ty: ignore [too-many-positional-arguments]
    md4.update([("a", 999), ("c", 3)], a=4)
    assert len(md4) == 4
    assert md4["a"] == 999  # Replaced
    assert md4["b"] == 2  # Unchanged
    assert md4["c"] == 3  # New key added
    assert md4.getall("a") == [999, 4]  # Both 'a' values present


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_none_values(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with None values."""
    md = cls()

    # Test adding None values
    md.add("key", None)
    md.add("key", "value")
    md.add("other", None)

    assert len(md) == 3
    assert md["key"] is None  # First value
    assert md.getall("key") == [None, "value"]
    assert md["other"] is None

    # Test setting None value
    md["new"] = None
    assert md["new"] is None

    # Test None in contains
    assert "key" in md
    assert "other" in md
    assert "new" in md


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_empty_operations(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with empty MultiDict operations."""
    md = cls()

    # Test operations on empty dict
    assert len(md) == 0
    assert list(md) == []
    assert list(md.items()) == []
    assert list(md.values()) == []
    assert list(md.keys()) == []

    # Test get operations on empty dict
    with pytest.raises(KeyError):
        _ = md["missing"]

    with pytest.raises(KeyError):
        md.getone("missing")

    with pytest.raises(KeyError):
        md.getall("missing")

    assert md.get("missing") is None
    assert md.get("missing", "default") == "default"

    # Test pop operations on empty dict
    with pytest.raises(KeyError):
        md.popone("missing")

    with pytest.raises(KeyError):
        md.popall("missing")

    assert md.popone("missing", "default") == "default"
    assert md.popall("missing", []) == []

    # Test clear on empty dict
    md.clear()
    assert len(md) == 0


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_single_item_operations(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with single item operations."""
    md = cls([("single", "value")])  # ty: ignore [too-many-positional-arguments]

    # Test that single item behaves correctly
    assert len(md) == 1
    assert md["single"] == "value"
    assert md.getone("single") == "value"
    assert md.getall("single") == ["value"]

    # Test popping the only item
    result = md.popone("single")
    assert result == "value"
    assert len(md) == 0

    # Test operations after becoming empty
    with pytest.raises(KeyError):
        _ = md["single"]


@pytest.mark.parametrize("cls", [MultiDict, ListMultiDict, multidict.MultiDict])
def test_edge_cases_duplicate_handling(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with many duplicate keys."""
    md = cls()

    # Add many values for same key
    for i in range(5):
        md.add("key", i)

    assert len(md) == 5
    assert md["key"] == 0  # First value
    assert md.getall("key") == [0, 1, 2, 3, 4]

    # Test popone removes first
    result = md.popone("key")
    assert result == 0
    assert md.getall("key") == [1, 2, 3, 4]

    # Test popall removes all remaining
    result = md.popall("key")
    assert result == [1, 2, 3, 4]
    assert len(md) == 0

    # Test setitem replaces all
    md.add("key", 1)
    md.add("key", 2)
    md.add("key", 3)
    md["key"] = 999
    assert len(md) == 1
    assert md["key"] == 999


@pytest.mark.parametrize(
    "cls", [MultiDict, ListMultiDict]
)  # multidict has type restrictions
def test_edge_cases_mixed_types(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with mixed key and value types."""
    md = cls()

    # Test various key types
    md.add("string", "value1")
    md.add(42, "value2")
    md.add(("tuple", "key"), "value3")
    md.add(None, "value4")

    assert len(md) == 4
    assert md["string"] == "value1"
    assert md[42] == "value2"
    assert md[("tuple", "key")] == "value3"
    assert md[None] == "value4"

    # Test various value types
    md2 = cls()
    md2.add("key", "string")
    md2.add("key", 42)
    md2.add("key", [1, 2, 3])
    md2.add("key", {"nested": "dict"})

    assert len(md2) == 4
    assert md2.getall("key") == ["string", 42, [1, 2, 3], {"nested": "dict"}]


@pytest.mark.parametrize("cls", [multidict.MultiDict])
def test_edge_cases_multidict_string_keys(cls: type[MutableMultiMapping]) -> None:
    """Test edge cases with multidict string key restriction."""
    md = cls()

    # Test that multidict only accepts string keys
    md.add("string", "value1")
    assert md["string"] == "value1"

    # Test that non-string keys raise TypeError
    with pytest.raises(TypeError):
        md.add(42, "value2")

    with pytest.raises(TypeError):
        md.add(None, "value3")


def test_edge_cases_multidict_specific() -> None:
    """Test edge cases specific to our MultiDict implementation."""
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])

    # Test internal consistency after operations
    assert len(md._items) == 3  # noqa: SLF001
    assert len(md._key_indices) == 2  # noqa: SLF001
    assert md._key_indices["a"] == [0, 2]  # noqa: SLF001
    assert md._key_indices["b"] == [1]  # noqa: SLF001

    # Test that internal state is maintained after deletion
    del md["a"]
    assert len(md._items) == 1  # noqa: SLF001
    assert len(md._key_indices) == 1  # noqa: SLF001
    assert "a" not in md._key_indices  # noqa: SLF001
    assert md._key_indices["b"] == [0]  # Index should be updated  # noqa: SLF001

    # Test that internal state is maintained after setitem with duplicates
    md.add("c", 1)
    md.add("c", 2)
    md.add("c", 3)
    md["c"] = 999

    assert len(md._items) == 2  # b and c  # noqa: SLF001
    assert md._key_indices["c"] == [1]  # Only one index for c  # noqa: SLF001


@pytest.mark.parametrize("cls", [MultiDict, multidict.MultiDict])
def test_copy_method(cls: type[MultiDict | multidict.MultiDict]) -> None:
    """Test copy() method."""
    # Test copying empty MultiDict
    empty_md = cls()
    empty_copy = empty_md.copy()
    assert len(empty_copy) == 0
    assert list(empty_copy.items()) == []
    assert empty_md is not empty_copy  # Different objects

    # Test copying MultiDict with single item
    single_md = cls([("a", 1)])  # ty: ignore [too-many-positional-arguments]
    single_copy = single_md.copy()
    assert len(single_copy) == 1
    assert list(single_copy.items()) == [("a", 1)]
    assert single_md is not single_copy  # Different objects

    # Test copying MultiDict with multiple items including duplicates
    md = cls([("a", 1), ("b", 2), ("a", 3), ("c", 4)])  # ty: ignore [too-many-positional-arguments]
    copied = md.copy()

    # Test that content is identical
    assert len(copied) == len(md)
    assert list(copied.items()) == list(md.items())
    assert list(copied.keys()) == list(md.keys())
    assert list(copied.values()) == list(md.values())

    # Test that duplicate keys are preserved
    assert copied.getall("a") == md.getall("a") == [1, 3]

    # Test that they are different objects
    assert md is not copied

    # Test that changes to original don't affect copy
    md.add("d", 5)
    assert len(md) == 5
    assert len(copied) == 4
    assert "d" not in copied

    # Test that changes to copy don't affect original
    copied.add("e", 6)
    assert len(copied) == 5
    assert len(md) == 5
    assert "e" not in md

    # Test that copy() creates a shallow copy (values are not deep copied)
    value_list = [1, 2, 3]
    md_with_mutable = cls([("key", value_list)])  # ty: ignore [too-many-positional-arguments]
    copied_with_mutable = md_with_mutable.copy()

    # The list should be the same object (shallow copy)
    assert copied_with_mutable["key"] is value_list
    assert md_with_mutable["key"] is value_list


# Additional tests for uncovered lines
def test_empty_init_no_rebuild() -> None:
    """Test that empty MultiDict initialization doesn't call _rebuild_indices."""
    # This tests line 53-54: if self._items: and the else branch
    md = MultiDict()
    assert len(md._items) == 0  # noqa: SLF001
    assert len(md._key_indices) == 0  # noqa: SLF001


def test_update_with_empty_input() -> None:
    """Test update with empty input to cover early return."""
    # This tests line 214-215: if not all_items: return
    md = MultiDict([("a", 1)])
    md.update()  # Empty input
    assert len(md) == 1
    assert md["a"] == 1

    md.update([])  # Empty list
    assert len(md) == 1
    assert md["a"] == 1


def test_merge_with_empty_input() -> None:
    """Test merge with empty input to cover early return."""
    # This tests line 253-254: if not new_items: return
    md = MultiDict([("a", 1)])
    md.merge()  # Empty input
    assert len(md) == 1
    assert md["a"] == 1

    md.merge([])  # Empty list
    assert len(md) == 1
    assert md["a"] == 1


def test_extend_with_empty_input() -> None:
    """Test extend with empty input to cover early return."""
    # This tests line 281-282: if not new_items: return
    md = MultiDict([("a", 1)])
    md.extend()  # Empty input
    assert len(md) == 1
    assert md["a"] == 1

    md.extend([])  # Empty list
    assert len(md) == 1
    assert md["a"] == 1


def test_merge_all_existing_keys() -> None:
    """Test merge where all keys already exist."""
    # This tests the case where new_items becomes empty after filtering
    md = MultiDict([("a", 1), ("b", 2)])
    md.merge([("a", 999), ("b", 888)])  # All keys exist, should be filtered out
    assert len(md) == 2
    assert md["a"] == 1  # Should remain unchanged
    assert md["b"] == 2  # Should remain unchanged


def test_merge_existing_key_in_indices() -> None:
    """Test merge with key that already exists in indices."""
    # This tests line 262-263: if key not in self._key_indices
    md = MultiDict([("a", 1)])
    existing_keys = set(md._key_indices.keys())  # noqa: SLF001
    assert "a" in existing_keys

    # Since merge filters out existing keys, we test the else branch
    # by adding a new key
    md.merge([("b", 2)])
    assert "b" in md._key_indices  # noqa: SLF001
    assert md["b"] == 2


def test_extend_existing_key_in_indices() -> None:
    """Test extend with key that already exists in indices."""
    # This tests line 290-291: if key not in self._key_indices
    md = MultiDict([("a", 1)])

    # Extend with existing key - should add to existing key's index list
    md.extend([("a", 2)])
    assert len(md._key_indices["a"]) == 2  # noqa: SLF001
    assert md._key_indices["a"] == [0, 1]  # noqa: SLF001


def test_update_only_updates_no_additions() -> None:
    """Test update with only existing keys (no new keys)."""
    # This tests line 228-229: if additions: branch when additions is empty
    md = MultiDict([("a", 1), ("b", 2)])
    md.update([("a", 999), ("b", 888)])  # Only existing keys

    assert len(md) == 2
    assert md["a"] == 999
    assert md["b"] == 888


def test_update_only_additions_no_updates() -> None:
    """Test update with only new keys (no existing keys)."""
    # This tests line 224-225: if updates_by_key: branch when updates_by_key is empty
    md = MultiDict([("a", 1)])
    md.update([("b", 2), ("c", 3)])  # Only new keys

    assert len(md) == 3
    assert md["a"] == 1  # Original unchanged
    assert md["b"] == 2
    assert md["c"] == 3


def test_init_with_no_items_and_no_kwargs() -> None:
    """Test initialization with completely empty input."""
    # This tests the case where _items remains empty after all initialization
    md = MultiDict(())  # Empty tuple
    assert len(md._items) == 0  # noqa: SLF001
    assert len(md._key_indices) == 0  # noqa: SLF001


def test_collect_update_items_edge_cases() -> None:
    """Test _collect_update_items helper method edge cases."""
    md = MultiDict([("a", 1)])

    # Test with empty all_items
    updates, additions = md._collect_update_items([], set())  # noqa: SLF001
    assert updates == {}
    assert additions == []

    # Test with all new keys
    updates, additions = md._collect_update_items([("b", 2), ("c", 3)], set())  # noqa: SLF001
    assert updates == {}
    assert additions == [("b", 2), ("c", 3)]

    # Test with all existing keys
    updates, additions = md._collect_update_items([("a", 999)], {"a"})  # noqa: SLF001
    assert updates == {"a": [999]}
    assert additions == []


def test_process_updates_edge_cases() -> None:
    """Test _process_updates helper method edge cases."""
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    original_len = len(md)

    # Test with empty updates
    md._process_updates({})  # noqa: SLF001
    assert len(md) == original_len  # Should remain unchanged

    # Test with single key update - need to rebuild indices after _process_updates
    md = MultiDict([("a", 1), ("b", 2), ("a", 3)])
    md._process_updates({"a": [999]})  # noqa: SLF001
    md._rebuild_indices()  # _process_updates doesn't rebuild indices  # noqa: SLF001
    assert md["a"] == 999
    assert md["b"] == 2
