from typing import List, Optional
from urllib.parse import urljoin

"""
======================================================================
 Project: Gedcom-X
 File:    Person.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX Person Type

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
from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Extensions.rs10.rsLink import _rsLinkList
from .Fact import Fact, FactType
from .Gender import Gender, GenderType
from .Identifier import IdentifierList
from .Name import Name, QuickName
from .Note import Note
from .Resource import Resource
from .SourceReference import SourceReference
from .Subject import Subject

class Person(Subject):
    """A person in the system.

    Args:
        id (str):      Unique identifier for this person.
        name (str):    Full name.
        birth (date):  Birth date (YYYY-MM-DD).
        friends (List[Person], optional): List of friends. Defaults to None.

    Raises:
        ValueError: If `id` is not a valid UUID.
    """
    identifier = 'http://gedcomx.org/v1/Person'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str | None = None,
             lang: str = 'en',
             sources: Optional[List[SourceReference]] = None,
             analysis: Optional[Resource] = None,
             notes: Optional[List[Note]] = None,
             confidence: Optional[ConfidenceLevel] = None,
             attribution: Optional[Attribution] = None,
             extracted: Optional[bool] = None,
             evidence: Optional[List[EvidenceReference]] = None,
             media: Optional[List[SourceReference]] = None,
             identifiers: Optional[IdentifierList] = None,
             private: Optional[bool] = False,
             gender: Optional[Gender] = Gender(type=GenderType.Unknown),
             names: Optional[List[Name]] = None,
             facts: Optional[List[Fact]] = None,
             living: Optional[bool] = False,
             links: Optional[_rsLinkList] = None,
             uri: Optional[Resource] = None) -> None:
        # Call superclass initializer if needed
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers,links=links,uri=uri)
        
        # Initialize mutable attributes to empty lists if None
        self.sources = sources if sources is not None else []
        self.notes = notes if notes is not None else []
        self.evidence = evidence if evidence is not None else []
        self.media = media if media is not None else []
        self.identifiers = identifiers if identifiers is not None else []
        self.names = names if names is not None else []
        self.facts = facts if facts is not None else []

        self.private = private
        self.gender = gender

        self.living = living       #TODO This is from familysearch API

        self._relationships = []
          
    def add_fact(self, fact_to_add: Fact) -> bool:
        if fact_to_add and isinstance(fact_to_add,Fact):
            for current_fact in self.facts:
                if fact_to_add == current_fact:
                    return False
            self.facts.append(fact_to_add)
            return True

    def add_name(self, name_to_add: Name) -> bool:
        if len(self.names) > 5: 
            for name in self.names:
                print(name)
            raise
        if name_to_add and isinstance(name_to_add, Name):
            for current_name in self.names:
                if name_to_add == current_name:
                    return False
            self.names.append(name_to_add)
            return True
    
    def _add_relationship(self, relationship_to_add: object):
        from .Relationship import Relationship
        if isinstance(relationship_to_add,Relationship):
            self._relationships.append(relationship_to_add)
        else:
            raise ValueError()
    
    def display(self):
        display = {
        "ascendancyNumber": "1",
        "deathDate": "from 2001 to 2005",
        "descendancyNumber": "1",
        "gender": self.gender.type if self.gender else 'Unknown',
        "lifespan": "-2005",
        "name": self.names[0].nameForms[0].fullText
            }
        
        return display

    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = super()._as_dict_  
        if self.private is not None:
            type_as_dict['private'] = self.private
        if self.living is not None:
            type_as_dict['living'] = self.living
        if self.gender:
            type_as_dict['gender'] = self.gender._as_dict_
        if self.names:
            type_as_dict['names'] = [n._as_dict_ for n in self.names if n]
        if self.facts:
            type_as_dict['facts'] = [f._as_dict_ for f in self.facts if f]
        if self.uri:
            type_as_dict['uri'] = self.uri._as_dict_

        return Serialization.serialize_dict(type_as_dict)
           
    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        from .Serialization import Serialization
        return Serialization.deserialize(data, Person)

    @classmethod
    def from_familysearch(cls, pid: str, token: str, *, base_url: Optional[str] = None):
        from .Serialization import Serialization
        """
        Fetch a single person by PID from FamilySearch and return a Person.
        - pid: e.g. "KPHP-4B4"
        - token: OAuth2 access token (Bearer)
        - base_url: override API base (defaults to settings.FS_API_BASE or prod)
        """
        import requests
        default_base = "https://apibeta.familysearch.org/platform/"

        base = (base_url or default_base).rstrip("/") + "/"
        url = urljoin(base, f"tree/persons/{pid}")

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        }

        resp = requests.get(url, headers=headers, timeout=(5, 30))
        resp.raise_for_status()

        payload = resp.json()
        persons = payload.get("persons") or []

        # Prefer exact match on PID, else first item if present
        person_json = next((p for p in persons if (p.get("id") == pid)), None) or (persons[0] if persons else None)
        if not person_json:
            raise ValueError(f"FamilySearch returned no person for PID {pid}")

        # Keep your existing deserialization helper
        return Serialization.deserialize(person_json, Person)    

class QuickPerson:
    """A GedcomX Person Data Type created with basic information.

    Underlying GedcomX Types are created for you.
        
    Args:
        name (str):    Full name.
        birth (date,Optional):  Birth date (YYYY-MM-DD).
        death (date, Optional)

        

    Raises:
        ValueError: If `id` is not a valid UUID.
    """
    def __new__(cls, name: str, dob: Optional[str] = None, dod: Optional[str] = None):
        # Build facts from args
        facts = []
        if dob:
            facts.append(Fact(type=FactType.Birth, date=Date(original=dob)))
        if dod:
            facts.append(Fact(type=FactType.Death, date=Date(original=dod)))

        # Return the different class instance
        return Person(facts=facts, names=[QuickName(name=name)] if name else None)