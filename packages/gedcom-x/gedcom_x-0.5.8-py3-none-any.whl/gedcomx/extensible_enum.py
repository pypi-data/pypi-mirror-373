from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Iterator, Literal

"""
======================================================================
 Project: Gedcom-X
 File:    ExtensibleEnum.py
 Author:  David J. Cartwright
 Purpose: Create a class that can act like an enum but be extended by the user at runtime.

 Created: 2025-08-25
 Updated:
   - YYYY-MM-DD: <change description>
   
======================================================================
"""

@dataclass(frozen=True, slots=True)
class _EnumItem:
    """
    A single registered member of an :class:`ExtensibleEnum`.

    Each `_EnumItem` represents one (name, value) pair that belongs
    to a particular `ExtensibleEnum` subclass. Items are immutable
    once created.

    Attributes
    ----------
    owner : type
        The subclass of :class:`ExtensibleEnum` that owns this member
        (e.g., `Color`).
    name : str
        The symbolic name of the member (e.g., `"RED"`).
    value : Any
        The underlying value associated with the member (e.g., `"r"`).

    Notes
    -----
    - Equality is determined by object identity (not overridden).
    - Instances are hashable by default since the dataclass is frozen.
    - The `__repr__` and `__str__` provide user-friendly string forms.

    Examples
    --------
    >>> class Color(ExtensibleEnum): ...
    >>> red = Color.register("RED", "r")
    >>> repr(red)
    'Color.RED'
    >>> str(red)
    'RED'
    >>> red.value
    'r'
    """
    owner: type
    name: str
    value: Any
    def __repr__(self) -> str:  # print(...) shows "Color.RED"
        return f"{self.owner.__name__}.{self.name}"
    def __str__(self) -> str:
        return self.name

class _ExtEnumMeta(type):
    def __iter__(cls) -> Iterator[_EnumItem]:
        return iter(cls._members.values())
    def __contains__(cls, item: object) -> bool:
        return item in cls._members.values()
    # Support Color('RED') / Color(2)
    def __call__(cls, arg: Any, /, *, by: Literal["auto","name","value"]="auto") -> _EnumItem:
        if isinstance(arg, _EnumItem):
            if arg.owner is cls:
                return arg
            raise TypeError(f"{arg!r} is not a member of {cls.__name__}")
        if by == "name":
            return cls.get(str(arg))
        if by == "value":
            return cls.from_value(arg)
        if isinstance(arg, str) and arg in cls._members:
            return cls.get(arg)
        return cls.from_value(arg)

class ExtensibleEnum(metaclass=_ExtEnumMeta):
    """
    A lightweight, **runtime-extensible**, enum-like base class.

    Subclass this to create an enum whose members can be registered at runtime.
    Registered members are exposed as class attributes (e.g., `Color.RED`) and
    can be retrieved by name (`Color.get("RED")`) or by value
    (`Color.from_value("r")`). Square-bracket lookup (`Color["RED"]`) is also
    supported via ``__class_getitem__``.

    This is useful when:
      - The full set of enum values is not known until runtime (plugins, config).
      - You need attribute-style access (`Color.RED`) but want to add members
        dynamically and/or validate uniqueness of names/values.

    Notes
    -----
    - **Uniqueness:** Names and values are unique within a subclass.
    - **Per-subclass registry:** Each subclass has its own member registry.
    - **Thread safety:** Registration is **not** thread-safe. If multiple threads
      may register members, wrap `register()` calls in your own lock.
    - **Immutability:** Once registered, a member’s `name` and `value` are fixed.
      Re-registering the same `name` with the *same* `value` returns the existing
      item; a different value raises an error.

    Examples
    --------
    Define an extensible enum and register members:

    >>> class Color(ExtensibleEnum):
    ...     pass
    ...
    >>> Color.register("RED", "r")
    _EnumItem(owner=Color, name='RED', value='r')
    >>> Color.register("GREEN", "g")
    _EnumItem(owner=Color, name='GREEN', value='g')

    Access members:

    >>> Color.RED is Color.get("RED")
    True
    >>> Color["GREEN"] is Color.get("GREEN")
    True
    >>> Color.from_value("g") is Color.GREEN
    True
    >>> Color.names()
    ['RED', 'GREEN']

    Error cases:

    >>> Color.register("RED", "different")  # doctest: +IGNORE_EXCEPTION_DETAIL
    ValueError: name 'RED' already used with different value 'r'
    >>> Color.get("BLUE")                    # doctest: +IGNORE_EXCEPTION_DETAIL
    KeyError: Color has no member named 'BLUE'
    >>> Color.from_value("b")                # doctest: +IGNORE_EXCEPTION_DETAIL
    KeyError: Color has no member with value 'b'
    """
    """Runtime-extensible enum-like base."""
    _members: Dict[str, _EnumItem] = {}

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        cls._members = {}  # fresh registry per subclass

    @classmethod
    def __class_getitem__(cls, key: str) -> _EnumItem:  # Color['RED']
        return cls.get(key)

    @classmethod
    def register(cls, name: str, value: Any) -> _EnumItem:
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError("name must be a valid identifier")
        if name in cls._members:
            item = cls._members[name]
            if item.value != value:
                raise ValueError(f"name {name!r} already used with different value {item.value!r}")
            return item
        if any(m.value == value for m in cls._members.values()):
            raise ValueError(f"value {value!r} already used")
        item = _EnumItem(owner=cls, name=name, value=value)
        cls._members[name] = item
        setattr(cls, name, item)  # enables Color.RED attribute
        return item

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._members.keys())

    @classmethod
    def get(cls, name: str) -> _EnumItem:
        try:
            return cls._members[name]
        except KeyError as e:
            raise KeyError(f"{cls.__name__} has no member named {name!r}") from e

    @classmethod
    def from_value(cls, value: Any) -> _EnumItem:
        for m in cls._members.values():
            if m.value == value:
                return m
        raise KeyError(f"{cls.__name__} has no member with value {value!r}")

