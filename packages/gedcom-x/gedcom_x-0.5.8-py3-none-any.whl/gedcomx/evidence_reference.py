from typing import Optional

from .attribution import Attribution
from .resource import Resource

class EvidenceReference:
    identifier = 'http://gedcomx.org/v1/EvidenceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, resource: Resource, attribution: Optional[Attribution]) -> None:
        pass