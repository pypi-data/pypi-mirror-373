from enum import Enum
from typing import List, Optional

from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .EvidenceReference import EvidenceReference
from .Identifier import Identifier
from .Note import Note
from .PlaceReference import PlaceReference
from .SourceReference import SourceReference
from .Resource import Resource

from .TextValue import TextValue
from .Subject import Subject

class GroupRoleType(Enum):
    def __init__(self) -> None:
        super().__init__()

class GroupRole:
    identifier = 'http://gedcomx.org/v1/GroupRole'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, person: Resource,type: Optional[Enum], date: Optional[Date],details: Optional[str]) -> None:
        pass

class Group(Subject):
    identifier = 'http://gedcomx.org/v1/Group'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: str | None, lang: str | None, sources: SourceReference | None, analysis: Resource | None, notes: Note | None, confidence: ConfidenceLevel | None, attribution: Attribution | None, extracted: bool | None, evidence: List[EvidenceReference] | None, media: List[SourceReference] | None, identifiers: List[Identifier] | None,
                 names: TextValue,
                 date: Optional[Date],
                 place: Optional[PlaceReference],
                 roles: Optional[List[GroupRole]]) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)