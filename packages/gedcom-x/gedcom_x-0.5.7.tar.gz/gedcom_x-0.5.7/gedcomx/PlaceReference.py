from __future__ import annotations
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .PlaceDescription import PlaceDescription

"""
======================================================================
 Project: Gedcom-X
 File:    PlaceReference.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX PlaceReference Type

 Created: 2025-08-25
 Updated:
   - 2025-08-31: _as_dict_ to only create entries in dict for fields that hold data
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .Resource import Resource

class PlaceReference:
    """defines a reference to a PlaceDescription.

    
    Attributes:
        original (Optional[str]): The unnormalized, user- or source-provided place text.
            Keep punctuation and ordering exactly as recorded in the source.
        description (Optional[Resource|PlaceDescription]): A :class:`gedcomx.PlaceDescription` Object or pointer to it. (URI/:class:`~Resource`)

    """
    identifier = 'http://gedcomx.org/v1/PlaceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self,
                 original: Optional[str] = None,
                 description: Optional["Resource | PlaceDescription"] = None) -> None:
        self.original = original
        self.description = description

    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.original:
            type_as_dict['original'] = self.original
        if self.description:
            type_as_dict['description'] = self.description._as_dict_ 
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data):
        from .Serialization import Serialization
        return Serialization.deserialize(data, PlaceReference)



