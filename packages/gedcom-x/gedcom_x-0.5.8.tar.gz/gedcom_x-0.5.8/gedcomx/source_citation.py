from typing import Optional

class SourceCitation:
    identifier = 'http://gedcomx.org/v1/SourceCitation'
    version = 'http://gedcomx.org/conceptual-model/v1'
    
    def __init__(self, lang: Optional[str], value: str) -> None:
        self.lang = lang if lang else 'en'
        self.value = value
    
    # ...existing code...

    @classmethod
    def _from_json_(cls, data: dict):
        """
        Create a SourceCitation instance from a JSON-dict (already parsed).
        """
        lang = data.get('lang', 'en')
        value = data.get('value')
        return cls(lang=lang, value=value)
    
    @property
    def _as_dict_(self):
        return {'lang':self.lang,
                'value': self.value}