from .Gedcom5x import Gedcom5xRecord
from .Fact import Fact, FactType
from .Event import Event, EventType

fact_event_table = {
    # Person Fact / Event Types
    "ADOP": {
        "Fact": FactType.AdoptiveParent,
        "Event": EventType.Adoption,
    },
    "CHR": {
        "Fact": FactType.AdultChristening,
        "Event": EventType.AdultChristening,
    },
    "EVEN": {
        "Fact": FactType.Amnesty,
        # no Event
    },
    "BAPM": {
        "Fact": FactType.Baptism,
        "Event": EventType.Baptism,
    },
    "BARM": {
        "Fact": FactType.BarMitzvah,
        "Event": EventType.BarMitzvah,
    },
    "BASM": {
        "Fact": FactType.BatMitzvah,
        "Event": EventType.BatMitzvah,
    },
    "BIRT": {
        "Fact": FactType.Birth,
        "Event": EventType.Birth,
    },
    "BIRT, CHR": {
        "Fact": FactType.Birth,
        "Event": EventType.Birth,
    },
    "BLES": {
        "Fact": FactType.Blessing,
        "Event": EventType.Blessing,
    },
    "BURI": {
        "Fact": FactType.Burial,
        "Event": EventType.Burial,
    },
    "CAST": {
        "Fact": FactType.Caste,
        # no Event
    },
    "CENS": {
        "Fact": FactType.Census,
        "Event": EventType.Census,
    },
    "CIRC": {
        "Fact": FactType.Circumcision,
        "Event": EventType.Circumcision,
    },
    "CONF": {
        "Fact": FactType.Confirmation,
        "Event": EventType.Confirmation,
    },
    "CREM": {
        "Fact": FactType.Cremation,
        "Event": EventType.Cremation,
    },
    "DEAT": {
        "Fact": FactType.Death,
        "Event": EventType.Death,
    },
    "EDUC": {
        "Fact": FactType.Education,
        "Event": EventType.Education,
    },
    "EMIG": {
        "Fact": FactType.Emigration,
        "Event": EventType.Emigration,
    },
    "FCOM": {
        "Fact": FactType.FirstCommunion,
        "Event": EventType.FirstCommunion,
    },
    "GRAD": {
        "Fact": FactType.Graduation,
        # no Event
    },
    "IMMI": {
        "Fact": FactType.Immigration,
        "Event": EventType.Immigration,
    },
    "MIL": {
        "Fact": FactType.MilitaryService,
        # no Event
    },
    "NATI": {
        "Fact": FactType.Nationality,
        # no Event
    },
    "NATU": {
        "Fact": FactType.Naturalization,
        "Event": EventType.Naturalization,
    },
    "OCCU": {
        "Fact": FactType.Occupation,
        # no Event
    },
    "ORDN": {
        "Fact": FactType.Ordination,
        "Event": EventType.Ordination,
    },
    "DSCR": {
        "Fact": FactType.PhysicalDescription,
        # no Event
    },
    "PROB": {
        "Fact": FactType.Probate,
        # no Event
    },
    "PROP": {
        "Fact": FactType.Property,
        # no Event
    },
    "RELI": {
        "Fact": FactType.Religion,
        # no Event
    },
    "RESI": {
        "Fact": FactType.Residence,
        # no Event
    },
    "WILL": {
        "Fact": FactType.Will,
        # no Event
    },

    # Couple Relationship Fact / Event Types
    "ANUL": {
        "Fact": FactType.Annulment,
        "Event": EventType.Annulment,
    },
    "DIV": {
        "Fact": FactType.Divorce,
        "Event": EventType.Divorce,
    },
    "DIVF": {
        "Fact": FactType.DivorceFiling,
        "Event": EventType.DivorceFiling,
    },
    "ENGA": {
        "Fact": FactType.Engagement,
        "Event": EventType.Engagement,
    },
    "MARR": {
        "Fact": FactType.Marriage,
        "Event": EventType.Marriage,
    },
    "MARB": {
        "Fact": FactType.MarriageBanns,
        # no Event
    },
    "MARC": {
        "Fact": FactType.MarriageContract,
        # no Event
    },
    "MARL": {
        "Fact": FactType.MarriageLicense,
        # no Event
    },
    "MARS":{
        "Fact":EventType.MarriageSettlment

    },
    "SEPA": {
        "Fact": FactType.Separation,
        # no Event
    },

}

class GedcomXObject:
    def __init__(self,record: Gedcom5xRecord | None = None) -> None:
        self.created_with_tag: str = record.tag if record and isinstance(record, Gedcom5xRecord) else None    
        self.created_at_level: int = record.level if record and isinstance(record, Gedcom5xRecord) else None
        self.created_at_line_number: int = record.line_number if record and isinstance(record, Gedcom5xRecord) else None

class GedcomXSourceOrDocument(GedcomXObject):
    def __init__(self,record: Gedcom5xRecord | None = None) -> None:
        super().__init__(record)
        self.title: str = None
        self.citation: str = None
        self.page: str = None
        self.contributor: str = None
        self.publisher: str = None
        self.rights: str = None
        self.url: str = None
        self.medium: str = None
        self.type: str = None
        self.format: str = None
        self.created: str = None
        self.modified: str = None
        self.language: str = None
        self.relation: str = None
        self.identifier: str = None
        self.description: str = None

class GedcomXEventOrFact(GedcomXObject):
    def __new__(cls,record: Gedcom5xRecord | None = None, object_stack: dict | None = None) -> object:
        super().__init__(record)
        if record.tag in fact_event_table.keys():

            if 'Fact' in fact_event_table[record.tag].keys():
                obj = Fact(type=fact_event_table[record.tag]['Fact'])
                return obj
            elif 'Event' in fact_event_table[record.tag].keys():
                obj = Event(type=fact_event_table[record.tag]['Fact'])
            else:
                raise ValueError
        else:
            raise ValueError(f"{record.tag} not found in map")

class GedcomXRelationshipBuilder(GedcomXObject):
    def __new__(cls,record: Gedcom5xRecord | None = None, object_stack: dict | None = None) -> object:
        last_relationship = object_stack.get('lastrelationship',None)
        last_relationship_data = object_stack.get('lastrelationshipdata',None)
        if not isinstance(last_relationship_data,dict):
            last_relationship_data = None

        
