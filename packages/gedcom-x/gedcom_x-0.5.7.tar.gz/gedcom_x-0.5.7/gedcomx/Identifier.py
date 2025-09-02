
from enum import Enum

from typing import List, Optional, Dict, Any

from collections.abc import Iterator
import json
from .Resource import Resource
from .URI import URI
from .ExtensibleEnum import ExtensibleEnum

import secrets
import string
import json

def make_uid(length: int = 10, alphabet: str = string.ascii_letters + string.digits) -> str:
    """
    Generate a cryptographically secure alphanumeric UID.

    Args:
        length: Number of characters to generate (must be > 0).
        alphabet: Characters to choose from (default: A-Za-z0-9).

    Returns:
        A random string of `length` characters from `alphabet`.
    """
    if length <= 0:
        raise ValueError("length must be > 0")
    return ''.join(secrets.choice(alphabet) for _ in range(length)).upper()

class IdentifierType(ExtensibleEnum):
    pass

"""Enumeration of identifier types."""
IdentifierType.register("Primary", "http://gedcomx.org/Primary")
IdentifierType.register("Authority", "http://gedcomx.org/Authority")            
IdentifierType.register("Deprecated", "http://gedcomx.org/Deprecated")
IdentifierType.register("Persistent", "http://gedcomx.org/Persistent")
IdentifierType.register("External", "https://gedcom.io/terms/v7/EXID")
IdentifierType.register("Other", "user provided")
    
class Identifier:
    identifier = 'http://gedcomx.org/v1/Identifier'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[List[URI]], type: Optional[IdentifierType] = IdentifierType.Primary) -> None: # type: ignore
        if not isinstance(value,list):
            value = [value] if value else []
        self.type = type
        self.values = value if value else []
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.values:
            type_as_dict["value"] = list(self.values)  # or [v for v in self.values]
        if self.type:
            type_as_dict["type"] = getattr(self.type, "value", self.type)  # type: ignore[attr-defined]

        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'Identifier | None':
        """
        Construct an Identifier from a dict parsed from JSON.
        """
        
        for key in data.keys():
            type = key
            value = data[key]
        uri_obj: Optional[Resource] = None
        # TODO DO THIS BETTER

        # Parse type
        raw_type = data.get('type')
        if raw_type is None:
            return None
        id_type: Optional[IdentifierType] = IdentifierType(raw_type) if raw_type else None
        return cls(value=value, type=id_type)

class IdentifierList:
    def __init__(self) -> None:
        # maps identifier-type (e.g., str or IdentifierType.value) -> list of values
        self.identifiers: dict[str, list] = {}

    # -------------------- hashing/uniqueness helpers --------------------
    def make_hashable(self, obj):
        """Convert any object into a hashable representation."""
        if isinstance(obj, dict):
            return tuple(sorted((k, self.make_hashable(v)) for k, v in obj.items()))
        elif isinstance(obj, (list, set, tuple)):
            return tuple(self.make_hashable(i) for i in obj)
        elif isinstance(obj, URI):
            return obj._as_dict_
        elif hasattr(obj, "_as_dict_"):
            d = getattr(obj, "_as_dict_")
            return tuple(sorted((k, self.make_hashable(v)) for k, v in d.items()))
        else:
            return obj

    def unique_list(self, items):
        """Return a list without duplicates, preserving order."""
        seen = set()
        result = []
        for item in items:
            h = self.make_hashable(item)
            if h not in seen:
                seen.add(h)
                result.append(item)
        return result

    # -------------------- public mutation API --------------------
    def append(self, identifier: "Identifier"):
        if isinstance(identifier, Identifier):
            self.add_identifier(identifier)
        else:
            raise ValueError("append expects an Identifier instance")

    # keep the old name working; point it at the corrected spelling
    def add_identifer(self, identifier: "Identifier"):  # backward-compat alias
        return self.add_identifier(identifier)

    def add_identifier(self, identifier: "Identifier"):
        """Add/merge an Identifier (which may contain multiple values)."""
        if not (identifier and isinstance(identifier, Identifier) and identifier.type):
            raise ValueError("The 'identifier' must be a valid Identifier instance with a type.")

        key = identifier.type.value if hasattr(identifier.type, "value") else str(identifier.type)
        existing = self.identifiers.get(key, [])
        merged = self.unique_list(list(existing) + list(identifier.values))
        self.identifiers[key] = merged

    # -------------------- queries --------------------
    def contains(self, identifier: "Identifier") -> bool:
        """Return True if any of the identifier's values are present under that type."""
        if not (identifier and isinstance(identifier, Identifier) and identifier.type):
            return False
        key = identifier.type.value if hasattr(identifier.type, "value") else str(identifier.type)
        if key not in self.identifiers:
            return False
        pool = self.identifiers[key]
        # treat values as a list on the incoming Identifier
        for v in getattr(identifier, "values", []):
            if any(self.make_hashable(v) == self.make_hashable(p) for p in pool):
                return True
        return False

    # -------------------- mapping-like dunder methods --------------------
    def __iter__(self) -> Iterator[str]:
        """Iterate over identifier *types* (keys)."""
        return iter(self.identifiers)

    def __len__(self) -> int:
        """Number of identifier types (keys)."""
        return len(self.identifiers)

    def __contains__(self, key) -> bool:
        """Check if a type key exists (accepts str or enum with .value)."""
        k = key.value if hasattr(key, "value") else str(key)
        return k in self.identifiers

    def __getitem__(self, key):
        """Lookup values by type key (accepts str or enum with .value)."""
        k = key.value if hasattr(key, "value") else str(key)
        return self.identifiers[k]

    # (optional) enable assignment via mapping syntax
    def __setitem__(self, key, values):
        """Set/replace the list of values for a type key."""
        k = key.value if hasattr(key, "value") else str(key)
        vals = values if isinstance(values, list) else [values]
        self.identifiers[k] = self.unique_list(vals)

    def __delitem__(self, key):
        k = key.value if hasattr(key, "value") else str(key)
        del self.identifiers[k]

    # -------------------- dict-style convenience --------------------
    def keys(self):
        return self.identifiers.keys()

    def values(self):
        return self.identifiers.values()

    def items(self):
        return self.identifiers.items()

    def iter_pairs(self) -> Iterator[tuple[str, object]]:
        """Flattened iterator over (type_key, value) pairs."""
        for k, vals in self.identifiers.items():
            for v in vals:
                yield (k, v)
    
    @classmethod
    def _from_json_(cls, data):
        if isinstance(data, dict):
            identifier_list = IdentifierList()
            for key, vals in data.items():
                # Accept both single value and list in JSON
                vals = vals if isinstance(vals, list) else [vals]
                identifier_list.add_identifier(
                    Identifier(value=vals, type=IdentifierType(key))
                )
            return identifier_list
        else:
            raise ValueError("Data must be a dict of identifiers.")

    @property
    def _as_dict_(self):
        # If you want a *copy*, return `dict(self.identifiers)`
        return self.identifiers

    def __repr__(self) -> str:
        return json.dumps(self._as_dict_, indent=4)

    def __str__(self) -> str:
        return json.dumps(self._as_dict_)





