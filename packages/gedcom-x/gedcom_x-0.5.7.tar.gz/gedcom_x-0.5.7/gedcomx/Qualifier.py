from typing import Optional

"""
======================================================================
 Project: Gedcom-X
 File:    Qualifier.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX Qualifier Type

 Created: 2025-08-25
 Updated:
   - 2025-08-31: _as_dict_ to only create entries in dict for fields that 
   hold data, updated _from_json
   
======================================================================
"""

class Qualifier:
    """defines the data structure used to supply additional details, annotations,
    tags, or other qualifying data to a specific data element.

    
    Attributes:
        name str: The name of the Qualifier. *It is RECOMMENDED that the qualifier 
            name resolve to an element of a constrained vocabulary.*
            
        value (Optional[str]): The value of the Qualifier. *If provided, the name 
            MAY give the semantic meaning of the value.*

    """
    identifier = 'http://gedcomx.org/v1/Qualifier'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, name: str, value: Optional[str]) -> None:
        self.name = name
        self.value = value
    
    @property
    def __as_dict__(self):
        from .Serialization import Serialization

        type_as_dict = {}
        if self.name:
            type_as_dict["name"] = self.name
        if self.value:
            type_as_dict["value"] = self.value
        
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json(cls,data):
        qualifier = Qualifier(name=data.get('name',"ERROR: This Qualifier require a 'name' but has none."),value=data.get('value'))
        return qualifier

