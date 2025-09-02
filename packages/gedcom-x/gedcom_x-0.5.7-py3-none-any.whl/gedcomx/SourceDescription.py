import warnings

from enum import Enum
from typing import List, Optional, Dict, Any

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .Document import Document

"""
======================================================================
 Project: Gedcom-X
 File:    SourceDescription.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-07-25
 Updated:
   - 2025-08-31: _as_dict_ refactored to ignore empty fields, changed id creation to make_uid()
 
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .Agent import Agent
from .Attribution import Attribution
from .Coverage import Coverage
from .Date import Date
from .Identifier import Identifier, IdentifierList, make_uid
from .Note import Note
from .Resource import Resource
from .SourceCitation import SourceCitation
from .SourceReference import SourceReference
from .TextValue import TextValue
from .URI import URI
#=====================================================================

class ResourceType(Enum):
    Collection = "http://gedcomx.org/Collection"
    PhysicalArtifact = "http://gedcomx.org/PhysicalArtifact"
    DigitalArtifact = "http://gedcomx.org/DigitalArtifact"
    Record = "http://gedcomx.org/Record"
    Person = "http://gedcomx.org/Person"    
    
    @property
    def description(self):
        descriptions = {
            ResourceType.Collection: "A collection of genealogical resources. A collection may contain physical artifacts (such as a collection of books in a library), records (such as the 1940 U.S. Census), or digital artifacts (such as an online genealogical application).",
            ResourceType.PhysicalArtifact: "A physical artifact, such as a book.",
            ResourceType.DigitalArtifact: "A digital artifact, such as a digital image of a birth certificate or other record.",
            ResourceType.Record: "A historical record, such as a census record or a vital record."
        }
        return descriptions.get(self, "No description available.")
    
class SourceDescription:
    """Description of a genealogical information source.

    See: http://gedcomx.org/v1/SourceDescription

    Args:
        id (str | None): Unique identifier for this `SourceDescription`.
        resourceType (ResourceType | None): Type/category of the resource being
            described (e.g., digital artifact, physical artifact).
        citations (list[SourceCitation] | None): Citations that reference or
            justify this source description.
        mediaType (str | None): IANA media (MIME) type of the resource
            (e.g., ``"application/pdf"``).
        about (URI | None): Canonical URI that the description is about.
        mediator (Resource | None): The mediator resource (if any) involved in
            providing access to the source.
        publisher (Resource | Agent | None): Publisher of the resource.
        authors (list[Resource] | None): Authors/creators of the resource.
        sources (list[SourceReference] | None): Other sources this description
            derives from or references.
        analysis (Resource | None): Analysis document associated with the
            resource (often a `Document`; kept generic to avoid circular imports).
        componentOf (SourceReference | None): Reference to a parent/containing
            source (this is a component/child of that source).
        titles (list[TextValue] | None): One or more titles for the resource.
        notes (list[Note] | None): Human-authored notes about the resource.
        attribution (Attribution | None): Attribution metadata for who supplied
            or curated this description.
        rights (list[Resource] | None): Rights statements or licenses.
        coverage (list[Coverage] | None): Spatial/temporal coverage of the
            source’s content.
        descriptions (list[TextValue] | None): Short textual summaries or
            descriptions.
        identifiers (IdentifierList | None): Alternative identifiers for the
            resource (DOI, ARK, call numbers, etc.).
        created (Date | None): Creation date of the resource.
        modified (Date | None): Last modified date of the resource.
        published (Date | None): Publication/release date of the resource.
        repository (Agent | None): Repository or agency that holds the resource.
        max_note_count (int): Maximum number of notes to retain/emit. Defaults to 20.

    Raises:
        ValueError: If `id` is not a valid UUID.

    Attributes:
        identifier (str): Gedcom-X specification identifier for this type.
    """

    identifier = "http://gedcomx.org/v1/SourceDescription"
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, id: Optional[str] = None,
                 resourceType: Optional[ResourceType] = None,
                 citations: Optional[List[SourceCitation]] = [],
                 mediaType: Optional[str] = None,
                 about: Optional[URI] = None,
                 mediator: Optional[Agent|Resource] = None,
                 publisher: Optional[Agent|Resource] = None,
                 authors: Optional[List[Resource]] = None,
                 sources: Optional[List[SourceReference]] = None, # SourceReference
                 analysis: Optional["Document|Resource"] = None,  #TODO add type checker so its a document
                 componentOf: Optional[SourceReference] = None, # SourceReference
                 titles: Optional[List[TextValue]] = None,
                 notes: Optional[List[Note]] = None,
                 attribution: Optional[Attribution] = None,
                 rights: Optional[List[Resource]] = [],
                 coverage: Optional[List[Coverage]] = None, # Coverage
                 descriptions: Optional[List[TextValue]] = None,
                 identifiers: Optional[IdentifierList] = None,
                 created: Optional[Date] = None,
                 modified: Optional[Date] = None,
                 published: Optional[Date] = None,
                 repository: Optional[Agent] = None,
                 max_note_count: int = 20):
        
        self.id = id if id else make_uid()
        self.resourceType = resourceType
        self.citations = citations or []
        self.mediaType = mediaType
        self.about = about
        self.mediator = mediator
        self._publisher = publisher 
        self.authors = authors or []
        self.sources = sources or []
        self.analysis = analysis
        self.componentOf = componentOf
        self.titles = titles or []
        self.notes = notes or []
        self.attribution = attribution
        self.rights = rights or []
        self.coverage = coverage or []
        self.descriptions = descriptions or []
        self.identifiers = identifiers or IdentifierList()
        self.created = created
        self.modified = modified
        self.published = published
        self.repository = repository
        self.max_note_count = max_note_count

        self.uri = URI(fragment=id) if id else None #TODO Should i take care of this in the collections?
    
    @property
    def publisher(self) -> Resource | Agent | None:
        return self._publisher
    

    @publisher.setter
    def publisher(self, value: Resource | Agent):
        if value is None:
            self._publisher = None
        elif isinstance(value,Resource):
            self._publisher = value
        elif isinstance(value,Agent):
            self._publisher = value
        else:
            raise ValueError(f"'publisher' must be of type 'URI' or 'Agent', type: {type(value)} was provided")
    
    def add_description(self, desccription_to_add: TextValue):
        if desccription_to_add and isinstance(desccription_to_add,TextValue):
            for current_description in self.descriptions:
                if desccription_to_add == current_description:
                    return
            self.descriptions.append(desccription_to_add)

    def add_identifier(self, identifier_to_add: Identifier):
        if identifier_to_add and isinstance(identifier_to_add,Identifier):
            self.identifiers.append(identifier_to_add)
    
    def add_note(self,note_to_add: Note):
        if len(self.notes) >= self.max_note_count:
            warnings.warn(f"Max not count of {self.max_note_count} reached for id: {self.id}")
            return False
        if note_to_add and isinstance(note_to_add,Note):
            for existing in self.notes:
                if note_to_add == existing:
                    return False
            self.notes.append(note_to_add)
    
    def add_source(self, source_to_add: SourceReference):
        if source_to_add and isinstance(object,SourceReference):
            for current_source in self.sources:
                if current_source == source_to_add:
                    return
            self.sources.append(source_to_add)

    def add_title(self, title_to_add: TextValue):
        if isinstance(title_to_add,str): title_to_add = TextValue(value=title_to_add)
        if title_to_add and isinstance(title_to_add, TextValue):
            for current_title in self.titles:
                if title_to_add == current_title:
                    return False
            self.titles.append(title_to_add)
        else:
            raise ValueError(f"Cannot add title of type {type(title_to_add)}")
            
    @property
    def _as_dict_(self) -> Dict[str, Any]:
        from .Serialization import Serialization
        type_as_dict = {}

        if self.id:
            type_as_dict['id'] = self.id
        if self.about:
            type_as_dict['about'] = self.about._as_dict_
        if self.resourceType:
            type_as_dict['resourceType'] = getattr(self.resourceType, 'value', self.resourceType)
        if self.citations:
            type_as_dict['citations'] = [c._as_dict_ for c in self.citations if c]
        if self.mediaType:
            type_as_dict['mediaType'] = self.mediaType
        if self.mediator:
            type_as_dict['mediator'] = self.mediator._as_dict_
        if self.publisher:
            type_as_dict['publisher'] = self.publisher._as_dict_ #TODO Resource this
        if self.authors:
            type_as_dict['authors'] = [a._as_dict_ for a in self.authors if a]
        if self.sources:
            type_as_dict['sources'] = [s._as_dict_ for s in self.sources if s]
        if self.analysis:
            type_as_dict['analysis'] = self.analysis._as_dict_
        if self.componentOf:
            type_as_dict['componentOf'] = self.componentOf._as_dict_ 
        if self.titles:
            type_as_dict['titles'] = [t._as_dict_ for t in self.titles if t]
        if self.notes:
            type_as_dict['notes'] = [n._as_dict_ for n in self.notes if n]
        if self.attribution:
            type_as_dict['attribution'] = self.attribution._as_dict_
        if self.rights:
            type_as_dict['rights'] = [r._as_dict_ for r in self.rights if r]
        if self.coverage:
            type_as_dict['coverage'] = [c._as_dict_ for c in self.coverage if c]
        if self.descriptions:
            type_as_dict['descriptions'] = [d for d in self.descriptions if d]
        if self.identifiers:
            type_as_dict['identifiers'] = self.identifiers._as_dict_
        if self.created is not None:
            type_as_dict['created'] = self.created
        if self.modified is not None:
            type_as_dict['modified'] = self.modified
        if self.published is not None:
            type_as_dict['published'] = self.published
        if self.repository:
            type_as_dict['repository'] = self.repository._as_dict_ #TODO Resource this
        if self.uri and self.uri.value:
            type_as_dict['uri'] = self.uri.value

        
        return Serialization.serialize_dict(type_as_dict)
         
            
    @classmethod
    def _from_json_(cls, data: Dict[str, Any]) -> 'SourceDescription':
        # TODO Hande Resource/URI
        
        # Basic fields
        id_ = data.get('id')
        rt = ResourceType(data['resourceType']) if data.get('resourceType') else None

        # Sub-objects
        citations    = [SourceCitation._from_json_(c) for c in data.get('citations', [])]
        about        = URI._from_json_(data['about']) if data.get('about') else None
        mediator     = Resource._from_json_(data['mediator']) if data.get('mediator') else None
        publisher    = Resource._from_json_(data['publisher']) if data.get('publisher') else None
        authors      = [Resource._from_json_(a) for a in data.get('authors', [])] if data.get('authors') else None
        sources      = [SourceReference._from_json_(s) for s in data.get('sources', [])]
        analysis     = Resource._from_json_(data['analysis']) if data.get('analysis') else None
        component_of = SourceReference._from_json_(data['componentOf']) if data.get('componentOf') else None
        titles       = [TextValue._from_json_(t) for t in data.get('titles', [])]
        notes        = [Note._from_json_(n) for n in data.get('notes', [])]
        attribution  = Attribution._from_json_(data['attribution']) if data.get('attribution') else None
        rights       = [URI._from_json_(r) for r in data.get('rights', [])]
        coverage     = [Coverage._from_json_(cvg) for cvg in data.get('coverage',[])] 
        descriptions = [TextValue._from_json_(d) for d in data.get('descriptions', [])]
        identifiers  = IdentifierList._from_json_(data.get('identifiers', []))
        
        created      = Date._from_json_(data['created']) if data.get('created') else None
        modified     = data.get('modified',None)
        published    = Date._from_json_(data['published']) if data.get('published') else None
        repository   = Agent._from_json_(data['repository']) if data.get('repository') else None

        return cls(
            id=id_, resourceType=rt, citations=citations,
            mediaType=data.get('mediaType'), about=about,
            mediator=mediator, publisher=publisher,
            authors=authors, sources=sources,
            analysis=analysis, componentOf=component_of,
            titles=titles, notes=notes, attribution=attribution,
            rights=rights, coverage=coverage,
            descriptions=descriptions, identifiers=identifiers,
            created=created, modified=modified,
            published=published, repository=repository
        )

    