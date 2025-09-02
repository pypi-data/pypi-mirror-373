DEBUG = False

import json
import random
import string

from typing import Any, Dict, Optional

"""
======================================================================
 Project: Gedcom-X
 File:    GedcomX.py
 Author:  David J. Cartwright
 Purpose: Object for working with Gedcom-X Data

 Created: 2025-07-25
 Updated:
   - 2025-08-31: _as_dict_ to only create entries in dict for fields that hold data,
    id_index functionality, will be used for resolution of Resources
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .Agent import Agent
from .Attribution import Attribution
from .Document import Document
from .Event import Event
from .Group import Group
from .Identifier import make_uid
from .Logging import get_logger
from .Person import Person
from .PlaceDescription import PlaceDescription
from .Relationship import Relationship, RelationshipType
from .Resource import Resource, URI
from .SourceDescription import ResourceType, SourceDescription
from .TextValue import TextValue
#=====================================================================


def TypeCollection(item_type):
    """
    Factory that creates a typed, indexable collection for a specific model class.

    The returned object behaves like:
      - a container (append/remove, __len__, __getitem__)
      - an iterator (for item in collection)
      - a simple query helper via __call__(**field_equals)
      - a small in-memory index on id, name (see note), and uri

    Parameters
    ----------
    item_type : type
        The class/type that items in this collection must be instances of.

    Returns
    -------
    Collection
        A new, empty collection instance specialized for `item_type`.

    Notes
    -----
    - Name indexing is currently disabled (see TODO in `_update_indexes`).
    - The collection auto-assigns/normalizes an item's `uri.path` based on `item_type`.
    """
    class Collection:
        def __init__(self):
            self._items = []
            self._id_index = {}
            self._name_index = {}
            self._uri_index = {}
            self.uri = URI(path=f'/{item_type.__name__}s/')

        def __iter__(self):
            self._index = 0
            return self

        def __next__(self):
            if self._index < len(self._items):
                result = self._items[self._index]
                self._index += 1
                return result
            else:
                raise StopIteration

        @property
        def item_type(self):
            return item_type
        
        def _update_indexes(self, item):
            # Update the id index
            if hasattr(item, 'id'):
                self._id_index[item.id] = item
            
            try:
                if hasattr(item, 'uri'):
                    self._uri_index[item.uri.value] = item
            except AttributeError as e:
                print(f"type{item}")
                assert False

            # Update the name index
            ''' #TODO Fix name handling on persons
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    print(name._as_dict_)
                    name_value = name.value if isinstance(name, TextValue) else name
                    if name_value in self._name_index:
                        self._name_index[name_value].append(item)
                    else:
                        self._name_index[name_value] = [item]
            '''
        @property
        def id_index(self):
            return self._id_index
        
        def _remove_from_indexes(self, item):
            # Remove from the id index
            if hasattr(item, 'id'):
                if item.id in self._id_index:
                    del self._id_index[item.id]

            # Remove from the name index
            if hasattr(item, 'names'):
                names = getattr(item, 'names')
                for name in names:
                    name_value = name.value if isinstance(name, TextValue) else name
                    if name_value in self._name_index:
                        if item in self._name_index[name_value]:
                            self._name_index[name_value].remove(item)
                            if not self._name_index[name_value]:
                                del self._name_index[name_value]

        def byName(self, sname: str | None):
            # Use the name index for fast lookup
            if sname:
                sname = sname.strip()
                return self._name_index.get(sname, [])
            return []

        def byId(self, id):
            # Use the id index for fast lookup
            return self._id_index.get(id, None)
        
        def byUri(self, uri):
            # Use the id index for fast lookup
            return self._uri_index.get(uri.value, None)

        def append(self, item):
            if not isinstance(item, item_type):
                raise TypeError(f"Expected item of type {item_type.__name__}, got {type(item).__name__}")
            if item.uri:
                item.uri.path  = f'{str(item_type.__name__)}s' if (item.uri.path is None or item.uri.path == "") else item.uri.path
            else:
                item.uri = URI(path=f'/{item_type.__name__}s/',fragment=item.id)
                
            self._items.append(item)
            self._update_indexes(item)

        def remove(self, item):
            if item not in self._items:
                raise ValueError("Item not found in the collection.")
            self._items.remove(item)
            self._remove_from_indexes(item)

        def __repr__(self):
            return f"Collection({self._items!r})"
        
        def list(self):
            for item in self._items:
                print(item)
        
        def __call__(self, **kwargs):
            results = []
            for item in self._items:
                match = True
                for key, value in kwargs.items():
                    if not hasattr(item, key) or getattr(item, key) != value:
                        match = False
                        break
                if match:
                    results.append(item)
            return results
        
        def __len__(self):
            return len(self._items)
        
        def __getitem__(self, index):
            return self._items[index]
    
        @property
        def _items_as_dict(self) -> dict:
            return {f'{str(item_type.__name__)}s':  [item._as_dict_ for item in self._items]}

        @property
        def _as_dict_(self):
            return {f'{str(item_type.__name__).lower()}s': [item._as_dict_ for item in self._items]}     

        @property
        def json(self) -> str:
            
            return json.dumps(self._as_dict_, indent=4)    

    return Collection()

class GedcomX:
    """
    Main GedcomX Object representing a Genealogy. Stores collections of Top Level Gedcom-X Types.
    complies with GEDCOM X Conceptual Model V1 (http://gedcomx.org/conceptual-model/v1)

    Parameters
    ----------
    id : str
        Unique identifier for this Genealogy.
    attribution : Attribution Object
        Attribution information for the Genealogy
    filepath : str
        Not Implimented.
    description : str
        Description of the Genealogy: ex. 'My Family Tree'

    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] = None,
                 attribution: Optional[Attribution] = None,
                 filepath: Optional[str] = None,
                 description: Optional[str] = None) -> None:
        
        self.id = id
        self.attribution = attribution
        self._filepath = None
        
        self.description = description
        self.source_descriptions = TypeCollection(SourceDescription)
        self.persons = TypeCollection(Person)
        self.relationships = TypeCollection(Relationship)      
        self.agents = TypeCollection(Agent)
        self.events = TypeCollection(Event)
        self.documents = TypeCollection(Document)
        self.places = TypeCollection(PlaceDescription)
        self.groups = TypeCollection(Group)

        self.relationship_table = {}

        self.default_id_generator = make_uid

    @property
    def contents(self):
        return {
            "source_descriptions": len(self.source_descriptions),
            "persons": len(self.persons),
            "relationships": len(self.relationships),
            "agents": len(self.agents),
            "events": len(self.events),
            "documents": len(self.documents),
            "places": len(self.places),
            "groups": len(self.groups),
        }
            
    def add(self,gedcomx_type_object):
        if gedcomx_type_object:
            if isinstance(gedcomx_type_object,Person):
                self.add_person(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,SourceDescription):
                self.add_source_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Agent):
                self.add_agent(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,PlaceDescription):
                self.add_place_description(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Event):
                self.add_event(gedcomx_type_object)
            elif isinstance(gedcomx_type_object,Relationship):
                self.add_relationship(gedcomx_type_object)
            else:
                raise ValueError(f"I do not know how to add an Object of type {type(gedcomx_type_object)}")
        else:
            Warning("Tried to add a None type to the Geneology")

    def add_source_description(self,sourceDescription: SourceDescription):
        if sourceDescription and isinstance(sourceDescription,SourceDescription):
            if sourceDescription.id is None:
                sourceDescription.id =self.default_id_generator()
            self.source_descriptions.append(item=sourceDescription)
            self.lastSourceDescriptionAdded = sourceDescription
        else:
            raise ValueError(f"When adding a SourceDescription, value must be of type SourceDescription, type {type(sourceDescription)} was provided")

    def add_person(self,person: Person):
        """Add a Person object to the Genealogy

        Args:
            person: Person Object

        Returns:
            None

        Raises:
            ValueError: If `person` is not of type Person.
        """
        if person and isinstance(person,Person):
            if person.id is None:
                person.id =self.make_id()
            self.persons.append(item=person)
        else:
            raise ValueError(f'person must be a Person Object not type: {type(person)}')
        
    def add_relationship(self,relationship: Relationship):
        if relationship and isinstance(relationship,Relationship):
            if isinstance(relationship.person1,Resource) and isinstance(relationship.person2,Resource):
                print("Adding unresolved Relationship")
                self.relationships.append(relationship)
                return
            elif isinstance(relationship.person1,Person) and isinstance(relationship.person2,Person):

                if relationship.person1:
                    if relationship.person1.id is None:
                        relationship.person1.id = self.make_id()
                    if not self.persons.byId(relationship.person1.id):
                        self.persons.append(relationship.person1)
                    if relationship.person1.id not in self.relationship_table:
                        self.relationship_table[relationship.person1.id] = []
                    self.relationship_table[relationship.person1.id].append(relationship)
                    relationship.person1._add_relationship(relationship)
                else:
                    pass
                
                if relationship.person2:
                    if relationship.person2.id is None:
                        relationship.person2.id = self.make_id() #TODO
                    if not self.persons.byId(relationship.person2.id):
                        self.persons.append(relationship.person2)
                    if relationship.person2.id not in self.relationship_table:
                        self.relationship_table[relationship.person2.id] = []
                    self.relationship_table[relationship.person2.id].append(relationship)
                    relationship.person2._add_relationship(relationship)
                else:
                    pass

                self.relationships.append(relationship)
        else:
            raise ValueError()
    
    def add_place_description(self,placeDescription: PlaceDescription):
        if placeDescription and isinstance(placeDescription,PlaceDescription):
            if placeDescription.id is None:
                Warning("PlaceDescription has no id")
            self.places.append(placeDescription)

    def add_agent(self,agent: Agent):
        """Add a Agent object to the Genealogy

        Args:
            agent: Agent Object

        Returns:
            None

        Raises:
            ValueError: If `agent` is not of type Agent.
        """
        if agent and isinstance(agent,Agent):
            if agent in self.agents:
                return
            if agent.id is None:
                agent.id = make_uid()
            if self.agents.byId(agent.id):
                pass #TODO Deal with duplicates
                #raise ValueError
            self.agents.append(agent)
    
    def add_event(self,event_to_add: Event):
        if event_to_add and isinstance(event_to_add,Event):
            if event_to_add.id is None: event_to_add.id = make_uid()
            for current_event in self.events:
                if event_to_add == current_event:
                    print("DUPLICATE EVENT")
                    print(event_to_add._as_dict_)
                    print(current_event._as_dict_)
                    return
            self.events.append(event_to_add)
        else:
            raise ValueError

    def get_person_by_id(self,id: str):
        filtered = [person for person in self.persons if getattr(person, 'id') == id]
        if filtered: return filtered[0]
        return None
    
    def source(self,id: str):
        filtered = [source for source in self.source_descriptions if getattr(source, 'id') == id]
        if filtered: return filtered[0]
        return None        

    @property
    def id_index(self):
        combined = {**self.source_descriptions.id_index,
                    **self.persons.id_index,
                    **self.relationships.id_index,
                    **self.agents.id_index,
                    **self.events.id_index,
                    **self.documents.id_index,
                    **self.places.id_index,
                    **self.groups.id_index
        }
        for i in combined.keys():
            combined[i] = str(type(combined[i]).__name__)
        return combined

    @property
    def _as_dict(self) -> dict[str, Any]:
        type_as_dict: Dict[str, Any] = {}

        if self.persons and len(self.persons) > 0:
            type_as_dict["persons"] = [person._as_dict_ for person in self.persons]

        if self.source_descriptions:
            type_as_dict["sourceDescriptions"] = [
                sd._as_dict_ for sd in self.source_descriptions
            ]

        if self.relationships:
            type_as_dict["relationships"] = [
                rel._as_dict_ for rel in self.relationships
            ]

        if self.agents:
            type_as_dict["agents"] = [agent._as_dict_ for agent in self.agents]

        if self.events:
            type_as_dict["events"] = [event._as_dict_ for event in self.events]

        if self.places:
            type_as_dict["places"] = [place._as_dict_ for place in self.places]

        if self.documents:
            type_as_dict["documents"] = [doc._as_dict_ for doc in self.documents]

        return type_as_dict

    @property
    def json(self):
        """
        JSON Representation of the GedcomX Genealogy.

        Returns:
            str: JSON Representation of the GedcomX Genealogy in the GEDCOM X JSON Serialization Format
        """
        gedcomx_json = {
            'persons': [person._as_dict_ for person in self.persons],
            'sourceDescriptions' : [sourceDescription._as_dict_ for sourceDescription in self.source_descriptions],
            'relationships': [relationship._as_dict_ for relationship in self.relationships],
            'agents': [agent._as_dict_ for agent in self.agents],
            'events': [event._as_dict_ for event in self.events],
            'places': [place._as_dict_ for place in self.places],
            'documents': [document._as_dict_ for document in self.documents],
        }
        return json.dumps(gedcomx_json, indent=4)

    @staticmethod
    def from_json(data: dict):
        from .Serialization import Serialization
        gx = GedcomX()
        
        source_descriptions = data.get('sourceDescriptions', [])
        for source in source_descriptions:
            gx.add_source_description(Serialization.deserialize(source,SourceDescription))     
        
        persons = data.get('persons', [])
        for person in persons:
            gx.add_person(Serialization.deserialize(person,Person))
        
        relationships = data.get('relationships', [])
        for relationship in relationships:
            gx.add_relationship(Serialization.deserialize(relationship,Relationship))
        
        agents = data.get('agents', [])
        for agent in agents:
            gx.add_agent(Serialization.deserialize(agent,Agent))

        events = data.get('events', [])
        for event in events:
            gx.add_event(Serialization.deserialize(event,Event))
        
        return gx
        
    @staticmethod
    def make_id(length: int = 12) -> str:
        """Generate a random alphanumeric ID of given length."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(random.choices(alphabet, k=length))