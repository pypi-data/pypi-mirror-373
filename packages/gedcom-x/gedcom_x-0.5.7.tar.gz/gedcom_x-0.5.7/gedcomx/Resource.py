from typing import Optional

"""
======================================================================
 Project: Gedcom-X
 File:    Resource.py
 Author:  David J. Cartwright
 Purpose: References TopLevel Types for Serialization

 Created: 2025-08-25
 Updated:
   - 2025-08-31: working on target=Resource and deserialization issues
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""

from .URI import URI
    
class Resource:
    """
    Class used to track and resolve URIs and references between datastores.

    Parameters
    ----------
    
    Raises
    ------
    ValueError
        If `id` is not a valid UUID.
    """
    # TODO, Deal with a resouce being passed, as it may be unresolved.
    def __init__(self,uri: Optional[URI|str] = None, id:Optional[str] = None,top_lvl_object: Optional[object] = None,target= None) -> None:
        
        self.resource = URI.from_url(uri.value) if isinstance(uri,URI) else URI.from_url(uri) if isinstance(uri,str) else None
        self.Id = id

        self.type = None
        self.resolved = False
        self.target: object = target
        self.remote: bool | None = None    # is the resource pointed to persitent on a remote datastore?

        if target:
            if isinstance(target,Resource):
                self.resource = target.resource
                self.Id = target.Id
                self.target = target.target
            else:
                self.resource = target.uri
                self.Id = target.id
                self.type = type(target)
   
    @property
    def uri(self):
        return self.resource
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        typ_as_dict = {}
        if self.resource:
            typ_as_dict['resource'] = self.resource.value if self.resource else None
        if self.Id:
            typ_as_dict['resourceId'] = self.Id
        return Serialization.serialize_dict(typ_as_dict)
    
    @classmethod
    def _from_json_(cls,data):
        # TODO This is not used but taken care of in Serialization
        r = Resource(uri=data.get('resource'),id=data.get('resourceId',None))
        #return r

    def __repr__(self) -> str:
        return f"Resource(uri={self.resource}, id={self.Id}, target={self.target})"
    
    def __str__(self) -> str:
        return f"{self.resource}{f', id={self.Id}' if self.Id else ''}"
    


