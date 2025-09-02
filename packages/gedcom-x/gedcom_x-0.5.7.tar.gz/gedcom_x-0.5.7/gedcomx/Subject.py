import warnings
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import Conclusion, ConfidenceLevel
from .EvidenceReference import EvidenceReference
from .Identifier import Identifier, IdentifierList
from .Note import Note

from .SourceReference import SourceReference
from .Resource import Resource
from .Extensions.rs10.rsLink import _rsLinkList

class Subject(Conclusion):
    identifier = 'http://gedcomx.org/v1/Subject'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 id: Optional[str],
                 lang: Optional[str] = 'en',
                 sources: Optional[List[SourceReference]] = [],
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = [],
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 extracted: Optional[bool] = None,
                 evidence: Optional[List[EvidenceReference]] = [],
                 media: Optional[List[SourceReference]] = [],
                 identifiers: Optional[IdentifierList] = None,
                 uri: Optional[Resource] = None,
                 links: Optional[_rsLinkList] = None) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution,links=links)
        self.extracted = extracted
        self.evidence = evidence
        self.media = media
        self.identifiers = identifiers if identifiers else IdentifierList()
        self.uri = uri
        
    def add_identifier(self, identifier_to_add: Identifier):
        if identifier_to_add and isinstance(identifier_to_add,Identifier):
            for current_identifier in self.identifiers:
                if identifier_to_add == current_identifier:
                    return
            self.identifiers.append(identifier_to_add)
   
    @property
    def _as_dict_(self):
        from .Serialization import Serialization

        type_as_dict = super()._as_dict_  # Start with base class fields
        # Only add Relationship-specific fields
        type_as_dict.update({
            "extracted": self.extracted,
            "evidence": [evidence_ref for evidence_ref in self.evidence] if self.evidence else None,
            "media": [media for media in self.media] if self.media else None,
            "identifiers": self.identifiers._as_dict_ if self.identifiers else None
                           
        })
        return Serialization.serialize_dict(type_as_dict)