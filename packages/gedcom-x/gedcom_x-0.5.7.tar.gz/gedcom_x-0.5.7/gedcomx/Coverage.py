from typing import Optional

from .Date import Date
from .PlaceReference import PlaceReference


class Coverage:
    identifier = 'http://gedcomx.org/v1/Coverage'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,spatial: Optional[PlaceReference], temporal: Optional[Date]) -> None:
        self.spatial = spatial
        self.temporal = temporal    
    
    # ...existing code...

    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.spatial:
            type_as_dict['spatial'] = getattr(self.spatial, '_as_dict_', self.spatial)
        if self.temporal:  # (fixed: no space after the dot)
            type_as_dict['temporal'] = getattr(self.temporal, '_as_dict_', self.temporal)
        return Serialization.serialize_dict(type_as_dict) 

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Coverage instance from a JSON-dict (already parsed).
        """
        from .PlaceReference import PlaceReference
        from .Date import Date

        spatial = PlaceReference._from_json_(data.get('spatial')) if data.get('spatial') else None
        temporal = Date._from_json_(data.get('temporal')) if data.get('temporal') else None
        return cls(spatial=spatial, temporal=temporal)