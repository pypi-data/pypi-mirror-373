from typing import List, Optional

"""
======================================================================
 Project: Gedcom-X
 File:    PlaceDescription.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX PlaceDescription Type

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
from .Identifier import IdentifierList
from .Note import Note
from .Resource import Resource
from .SourceReference import SourceReference
from .Subject import Subject
from .TextValue import TextValue
from .URI import URI

class PlaceDescription(Subject):
    """PlaceDescription describes the details of a place in terms of 
    its name and possibly its type, time period, and/or a geospatial description
    functioning as a description of a place as a snapshot in time.

    Encapsulates textual names, geospatial coordinates, jurisdictional context,
    temporal coverage, and related resources (media, sources, evidence, etc.).
    

    Attributes:
        names (Optional[List[TextValue]]): Human-readable names or labels for
            the place (e.g., “Boston, Suffolk, Massachusetts, United States”).
        type (Optional[str]): A place type identifier (e.g., a URI). **TODO:**
            replace with an enumeration when finalized.
        place (Optional[URI]): Canonical identifier (URI) for the place.
        jurisdiction (Optional[Resource|PlaceDescription]): The governing or
            containing jurisdiction of this place (e.g., county for a town).
        latitude (Optional[float]): Latitude in decimal degrees (WGS84).
        longitude (Optional[float]): Longitude in decimal degrees (WGS84).
        temporalDescription (Optional[Date]): Temporal coverage/validity window
            for this description (e.g., when a jurisdictional boundary applied).
        spatialDescription (Optional[Resource]): A resource describing spatial
            geometry or a link to an external gazetteer/shape definition.
    """
    identifier = "http://gedcomx.org/v1/PlaceDescription"
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] =None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] =None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 extracted: Optional[bool] = None,
                 evidence: Optional[List[EvidenceReference]] = None,
                 media: Optional[List[SourceReference]] = None,
                 identifiers: Optional[IdentifierList] = None,
                 names: Optional[List[TextValue]] = None,
                 type: Optional[str] = None,    #TODO This needs to be an enumerated value, work out details
                 place: Optional[URI] = None,
                 jurisdiction: Optional["Resource | PlaceDescription"] = None, 
                 latitude: Optional[float] = None,
                 longitude: Optional[float] = None,
                 temporalDescription: Optional[Date] = None,
                 spatialDescription: Optional[Resource] = None,) -> None:
        
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution, extracted, evidence, media, identifiers)
        self.names = names
        self.type = type
        self.place = place
        self.jurisdiction = jurisdiction
        self.latitude = latitude
        self.longitude = longitude
        self.temporalDescription = temporalDescription
        self.spatialDescription = spatialDescription

    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = super()._as_dict_
        
        if self.names:
            type_as_dict["names"] = [n._as_dict_ for n in self.names if n]
        if self.type:
            type_as_dict["type"] = self.type    #TODO
        if self.place:
            type_as_dict["place"] = self.place._as_dict_
        if self.jurisdiction:
            type_as_dict["jurisdiction"] = self.jurisdiction._as_dict_ 
        if self.latitude is not None: # include 0.0; exclude only None
            type_as_dict["latitude"] = float(self.latitude)
        if self.longitude is not None: # include 0.0; exclude only None
            type_as_dict["longitude"] = float(self.longitude)
        if self.temporalDescription:
            type_as_dict["temporalDescription"] = self.temporalDescription._as_dict_
        if self.spatialDescription:
            type_as_dict["spatialDescription"] = self.spatialDescription._as_dict_

        return Serialization.serialize_dict(type_as_dict) 

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a PlaceDescription instance from a JSON-dict (already parsed).
        """
        from .Serialization import Serialization
        return Serialization.deserialize(data, PlaceDescription)   