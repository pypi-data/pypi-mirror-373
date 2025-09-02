from enum import Enum
from typing import List, Optional

from gedcomx.Attribution import Attribution
from gedcomx.Conclusion import ConfidenceLevel
from gedcomx.Note import Note
from gedcomx.SourceReference import SourceReference
from gedcomx.Resource import Resource

from .Conclusion import Conclusion
from .Qualifier import Qualifier


from collections.abc import Sized

class GenderType(Enum):
    Male = "http://gedcomx.org/Male"
    Female = "http://gedcomx.org/Female"
    Unknown = "http://gedcomx.org/Unknown"
    Intersex = "http://gedcomx.org/Intersex"
    
    @property
    def description(self):
        descriptions = {
            GenderType.Male: "Male gender.",
            GenderType.Female: "Female gender.",
            GenderType.Unknown: "Unknown gender.",
            GenderType.Intersex: "Intersex (assignment at birth)."
        }
        return descriptions.get(self, "No description available.")
    
class Gender(Conclusion):
    identifier = 'http://gedcomx.org/v1/Gender'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None, 
                 type: Optional[GenderType] = None
                 ) -> None:
        super().__init__(id=id, lang=lang, sources=sources, analysis=analysis, notes=notes, confidence=confidence, attribution=attribution)
        self.type = type
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization    
        type_as_dict = super()._as_dict_  
        if self.type:
            type_as_dict['type'] = self.type.value if self.type else None                   
        
        
        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls,data):
        from .Serialization import Serialization
        
        return Serialization.deserialize(data, Gender)
        
        