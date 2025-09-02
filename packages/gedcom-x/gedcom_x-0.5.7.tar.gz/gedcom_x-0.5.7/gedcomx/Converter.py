DEBUG = False
import base64
import json
import mimetypes
import re
import uuid
import xml.etree.ElementTree as ET

from typing import List, Optional, Any
from xml.dom import minidom
from .Address import Address
from .Agent import Agent
from .Attribution import Attribution
from .Conclusion import Conclusion
from .Coverage import Coverage
from .Date import Date, date_to_timestamp
from .Document import Document
from .EvidenceReference import EvidenceReference
from .Exceptions import TagConversionError
from .Event import Event,EventType,EventRole,EventRoleType
from .Fact import Fact, FactType, FactQualifier
from .Gedcom import Gedcom
from .Gedcom5x import Gedcom5x, Gedcom5xRecord
from .GedcomX import GedcomX
from .Gender import Gender, GenderType
from .Group import Group
from .Identifier import Identifier, IdentifierType, make_uid, IdentifierList
from .Logging import get_logger
from .Name import Name, NameType, NameForm, NamePart, NamePartType, NamePartQualifier
from .Note import Note
from .OnlineAccount import OnlineAccount
from .Person import Person
from .PlaceDescription import PlaceDescription
from .PlaceReference import PlaceReference
from .Qualifier import Qualifier
from .Relationship import Relationship, RelationshipType
from .SourceCitation import SourceCitation
from .SourceDescription import SourceDescription, ResourceType
from .SourceReference import SourceReference, KnownSourceReference
#from .Subject import Subject
from .TextValue import TextValue
from .TopLevelTypeCollection import TopLevelTypeCollection
from .Resource import Resource, URI


import logging
from .LoggingHub import hub, ChannelConfig
log = logging.getLogger("gedcomx")
job_id = "gedcomx.convert.GEDCOM5x"

class GedcomConverter():
    def __init__(self) -> None:
        self.gedcomx = GedcomX()
        self.object_map: dict[Any, Any] = {-1:self.gedcomx}
        self.missing_handler_count = {}
    
    gedcom_even_to_fact = {
    # Person Fact Types
    "ADOP": FactType.Adoption,
    "CHR": FactType.AdultChristening,
    "EVEN": FactType.Amnesty,  # and other FactTypes with no direct GEDCOM tag
    "BAPM": FactType.Baptism,
    "BARM": FactType.BarMitzvah,
    "BASM": FactType.BatMitzvah,
    "BIRT": FactType.Birth,
    "BIRT, CHR": FactType.Birth,
    "BLES": FactType.Blessing,
    "BURI": FactType.Burial,
    "CAST": FactType.Caste,
    "CENS": FactType.Census,
    "CIRC": FactType.Circumcision,
    "CONF": FactType.Confirmation,
    "CREM": FactType.Cremation,
    "DEAT": FactType.Death,
    "EDUC": FactType.Education,
    "EMIG": FactType.Emigration,
    "FCOM": FactType.FirstCommunion,
    "GRAD": FactType.Graduation,
    "IMMI": FactType.Immigration,
    "MIL": FactType.MilitaryService,
    "NATI": FactType.Nationality,
    "NATU": FactType.Naturalization,
    "OCCU": FactType.Occupation,
    "ORDN": FactType.Ordination,
    "DSCR": FactType.PhysicalDescription,
    "PROB": FactType.Probate,
    "PROP": FactType.Property,
    "RELI": FactType.Religion,
    "RESI": FactType.Residence,
    "WILL": FactType.Will,

    # Couple Relationship Fact Types
    "ANUL": FactType.Annulment,
    "DIV": FactType.Divorce,
    "DIVF": FactType.DivorceFiling,
    "ENGA": FactType.Engagement,
    "MARR": FactType.Marriage,
    "MARB": FactType.MarriageBanns,
    "MARC": FactType.MarriageContract,
    "MARL": FactType.MarriageLicense,
    "SEPA": FactType.Separation,

    # Parent-Child Relationship Fact Types
    # (Note: Only ADOPTION has a direct GEDCOM tag, others are under "EVEN")
    "ADOP": FactType.AdoptiveParent
}
    
    gedcom_even_to_evnt = {
    # Person Fact Types
    "ADOP": EventType.Adoption,
    "CHR": EventType.AdultChristening,
    "BAPM": EventType.Baptism,
    "BARM": EventType.BarMitzvah,
    "BASM": EventType.BatMitzvah,
    "BIRT": EventType.Birth,
    "BIRT, CHR": EventType.Birth,
    "BLES": EventType.Blessing,
    "BURI": EventType.Burial,
    
    "CENS": EventType.Census,
    "CIRC": EventType.Circumcision,
    "CONF": EventType.Confirmation,
    "CREM": EventType.Cremation,
    "DEAT": EventType.Death,
    "EDUC": EventType.Education,
    "EMIG": EventType.Emigration,
    "FCOM": EventType.FirstCommunion,
    
    "IMMI": EventType.Immigration,
    
    "NATU": EventType.Naturalization,
    
    "ORDN": EventType.Ordination,
    

    # Couple Relationship Fact Types
    "ANUL": EventType.Annulment,
    "DIV": EventType.Divorce,
    "DIVF": EventType.DivorceFiling,
    "ENGA": EventType.Engagement,
    "MARR": EventType.Marriage
    
}
    

    def clean_str(self, text: str | None) -> str:
        # Regular expression to match HTML/XML tags
        if text is None or text.strip() == '':
            return ""
        clean_text = re.sub(r'<[^>]+>', '', text)
        
        return clean_text
    
    def parse_gedcom5x_recrod(self,record: Gedcom5xRecord):
        if record: 
            with hub.use(job_id):       
                handler_name = 'handle_' + record.tag.lower()
                
                if hasattr(self,handler_name): 
                    log.info(f'Parsing Record: {record.describe()}')         
                    handler = getattr(self,handler_name)            
                    handler(record)
                else:
                    if record.tag in self.missing_handler_count:
                        self.missing_handler_count[record.tag] += 1
                    else:
                        self.missing_handler_count[record.tag] = 1
                    
                    log.error(f'Failed Parsing Record: {record.describe()}')
                for sub_record in record.subRecords():
                    self.parse_gedcom5x_recrod(sub_record)
    
    def handle__apid(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].description.add_identifier(Identifier(value=[URI.from_url('APID://' + record.value if record.value else '')]))
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].add_identifier(Identifier(value=[URI.from_url('APID://' + record.value if record.value else '')]))
        else:
            raise ValueError(f"Could not handle '_APID' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle__meta(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text=self.clean_str(record.value if record.value else 'Warning: This NOTE had not content.'))
            self.object_map[record.level-1].add_note(gxobject)
            
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"Could not handle 'WWW' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

    def handle__wlnk(self, record: Gedcom5xRecord):
        return self.handle_sour(record)

    def handle_addr(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            # TODO CHeck if URL?
            if record.value is not None and self.clean_str(record.value):
                gxobject = Address(value=self.clean_str(record.value))
            else:
                gxobject = Address()
            self.object_map[record.level-1].address = gxobject
            
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"I do not know how to handle an 'ADDR' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr1(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR1' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr2(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street2 = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR2' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr3(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street3 = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR3' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr4(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street4 = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR4' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr5(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street5 = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR5' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_adr6(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].street5 = self.clean_str(record.value)        
        else:
            raise ValueError(f"I do not know how to handle an 'ADR6' tag for a {type(self.object_map[record.level-1])}")
        
    def handle_phon(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].phones.append(self.clean_str(record.value))        
        else:
            raise ValueError(f"I do not know how to handle an '{record.tag}' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_email(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].emails.append(self.clean_str(record.value))        
        else:
            raise ValueError(f"I do not know how to handle an '{record.tag}' tag for a {type(self.object_map[record.level-1])}")
    
    def handle_fax(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            if record.value is not None and self.clean_str(record.value):
                self.object_map[record.level-1].emails.append('FAX:' + (self.clean_str(record.value) if record.value is not None else ''))        
        else:
            raise ValueError(f"I do not know how to handle an '{record.tag}' tag for a {type(self.object_map[record.level-1])}")

    def handle_adop(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Adoption)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            return #TODO
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_auth(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            if record.value is not None and self.gedcomx.agents.byName(record.value):
                gxobject = self.gedcomx.agents.byName(record.value)[0]
            else:
                gxobject = Agent(names=[TextValue(record.value)])
                self.gedcomx.add_agent(gxobject)
            
            self.object_map[record.level-1].author = gxobject
            
            self.object_map[record.level] = gxobject
        else:
            
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_bapm(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Baptism)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_birt(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Birth)
            self.object_map[record.level-1].add_fact(gxobject)
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_buri(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Burial)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_caln(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].description.add_identifier(Identifier(value=[URI.from_url('Call Number:' + record.value if record.value else '')]))
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].add_identifier(Identifier(value=[URI.from_url('Call Number:' + record.value if record.value else '')]))
        elif isinstance(self.object_map[record.level-1], Agent):
            pass
            # TODO Why is GEDCOM so shitty? A callnumber for a repository?
        else:
            raise ValueError(f"Could not handle 'CALN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle_chan(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            date = record.subRecord('DATE')
            if  date is not None:
                self.object_map[record.level-1].created = Date(date[0].value)
        elif isinstance(self.object_map[record.level-1], Agent):
            if self.object_map[record.level-1].attribution is None:
                gxobject = Attribution()
                self.object_map[record.level-1].attribution = gxobject
                self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Person):
            if self.object_map[record.level-1].attribution is None:
                gxobject = Attribution()
                self.object_map[record.level-1].attribution = gxobject
                self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_chr(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Christening)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_city(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None:
                self.object_map[record.level-1].city = self.clean_str(record.value)
            else: raise ValueError('Record had no value')
        else:
            raise ValueError(f"I do not know how to handle an 'CITY' tag for a {type(self.object_map[record.level-1])}")
        
    def handle_conc(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Note):
            gxobject = self.clean_str(str(record.value))
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = str(record.value)
            self.object_map[record.level-1]._append_to_name(gxobject)
        elif isinstance(self.object_map[record.level-1], Qualifier):
            gxobject = str(record.value)
            self.object_map[record.level-2].append(gxobject)
        elif isinstance(self.object_map[record.level-1], TextValue):
            #gxobject = TextValue(value=self.clean_str(record.value))
            self.object_map[record.level-1]._append_to_value(record.value)
        elif isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].append(record.value)
        elif isinstance(self.object_map[record.level-1], Fact):
            self.object_map[record.level-1].notes[0].text += record.value
            
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_cont(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Note):
            gxobject = str("\n" + record.value if record.value else '')
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = str("\n" + record.value if record.value else '')
        elif isinstance(self.object_map[record.level-1], Qualifier):
            gxobject = str("\n" + record.value if record.value else '')
            self.object_map[record.level-1].append(gxobject)
        elif isinstance(self.object_map[record.level-1], TextValue):
            #gxobject = TextValue(value="\n" + record.value)
            self.object_map[record.level-1]._append_to_value(record.value if record.value else '\n')
        elif isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].append(record.value)
        elif isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1]._append(record.value)
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)
    
    def handle_crea(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            date = record.subRecord('DATE')
            if  date is not None and date != []:
                self.object_map[record.level-1].created = Date(original=date[0].value)
            else: raise ValueError('DATE had not value')                     
            
        elif isinstance(self.object_map[record.level-1], Agent):
            if self.object_map[record.level-1].attribution is None:
                gxobject = Attribution()
                self.object_map[record.level-1].attribution = gxobject
                
                self.object_map[record.level] = gxobject
            else:
                log.info(f"[{record.tag}] Attribution already exists for SourceDescription with id: {self.object_map[record.level-1].id}")
        else:
            raise ValueError(f"Could not handle '{record.tag}' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")
    
    def handle_ctry(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            if record.value is not None:
                self.object_map[record.level-1].country = self.clean_str(record.value)
            else:
                raise ValueError('Recrod had no value')
        else:
            raise ValueError(f"I do not know how to handle an '{record.tag}' tag for a {type(self.object_map[record.level-1])}")
     
    def handle_data(self, record: Gedcom5xRecord) -> None:
        if record.value != '' and record.value == 'None':
            assert False
        self.object_map[record.level] = self.object_map[record.level-1]

    def handle_date(self, record: Gedcom5xRecord):
        if record.parent is not None and record.parent.tag == 'PUBL':
            #gxobject = Date(original=record.value) #TODO Make a parser for solid timestamps
            #self.object_map[0].published = gxobject
            #self.object_map[0].published = date_to_timestamp(record.value) if record.value else None 
            self.object_map[0].published = record.value    
            #
            #self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Event):
            self.object_map[record.level-1].date = Date(original=record.value)
        elif isinstance(self.object_map[record.level-1], Fact):
            self.object_map[record.level-1].date = Date(original=record.value)
        elif record.parent is not None and record.parent.tag == 'DATA' and isinstance(self.object_map[record.level-2], SourceReference):
            gxobject = Note(text='Date: ' + record.value if record.value else '')
            self.object_map[record.level-2].description.add_note(gxobject)
            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            
            self.object_map[record.level-1].ctreated = record.value #TODO String to timestamp
        elif isinstance(self.object_map[record.level-1], Attribution):
            if record.parent is not None and record.parent.tag == 'CREA':
                self.object_map[record.level-1].created = record.value #TODO G7
            elif record.parent is not None and record.parent.tag == "CHAN":
                self.object_map[record.level-1].modified = record.value #TODO G7
        elif record.parent is not None and record.parent.tag in ['CREA','CHAN']:
            pass

        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_deat(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Death)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_even(self, record: Gedcom5xRecord):
        # TODO If events in a @S, check if only 1 person matches?
        if record.value and (not record.value.strip() == ''):
            values = [value.strip() for value in record.value.split(",")]
            for value in values:
                if value in self.gedcom_even_to_fact.keys():
                    if isinstance(self.object_map[record.level-1], Person):
                        gxobject = Fact(type=self.gedcom_even_to_fact[value])
                        self.object_map[record.level-1].add_fact(gxobject)

                        
                        self.object_map[record.level] = gxobject

                    elif isinstance(self.object_map[record.level-1], SourceDescription):
                        gxobject = Event(type=self.gedcom_even_to_evnt[value],sources=[self.object_map[record.level-1]])
                        self.gedcomx.add_event(gxobject)
                        
                        self.object_map[record.level] = gxobject
                    else:
                        log.warning(f"Could not convert EVEN '{value}' for object of type {type(self.object_map[record.level-1])} in record {record.describe()}")
                        return
                        raise TagConversionError(record=record,levelstack=self.object_map)
                        assert False
                        # TODO: Fix, this. making an event to cacth subtags, why are these fact tied to a source? GEDCOM is horrible
                        gxobject = Event(type=EventType.UNKNOWN)
                        
                        self.object_map[record.level] = gxobject
                else:
                    raise TagConversionError(record=record,levelstack=self.object_map)

        else:
            possible_fact = FactType.guess(record.subRecord('TYPE')[0].value)
            if possible_fact:
                gxobject = Fact(type=possible_fact)
                self.object_map[record.level-1].add_fact(gxobject)

                
                self.object_map[record.level] = gxobject
                return
            elif EventType.guess(record.subRecord('TYPE')[0].value):
                if isinstance(self.object_map[record.level-1], Person):
                    gxobject = Event(type=EventType.guess(record.subRecord('TYPE')[0].value), roles=[EventRole(person=self.object_map[record.level-1], type=EventRoleType.Principal)])
                    self.gedcomx.add_event(gxobject)
                    
                    self.object_map[record.level] = gxobject
                return
            else:
                if isinstance(self.object_map[record.level-1], Person):
                    gxobject = Event(type=None, roles=[EventRole(person=self.object_map[record.level-1], type=EventRoleType.Principal)])
                    gxobject.add_note(Note(subject='Event', text=record.value))
                    self.gedcomx.add_event(gxobject)
                    
                    self.object_map[record.level] = gxobject
                    return
                    
                else:
                    assert False

    def handle_exid(self,record: Gedcom5xRecord):
        if record.value:
            gxobject = Identifier(type=IdentifierType.External,value=[URI(record.value) if record.value else URI()]) # type: ignore
            self.object_map[record.level-1].add_identifier(gxobject)       
            self.object_map[record.level] = gxobject
        else: raise ValueError('Record had no value')

    def handle_fam(self, record: Gedcom5xRecord) -> None:
        if record.tag != 'FAM' or record.level != 0:
            raise ValueError("Invalid record: Must be a level 0 FAM record")

        husband, wife, children = None, None, []

        husband_record = record.subRecords('HUSB')
        if husband_record is not None:
            id = husband_record[0].xref if len(husband_record) > 0 else None
            if id:
                husband = self.gedcomx.get_person_by_id(id)

        wife_record = record.subRecords('WIFE')
        if wife_record:
            id = wife_record[0].xref if len(wife_record) > 0 else None
            if id:
                wife = self.gedcomx.get_person_by_id(id)

        children_records = record.subRecords('CHIL')
        if children_records:
            for child_record in children_records:
                id = child_record.xref
                if id:
                    child = self.gedcomx.get_person_by_id(id)
                    if child:
                        children.append(child)

        if husband:
            for child in children:
                relationship = Relationship(person1=husband, person2=child, type=RelationshipType.ParentChild)
                self.gedcomx.add_relationship(relationship)
        if wife:
            for child in children:
                relationship = Relationship(person1=wife, person2=child, type=RelationshipType.ParentChild)
                self.gedcomx.add_relationship(relationship)
        if husband and wife:
            relationship = Relationship(person1=husband, person2=wife, type=RelationshipType.Couple)
            self.gedcomx.add_relationship(relationship)

    def handle_famc(self, record: Gedcom5xRecord) -> None:
        return

    def handle_fams(self, record: Gedcom5xRecord) -> None:
        return

    def handle_file(self, record: Gedcom5xRecord):
        if record.value and record.value.strip() != '':
            #raise ValueError(f"I did not expect the 'FILE' tag to have a value: {record.value}")
            #TODO Handle files referenced here
            ...
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            ...
        self.object_map[record.level-1].resourceType = ResourceType.DigitalArtifact
           
    def handle_form(self, record: Gedcom5xRecord):
        if record.parent is not None and record.parent.tag == 'FILE' and isinstance(self.object_map[record.level-2], SourceDescription):
            if record.value and record.value.strip() != '':
                mime_type, _ = mimetypes.guess_type('placehold.' + record.value)
                if mime_type:
                    self.object_map[record.level-2].mediaType = mime_type
                else:
                    print(f"Could not determing mime type from {record.value}")
        elif isinstance(self.object_map[record.level-1], PlaceDescription):
            self.object_map[record.level-1].names.append(TextValue(value=record.value))
        elif record.parent is not None and record.parent.tag == 'TRAN':
            pass #TODO
        else:
            log.error(f"raise TagConversionError(record=record,levelstack=self.object_map")

    def handle_givn(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Name):
            given_name = NamePart(value=record.value, type=NamePartType.Given)
            self.object_map[record.level-1]._add_name_part(given_name)
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_indi(self, record: Gedcom5xRecord):
        person = self.gedcomx.persons.byId(record.xref)
        if person is None:
            log.warning('Had to create person with id {recrod.xref}')
            if isinstance(record.xref,str):
                person = Person(id=record.xref.replace('@',''))
            else:
                raise ValueError('INDI Record had no XREF')
        self.gedcomx.add_person(person) 
        self.object_map[record.level] = person

    def handle_immi(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Immigration)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_marr(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Marriage)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_name(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Name.simple(record.value if record.value else 'WARNING: NAME had no value')
            #gxobject = Name(nameForms=[NameForm(fullText=record.value)], type=NameType.BirthName)
            self.object_map[record.level-1].add_name(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = TextValue(value=record.value)
            self.object_map[record.level-1].add_name(gxobject)
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_note(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text=self.clean_str(record.value))
            self.object_map[record.level-1].add_note(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], SourceReference):
            gxobject = Note(text=self.clean_str(record.value))
            self.object_map[record.level-1].description.add_note(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Conclusion):
            gxobject = Note(text=record.value)
            self.object_map[record.level-1].add_note(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = Note(text=record.value)
            self.object_map[record.level-1].add_note(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Attribution):
            if self.object_map[record.level-1].changeMessage is None:
                self.object_map[record.level-1].changeMessage = record.value
            else:
                self.object_map[record.level-1].changeMessage = self.object_map[record.level-1].changeMessage + '' + record.value
        elif isinstance(self.object_map[record.level-1], Note):
            gxobject = Note(text=self.clean_str(record.value))
            self.object_map[record.level-2].add_note(gxobject)

            
            self.object_map[record.level] = gxobject

        else:
            raise ValueError(f"Could not handle 'NOTE' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")
            assert False

    def handle_nsfx(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Name):
            surname = NamePart(value=record.value, type=NamePartType.Suffix)
            self.object_map[record.level-1]._add_name_part(surname)
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_occu(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Occupation)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_obje(self, record: Gedcom5xRecord):
        self.handle_sour(record)

    def handle_page(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceReference):
            self.object_map[record.level-1].descriptionId = record.value
            gx_object = KnownSourceReference(name=KnownSourceReference.Page,value=record.value)
            self.object_map[record.level-1].add_qualifier(gx_object)
            self.object_map[record.level] = self.object_map[record.level-1]
        else:
            raise ValueError(f"Could not handle 'PAGE' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

    def handle_plac(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            gxobject = Address(value=record.value)
            self.object_map[record.level-1].add_address(gxobject)

            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Event):
            if self.gedcomx.places.byName(record.value):
                self.object_map[record.level-1].place = PlaceReference(original=record.value, description=self.gedcomx.places.byName(record.value)[0])
            else:
                place_des = PlaceDescription(names=[TextValue(value=record.value)])
                self.gedcomx.add_place_description(place_des)
                self.object_map[record.level-1].place = PlaceReference(original=record.value, description=place_des)
                if len(record.subRecords()) > 0:
                    self.object_map[record.level]= place_des

        elif isinstance(self.object_map[record.level-1], Fact):
            if self.gedcomx.places.byName(record.value):
                self.object_map[record.level-1].place = PlaceReference(original=record.value, description=self.gedcomx.places.byName(record.value)[0])
            else:
                place_des = PlaceDescription(names=[TextValue(value=record.value)])
                self.gedcomx.add_place_description(place_des)
                self.object_map[record.level-1].place = PlaceReference(original=record.value, description=place_des)
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Note(text='Place: ' + record.value if record.value else 'WARNING: NOTE had no value')
            self.object_map[record.level-1].add_note(gxobject)
            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_post(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].postalCode = self.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'POST' tag for a {type(self.object_map[record.level-1])}")   
    
    def handle_publ(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            if record.value and self.gedcomx.agents.byName(record.value):
                gxobject = self.gedcomx.agents.byName(record.value)[0]
            else:
                gxobject = Agent(names=[TextValue(record.value)])
                self.gedcomx.add_agent(gxobject)
            self.object_map[record.level-1].publisher = gxobject

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_prob(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Probate)
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_uid(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            gxobject = Identifier(value=[URI('UID:' + record.value)] if record.value else [URI('WARNING: NOTE had no value')],type=IdentifierType.Primary) # type: ignore
            self.object_map[record.level-1].add_identifier(gxobject) #NOTE GC7
            
            self.object_map[record.level] = gxobject

    def handle_refn(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person) or isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Identifier(value=[URI.from_url('Reference Number:' + record.value)] if record.value else [])
            self.object_map[record.level-1].add_identifier(gxobject)
            
            self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], Agent):
            gxobject = Identifier(value=[URI('Reference Number:' + record.value)] if record.value else [])
            self.object_map[record.level-1].add_identifier(gxobject) #NOTE GC7
            
            self.object_map[record.level] = gxobject
        else:
            raise ValueError(f"Could not handle 'REFN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")

    def handle_repo(self, record: Gedcom5xRecord):

        if record.level == 0:
            
            gxobject = Agent(id=record.xref)
            self.gedcomx.add_agent(gxobject)
            
            self.object_map[record.level] = gxobject
            
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            if self.gedcomx.agents.byId(record.xref) is not None:
                
                # TODO WHere and what to add this to?
                gxobject = self.gedcomx.agents.byId(record.xref)
                self.object_map[record.level-1].repository = gxobject
                self.object_map[record.level] = gxobject

            else:
                print("handle_repo",record.describe())
                raise ValueError()
                gxobject = Agent(names=[TextValue(record.value)])
        else:
            raise ValueError(f"I do not know how to handle 'REPO' tag that is not a top-level, or sub-tag of {type(self.object_map[record.level-1])}")
            

        
        self.object_map[record.level] = gxobject

    def handle_resi(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Person):
            gxobject = Fact(type=FactType.Residence)
            if record.value and record.value.strip() != '':
                gxobject.add_note(Note(text=record.value))
            self.object_map[record.level-1].add_fact(gxobject)

            
            self.object_map[record.level] = gxobject
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_rin(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            self.object_map[record.level-1].id = record.value
            self.object_map[record.level-1].add_note(Note(text=f"Source had RIN: of {record.value}"))

        else:
            raise ValueError(f"Could not handle 'RIN' tag in record {record.describe()}, last stack object {type(self.object_map[record.level-1])}")
        
    def handle_sex(self, record: Gedcom5xRecord):
        
        if isinstance(self.object_map[record.level-1], Person):
            if record.value == 'M':
                gxobject = Gender(type=GenderType.Male)
            elif record.value == 'F':
                gxobject = Gender(type=GenderType.Female)
            else:
                gxobject = Gender(type=GenderType.Unknown)
            self.object_map[record.level-1].gender = gxobject
            
            
            self.object_map[record.level] = gxobject
        else:
            assert False

    def handle_sour(self, record: Gedcom5xRecord):
        if record.level == 0 or record.tag == '_WLNK' or (record.level == 0 and record.tag == 'OBJE'):
            source_description = SourceDescription(id=record.xref.replace('@','') if record.xref else None)
            self.gedcomx.add_source_description(source_description)
            
            self.object_map[record.level] = source_description
        else:
            # This 'SOUR' is a SourceReference
            if record.xref is None or record.xref.strip() == '':
                log.warning(f"SOUR points to nothing: {record.describe()}")
                return False
            if self.gedcomx.source_descriptions.byId(record.xref):
                gxobject = SourceReference(descriptionId=record.xref, description=self.gedcomx.source_descriptions.byId(record.xref))
            else:
                log.warning(f'Could not find source with id: {record.xref}')
                source_description = SourceDescription(id=record.xref)
                gxobject = SourceReference(descriptionId=record.value, description=source_description)
            if isinstance(self.object_map[record.level-1],SourceReference):
                self.object_map[record.level-1].description.add_source(gxobject)
            elif record.parent is not None and record.parent.tag in ['NOTE']:
                pass
            else:
                self.object_map[record.level-1].add_source(gxobject)
            
            self.object_map[record.level] = gxobject
          
    def handle_stae(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Address):
            self.object_map[record.level-1].stateOrProvince = self.clean_str(record.value)
        else:
            raise ValueError(f"I do not know how to handle an 'STAE' tag for a {type(self.object_map[record.level-1])}")
        
    def handle_surn(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Name):
            surname = NamePart(value=record.value, type=NamePartType.Surname)
            self.object_map[record.level-1]._add_name_part(surname)
        else:
            raise TagConversionError(record=record,levelstack=self.object_map)

    def handle_text(self, record: Gedcom5xRecord):
        if record.parent is not None and record.parent.tag == 'DATA':
            if isinstance(self.object_map[record.level-2], SourceReference):
                gxobject = TextValue(value=record.value)
                self.object_map[record.level-2].description.add_description(gxobject)
                
                self.object_map[record.level] = gxobject
        elif isinstance(self.object_map[record.level-1], SourceDescription):
            gxobject = Document(text=record.value)
            self.object_map[record.level-1].analysis = gxobject
        else:
            assert False

    def handle_titl(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], SourceDescription):
            
            gxobject = TextValue(value=self.clean_str(record.value))
            self.object_map[record.level-1].add_title(gxobject)

            
            self.object_map[record.level] = gxobject
        
        elif record.parent is not None and record.parent.tag == 'FILE' and isinstance(self.object_map[record.level-2], SourceDescription):
            gxobject = TextValue(value=record.value)
            self.object_map[record.level-2].add_title(gxobject)

            
            self.object_map[record.level] = gxobject
        elif self.object_map[record.level] and isinstance(self.object_map[record.level], Name):
            gxobject = NamePart(value=record.value, qualifiers=[NamePartQualifier.Title])

            self.object_map[record.level]._add_name_part(gxobject)
        else:
            log.error(f"raise TagConversionError(record=record,levelstack=self.object_map)")

    def handle_tran(self, record: Gedcom5xRecord):
        pass

    def handle_type(self, record: Gedcom5xRecord):
        # peek to see if event or fact
        if isinstance(self.object_map[record.level-1], Event):
            if EventType.guess(record.value):
                self.object_map[record.level-1].type = EventType.guess(record.value)                
            else:
                log.warning(f"Could not determine type of event with value '{record.value}'")  
                assert False            
                self.object_map[record.level-1].type = None
            self.object_map[record.level-1].add_note(Note(text=self.clean_str(record.value)))
        elif isinstance(self.object_map[record.level-1], Fact):
            if not self.object_map[record.level-1].type:
                self.object_map[0].type = FactType.guess(record.value)
        elif isinstance(self.object_map[record.level-1], Identifier):
            
            self.object_map[record.level-1].values.append(self.clean_str(record.value))
            self.object_map[record.level-1].type = IdentifierType.Other # type: ignore

        elif record.parent is not None and record.parent.tag == 'FORM':
            if not self.object_map[0].mediaType:
                self.object_map[0].mediaType = record.value

        else:
            raise ValueError(f"I do not know how to handle 'TYPE' tag for {type(self.object_map[record.level-1])}")

    def handle__url(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-2], SourceDescription):
            self.object_map[record.level-2].about = URI.from_url(record.value) if record.value else None
        else:
            raise ValueError(f"Could not handle '_URL' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")
            
    def handle_www(self, record: Gedcom5xRecord):
        if isinstance(self.object_map[record.level-1], Agent):
            self.object_map[record.level-1].homepage = self.clean_str(record.value)
        elif isinstance(self.object_map[record.level-2], SourceReference):
            self.object_map[record.level-2].description.add_identifier(Identifier(value=[URI.from_url(record.value)] if record.value else []))
        else:
            raise ValueError(f"Could not handle 'WWW' tag in record {record.describe()}, last stack object {self.object_map[record.level-1]}")

    def Gedcom5x_GedcomX(self, gedcom5x: Gedcom5x):
        print(f'Parsing GEDCOM Version {gedcom5x.version}')
        individual_ids = set()
        source_ids = set()
        repository_ids = set()
        family_ids = set()

        if gedcom5x:
            for individual in gedcom5x.individuals:
                individual_ids.add(individual.xref)
                gx_obj = Person(id=individual.xref)
                self.gedcomx.add_person(gx_obj)
                
        
            for source in gedcom5x.sources:
                source_ids.add(source.xref)
                gx_obj = SourceDescription(id=source.xref)
                self.gedcomx.add_source_description(gx_obj)
            
            for source in gedcom5x.repositories:
                repository_ids.add(source.xref)
                gx_obj = Agent(id=source.xref)
                self.gedcomx.add_agent(gx_obj)
            
            for family in gedcom5x.families:
                family_ids.add(family.xref)
                self.handle_fam(family)
            
            # Now Parse Zero Level Recrods
            for individual in gedcom5x.individuals:
                self.parse_gedcom5x_recrod(individual)

        return self.gedcomx
