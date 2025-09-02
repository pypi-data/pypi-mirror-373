from enum import Enum
from typing import Optional, List
"""
======================================================================
 Project: Gedcom-X
 File:    document.py
 Author:  David J. Cartwright
 Purpose: 

 Created: 2025-08-25
 Updated:
   - 2025-08-31: 
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .attribution import Attribution
from .conclusion import Conclusion, ConfidenceLevel
from .note import Note
from .resource import Resource
from .source_reference import SourceReference


class DocumentType(Enum):
    Abstract = "http://gedcomx.org/Abstract"
    Transcription = "http://gedcomx.org/Transcription"
    Translation = "http://gedcomx.org/Translation"
    Analysis = "http://gedcomx.org/Analysis"
    
    @property
    def description(self):
        descriptions = {
            DocumentType.Abstract: "The document is an abstract of a record or document.",
            DocumentType.Transcription: "The document is a transcription of a record or document.",
            DocumentType.Translation: "The document is a translation of a record or document.",
            DocumentType.Analysis: "The document is an analysis done by a researcher; a genealogical proof statement is an example of one kind of analysis document."
        }
        return descriptions.get(self, "No description available.")

class TextType(Enum):
    plain = 'plain'
    xhtml = 'xhtml'

class Document(Conclusion):
    identifier = 'http://gedcomx.org/v1/Document'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Optional[Resource] = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None, # ConfidenceLevel
                 attribution: Optional[Attribution] = None,
                 type: Optional[DocumentType] = None,
                 extracted: Optional[bool] = None, # Default to False
                 textType: Optional[TextType] = None,
                 text: Optional[str] = None,
                 ) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.type = type
        self.extracted = extracted
        self.textType = textType
        self.text = text
    
    @property
    def _as_dict(self):
        from .serialization import Serialization
        type_as_dict = super()._as_dict_
        if self.type:
            type_as_dict['type'] = self.type.value
        if self.extracted is not None:
            type_as_dict['extracted'] = self.extracted
        if self.textType:
            type_as_dict['textType'] = self.textType.value
        if self.text:
            type_as_dict['text'] = self.text
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Person instance from a JSON-dict (already parsed).
        """
        from .serialization import Serialization
        type_as_dict = Serialization.get_class_fields('Document')
        return Serialization.deserialize(type_as_dict,Document)