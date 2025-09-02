from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .SourceDescription import SourceDescription

from .Attribution import Attribution
from .Qualifier import Qualifier

from .Resource import Resource

from .URI import URI

from collections.abc import Sized

class KnownSourceReference(Qualifier):
    CharacterRegion = "http://gedcomx.org/CharacterRegion"
    RectangleRegion = "http://gedcomx.org/RectangleRegion"
    TimeRegion = "http://gedcomx.org/TimeRegion"
    Page = "http://gedcomx.org/Page"
    
    @property
    def description(self):
        descriptions = {
            self.CharacterRegion: (
                "A region of text in a digital document, in the form of a,b where a is the index of the start "
                "character and b is the index of the end character. The meaning of this qualifier is undefined "
                "if the source being referenced is not a digital document."
            ),
            self.RectangleRegion: (
                "A rectangular region of a digital image. The value of the qualifier is interpreted as a series "
                "of four comma-separated numbers. If all numbers are less than 1, it is interpreted as x1,y1,x2,y2, "
                "representing percentage-based coordinates of the top-left and bottom-right corners. If any number is "
                "more than 1, it is interpreted as x,y,w,h where x and y are coordinates in pixels, and w and h are "
                "the width and height of the rectangle in pixels."
            ),
            self.TimeRegion: (
                "A region of time in a digital audio or video recording, in the form of a,b where a is the starting "
                "point in milliseconds and b is the ending point in milliseconds. This qualifier's meaning is undefined "
                "if the source is not a digital audio or video recording."
            ),
            self.Page: (
                "A single page in a multi-page document, represented as a 1-based integer. This always references the "
                "absolute page number, not any custom page number. This qualifier is undefined if the source is not a "
                "multi-page document."
            )
        }
        return descriptions.get(self, "No description available.")
    
class SourceReference:
    identifier = 'http://gedcomx.org/v1/SourceReference'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self,
                 description: URI | SourceDescription | None = None,
                 descriptionId: Optional[str] = None,
                 attribution: Optional[Attribution] = None,
                 qualifiers: Optional[List[Qualifier]] = None
                 ) -> None:
        
        self.description = description
        self.descriptionId = descriptionId
        self.attribution = attribution
        self.qualifiers = qualifiers if qualifiers and isinstance(qualifiers, list) else [] 

    def add_qualifier(self, qualifier: Qualifier):
        if isinstance(qualifier, (Qualifier,KnownSourceReference)):
            if self.qualifiers:
                #TODO Prevent Duplicates
                for current_qualifier in self.qualifiers:
                    if qualifier == current_qualifier:
                        return
            self.qualifiers.append(qualifier)
            return
        raise ValueError("The 'qualifier' must be type 'Qualifier' or 'KnownSourceReference', not " + str(type(qualifier))) 
    
    def append(self, text_to_add: str):
        if text_to_add and isinstance(text_to_add, str):
            if self.descriptionId is None:
                self.descriptionId = text_to_add
            else:
                self.descriptionId += text_to_add
        else:
            raise ValueError("The 'text_to_add' must be a non-empty string.")
    
    @property    
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {
            'description':self.description._as_dict_ if self.description else None,
            'descriptionId': self.descriptionId.replace("\n"," ").replace("\r"," ") if self.descriptionId else None,
            'attribution': self.attribution._as_dict_ if self.attribution else None,
            'qualifiers':[qualifier.__as_dict__ for qualifier in self.qualifiers] if (self.qualifiers and len(self.qualifiers) > 0) else None
            }
        return Serialization.serialize_dict(type_as_dict)
      
    @classmethod
    def _from_json_(cls, data: dict):         
        """
        Rehydrate a SourceReference from the dict passed down from JSON deserialization.
        NOTE: This does not resolve references to SourceDescription objects.
        """
        from .Serialization import Serialization
        return Serialization.deserialize(data, SourceReference)
    
        

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False  

        return (
            self.description.uri == other.description.uri
        )
