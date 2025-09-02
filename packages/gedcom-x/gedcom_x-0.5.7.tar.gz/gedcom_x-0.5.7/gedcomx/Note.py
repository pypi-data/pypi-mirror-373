from typing import Optional

from .Attribution import Attribution

class Note:
    identifier = 'http://gedcomx.org/v1/Note'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,lang: Optional[str] = 'en', subject: Optional[str] = None, text: Optional[str] = None, attribution: Optional[Attribution] = None) -> None:
        self.lang = lang
        self.subject = subject
        self.text = text
        self.attribution = attribution  

    def append(self, text_to_add: str):
        if text_to_add and isinstance(text_to_add, str):
            if self.text:
                self.text = self.text + text_to_add
            else:
                self.text = text_to_add
        else:
            return #TODO
            raise ValueError("The text to add must be a non-empty string.")
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.lang:
            type_as_dict["lang"] = self.lang
        if self.subject:
            type_as_dict["subject"] = self.subject
        if self.text:
            type_as_dict["text"] = self.text
        if self.attribution:
            # If attribution exposes `_as_dict_` as a property, use it; otherwise include as-is
            type_as_dict["attribution"] = getattr(self.attribution, "_as_dict_", self.attribution)
        return Serialization.serialize_dict(type_as_dict)    
    
    def __eq__(self, other):
        if not isinstance(other, Note):
            return NotImplemented

        def safe_str(val):
            return val.strip() if isinstance(val, str) else ''

        return (
            #safe_str(self.lang) == safe_str(other.lang) and
            #safe_str(self.subject) == safe_str(other.subject) and
            safe_str(self.text) == safe_str(other.text) #and
           # self.attribution == other.attribution  # Assumes Attribution defines __eq__
        )
    
    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a Note instance from a JSON-dict (already parsed).
        """
        # Basic scalar fields
        lang     = data.get('lang', 'en')
        text     = data.get('text')
        subject  = data.get('subject')
        # Add other fields as needed

        # Build the instance
        inst = cls(
            lang    = lang,
            text    = text,
            subject = subject,
            # Add other fields as needed
        )

        return inst