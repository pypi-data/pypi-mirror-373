import base64
import uuid
import warnings

from typing import List, Optional

from .Attribution import Attribution
#from .Document import Document
from .Note import Note
from .Qualifier import Qualifier

from .SourceReference import SourceReference
from .Resource import Resource, URI
from .Extensions.rs10.rsLink import _rsLinkList, rsLink

from collections.abc import Sized

class ConfidenceLevel(Qualifier):
    High = "http://gedcomx.org/High"
    Medium = "http://gedcomx.org/Medium"
    Low = "http://gedcomx.org/Low"

    _NAME_TO_URI = {
        "high": High,
        "medium": Medium,
        "low": Low,
    }

    @classmethod
    def _from_json_(cls, data):
        """
        Accepts:
          - "High" | "Medium" | "Low"
          - "http://gedcomx.org/High" | ".../Medium" | ".../Low"
          - {"type": "..."} or {"value": "..."} or {"confidence": "..."} or {"level": "..."} or {"uri": "..."}
          - existing ConfidenceLevel instance
        Returns:
          ConfidenceLevel instance with .value set to the canonical URI.
        """
        if data is None:
            return None

        if isinstance(data, cls):
            return data

        # Extract token from dicts or use the raw scalar
        if isinstance(data, dict):
            token = (
                data.get("confidence")
                or data.get("type")
                or data.get("value")
                or data.get("level")
                or data.get("uri")
            )
        else:
            token = data

        if token is None:
            return None

        token_str = str(token).strip()

        # Normalize to canonical URI
        if token_str.lower() in cls._NAME_TO_URI:
            uri = cls._NAME_TO_URI[token_str.lower()]
        elif token_str in (cls.High, cls.Medium, cls.Low):
            uri = token_str
        else:
            raise ValueError(f"Unknown ConfidenceLevel: {token!r}")

        # Create a ConfidenceLevel instance without invoking Qualifier.__init__
        obj = cls.__new__(cls)
        # store the canonical URI on the instance; used by description and (optionally) serialization
        obj.value = uri
        return obj

    @property
    def description(self):
        descriptions = {
            self.High: "The contributor has a high degree of confidence that the assertion is true.",
            self.Medium: "The contributor has a medium degree of confidence that the assertion is true.",
            self.Low: "The contributor has a low degree of confidence that the assertion is true."
        }
        # Works whether the instance holds .value or (edge-case) if `self` is compared directly
        key = getattr(self, "value", self)
        return descriptions.get(key, "No description available.")

    
class Conclusion:
    """
    Represents a conclusion in the GEDCOM X conceptual model. A conclusion is a 
    genealogical assertion about a person, relationship, or event, derived from 
    one or more sources, with optional supporting metadata such as confidence, 
    attribution, and notes.

    Args:
        id (str, optional): A unique identifier for the conclusion. If not provided, 
            a UUID-based identifier will be automatically generated.
        lang (str, optional): The language code of the conclusion. 
        sources (list[SourceReference], optional): A list of source references that 
            support the conclusion.
        analysis (Document | Resource, optional): A reference to an analysis document 
            or resource that supports the conclusion.
        notes (list[Note], optional): A list of notes providing additional context. 
            Defaults to an empty list.
        confidence (ConfidenceLevel, optional): The contributor's confidence in the 
            conclusion (High, Medium, or Low).
        attribution (Attribution, optional): Information about who contributed the 
            conclusion and when.
        uri (Resource, optional): A URI reference for the conclusion. Defaults to a 
            URI with the fragment set to the `id`.
        links (_LinkList, optional): A list of links associated with the conclusion. 
            Defaults to an empty `_LinkList`.  
    """
    identifier = 'http://gedcomx.org/v1/Conclusion'
    version = 'http://gedcomx.org/conceptual-model/v1'

    @staticmethod
    def default_id_generator():
        # Generate a standard UUID
        standard_uuid = uuid.uuid4()
        # Convert UUID to bytes
        uuid_bytes = standard_uuid.bytes
        # Encode bytes to a Base64 string
        short_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('utf-8')
        return short_uuid
    
    def __init__(self,
                 id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[object | Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 uri: Optional[Resource] = None,
                 _max_note_count: int = 20,
                 links: Optional[_rsLinkList] = None) -> None:
        
        self._id_generator = Conclusion.default_id_generator

        self.id = id if id else None
        self.lang = lang
        self.sources = sources if sources else []
        self.analysis = analysis
        self.notes = notes if notes else []
        self.confidence = confidence
        self.attribution = attribution
        self.max_note_count = _max_note_count
        self.uri = uri if uri else URI(fragment=id if id else self.id)
        self.links = links if links else _rsLinkList()    #NOTE This is not in specification, following FS format
    
    def add_note(self,note_to_add: Note):
        if self.notes and len(self.notes) >= self.max_note_count:
            warnings.warn(f"Max not count of {self.max_note_count} reached for id: {self.id}")
            return False
        if note_to_add and isinstance(note_to_add,Note):
            for existing in self.notes:
                if note_to_add == existing:
                    return False
            self.notes.append(note_to_add)

    def add_source(self, source_to_add: SourceReference):
        if source_to_add and isinstance(source_to_add,SourceReference):
            for current_source in self.sources:
                if source_to_add == current_source:
                    return
            self.sources.append(source_to_add)
        else:
            raise ValueError()
        
    def add_link(self,link: rsLink) -> bool:
        """
        Adds a link to the Conclusion link list.

        Args:
            link (rsLink): The link to be added.

        Returns:
            bool: The return value. True for success, False otherwise.
        
        Note: Duplicate checking not impimented at this level
        """
        if link and isinstance(link,rsLink):
            self.links.add(link)
            return True
        return False
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}

        if self.id:
            type_as_dict['id'] = self.id
        if self.lang:
            type_as_dict['lang'] = self.lang
        if self.sources:
            type_as_dict['sources'] = [s._as_dict_ for s in self.sources if s]
        if self.analysis:
            type_as_dict['analysis'] = getattr(self.analysis, '_as_dict_', self.analysis)
        if self.notes:
            type_as_dict['notes'] = [
                (n._as_dict_ if hasattr(n, '_as_dict_') else n) for n in self.notes if n
            ]
        if self.confidence is not None:
            type_as_dict['confidence'] = self.confidence
        if self.attribution:
            type_as_dict['attribution'] = getattr(self.attribution, '_as_dict_', self.attribution)
        if self.links:
            type_as_dict['links'] = self.links._as_dict_
      
        return Serialization.serialize_dict(type_as_dict) 
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        
        return (
            self.id == other.id and
            self.lang == other.lang and
            self.sources == other.sources and
            self.analysis == other.analysis and
            self.notes == other.notes and
            self.confidence == other.confidence and
            self.attribution == other.attribution
        )