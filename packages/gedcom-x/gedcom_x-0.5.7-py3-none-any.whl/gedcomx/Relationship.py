from enum import Enum
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .EvidenceReference import EvidenceReference
from .Fact import Fact
from .Identifier import Identifier
from .Note import Note
from .Person import Person

from .SourceReference import SourceReference
from .Resource import Resource

from .Subject import Subject

class RelationshipType(Enum):
    Couple = "http://gedcomx.org/Couple"
    ParentChild = "http://gedcomx.org/ParentChild"
    
    @property
    def description(self):
        descriptions = {
            RelationshipType.Couple: "A relationship of a pair of persons.",
            RelationshipType.ParentChild: "A relationship from a parent to a child."
        }
        return descriptions.get(self, "No description available.")
    
class Relationship(Subject):
    """Represents a relationship between two Person(s)

    Args:
        type (RelationshipType): Type of relationship 
        person1 (Person) = First Person in Relationship
        person2 (Person): Second Person in Relationship

    Raises:
        
    """
    identifier = 'http://gedcomx.org/v1/Relationship'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
             person1: Optional[Person | Resource] = None,
             person2: Optional[Person | Resource] = None,
             facts: Optional[List[Fact]] = None,  
             id: Optional[str] = None,
             lang: Optional[str] = None,
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[Resource] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: Optional[bool] = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[List[Identifier]] = None,
             type: Optional[RelationshipType] = None,
             ) -> None:
    
        # Call superclass initializer if required
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        
        self.type = type
        self.person1 = person1
        self.person2 = person2
        self.facts = facts if facts else []
    
    def add_fact(self,fact: Fact):
        if fact is not None and isinstance(fact,Fact):
            for existing_fact in self.facts:
                if fact == existing_fact:
                    return
            self.facts.append(fact)
        else:
            raise TypeError(f"Expected type 'Fact' recieved type {type(fact)}")

    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = super()._as_dict_
        type_as_dict.update({
            "type": self.type.value if isinstance(self.type, RelationshipType) else self.type,
            "person1": Resource(target=self.person1)._as_dict_ if self.person1 else None,
            "person2": Resource(target=self.person1)._as_dict_ if self.person2 else None,
            "facts": [fact for fact in self.facts] if self.facts else None
        })
        return Serialization.serialize_dict(type_as_dict)

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        from .Serialization import Serialization
        return Serialization.deserialize(data, Relationship)
    