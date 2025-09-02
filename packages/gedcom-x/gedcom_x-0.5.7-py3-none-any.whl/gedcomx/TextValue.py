from typing import Optional

class TextValue:
    identifier = 'http://gedcomx.org/v1/TextValue'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, value: Optional[str] = None, lang: Optional[str] = 'en') -> None:
        self.lang = lang
        self.value = value
    
    def _append_to_value(self, value_to_append):
        if not isinstance(value_to_append, str):
            raise ValueError(f"Cannot append object of type {type(value_to_append)}.")
        self.value += ' ' + value_to_append
    
    @property
    def _as_dict_(self):
        return {
            "lang":self.lang if self.lang else None,
            "value":self.value if self.value else None
        }
    
    def __str__(self):
        return f"{self.value} ({self.lang})"
    
    # ...existing code...

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a TextValue instance from a JSON-dict (already parsed).
        """
        value = data.get('value')
        lang = data.get('lang', 'en')
        return cls(value=value, lang=lang)
