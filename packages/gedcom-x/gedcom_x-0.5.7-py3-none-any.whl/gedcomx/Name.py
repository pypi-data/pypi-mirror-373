from enum import Enum
from typing import List,Optional
from typing_extensions import Self

"""
======================================================================
 Project: Gedcom-X
 File:    Name.py
 Author:  David J. Cartwright
 Purpose: Python Object representation of GedcomX Name, NameType, NameForm, NamePart Types

 Created: 2025-08-25
 Updated:
   - 2025-08-31: _as_dict_ to only create entries in dict for fields that hold data
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
#======================================================================
from .Attribution import Attribution
from .Conclusion import Conclusion, ConfidenceLevel
from .Date import Date
from .Note import Note
from .Resource import Resource
from .SourceReference import SourceReference
#======================================================================


class NameType(Enum):
    BirthName = "http://gedcomx.org/BirthName"
    MarriedName = "http://gedcomx.org/MarriedName"
    AlsoKnownAs = "http://gedcomx.org/AlsoKnownAs"
    Nickname = "http://gedcomx.org/Nickname"
    AdoptiveName = "http://gedcomx.org/AdoptiveName"
    FormalName = "http://gedcomx.org/FormalName"
    ReligiousName = "http://gedcomx.org/ReligiousName"
    
    @property
    def description(self):
        descriptions = {
            NameType.BirthName: "Name given at birth.",
            NameType.MarriedName: "Name accepted at marriage.",
            NameType.AlsoKnownAs: "\"Also known as\" name.",
            NameType.Nickname: "Nickname.",
            NameType.AdoptiveName: "Name given at adoption.",
            NameType.FormalName: "A formal name, usually given to distinguish it from a name more commonly used.",
            NameType.ReligiousName: "A name given at a religious rite or ceremony."
        }
        return descriptions.get(self, "No description available.")

class NamePartQualifier(Enum):
    Title = "http://gedcomx.org/Title"
    Primary = "http://gedcomx.org/Primary"
    Secondary = "http://gedcomx.org/Secondary"
    Middle = "http://gedcomx.org/Middle"
    Familiar = "http://gedcomx.org/Familiar"
    Religious = "http://gedcomx.org/Religious"
    Family = "http://gedcomx.org/Family"
    Maiden = "http://gedcomx.org/Maiden"
    Patronymic = "http://gedcomx.org/Patronymic"
    Matronymic = "http://gedcomx.org/Matronymic"
    Geographic = "http://gedcomx.org/Geographic"
    Occupational = "http://gedcomx.org/Occupational"
    Characteristic = "http://gedcomx.org/Characteristic"
    Postnom = "http://gedcomx.org/Postnom"
    Particle = "http://gedcomx.org/Particle"
    RootName = "http://gedcomx.org/RootName"
    
    @property
    def description(self):
        descriptions = {
            NamePartQualifier.Title: "A designation for honorifics (e.g., Dr., Rev., His Majesty, Haji), ranks (e.g., Colonel, General), positions (e.g., Count, Chief), or other titles (e.g., PhD, MD). Name part qualifiers of type Title SHOULD NOT provide a value.",
            NamePartQualifier.Primary: "A designation for the most prominent name among names of that type (e.g., the primary given name). Name part qualifiers of type Primary SHOULD NOT provide a value.",
            NamePartQualifier.Secondary: "A designation for a name that is not primary in its importance among names of that type. Name part qualifiers of type Secondary SHOULD NOT provide a value.",
            NamePartQualifier.Middle: "Useful for cultures designating a middle name distinct from a given name and surname. Name part qualifiers of type Middle SHOULD NOT provide a value.",
            NamePartQualifier.Familiar: "A designation for one's familiar name. Name part qualifiers of type Familiar SHOULD NOT provide a value.",
            NamePartQualifier.Religious: "A name given for religious purposes. Name part qualifiers of type Religious SHOULD NOT provide a value.",
            NamePartQualifier.Family: "A name that associates a person with a group, such as a clan, tribe, or patriarchal hierarchy. Name part qualifiers of type Family SHOULD NOT provide a value.",
            NamePartQualifier.Maiden: "Original surname retained by women after adopting a new surname upon marriage. Name part qualifiers of type Maiden SHOULD NOT provide a value.",
            NamePartQualifier.Patronymic: "A name derived from a father or paternal ancestor. Name part qualifiers of type Patronymic SHOULD NOT provide a value.",
            NamePartQualifier.Matronymic: "A name derived from a mother or maternal ancestor. Name part qualifiers of type Matronymic SHOULD NOT provide a value.",
            NamePartQualifier.Geographic: "A name derived from associated geography. Name part qualifiers of type Geographic SHOULD NOT provide a value.",
            NamePartQualifier.Occupational: "A name derived from one's occupation. Name part qualifiers of type Occupational SHOULD NOT provide a value.",
            NamePartQualifier.Characteristic: "A name derived from a characteristic. Name part qualifiers of type Characteristic SHOULD NOT provide a value.",
            NamePartQualifier.Postnom: "A name mandated by law for populations in specific regions. Name part qualifiers of type Postnom SHOULD NOT provide a value.",
            NamePartQualifier.Particle: "A grammatical designation for articles, prepositions, conjunctions, and other words used as name parts. Name part qualifiers of type Particle SHOULD NOT provide a value.",
            NamePartQualifier.RootName: "The 'root' of a name part, as distinguished from prefixes or suffixes (e.g., the root of 'Wilkówna' is 'Wilk'). A RootName qualifier MUST provide a value property."
        }
        return descriptions.get(self, "No description available.")

class NamePartType(Enum):
    Prefix = "http://gedcomx.org/Prefix"
    Suffix = "http://gedcomx.org/Suffix"
    Given = "http://gedcomx.org/Given"
    Surname = "http://gedcomx.org/Surname"
    
    @property
    def description(self):
        descriptions = {
            NamePartType.Prefix: "A name prefix.",
            NamePartType.Suffix: "A name suffix.",
            NamePartType.Given: "A given name.",
            NamePartType.Surname: "A surname."
        }
        return descriptions.get(self, "No description available.")
    
class NamePart:
    """Used to model a portion of a full name
        including the terms that make up that portion. Some name parts may have qualifiers
        to provide additional semantic meaning to the name part (e.g., "given name" or "surname").

    Args:
        type (NamePartType | None): Classification of this component of the name
            (e.g., ``Given``, ``Surname``, ``Prefix``, ``Suffix``, ``Title``, ``Particle``).
        value (str): The textual value for this part, without surrounding
            punctuation (e.g., ``"John"``, ``"van"``, ``"III"``).
        qualifiers (list[NamePartQualifier] | None): Optional qualifiers that refine
            the meaning or usage of this part (e.g., language/script variants, initials).

    Examples:
        >>> from gedcomx.Name import *
        >>> typ = NamePartType.Given
        >>> given = "Moses"
        >>> q = NamePartQualifier.Primary
        >>> name = NamePart(type=typ,value=given,qualifiers=[q])
        >>> print(name)
        NamePart(type=Given, value='Moses', qualifiers=1)

    """
    identifier = 'http://gedcomx.org/v1/NamePart'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self,
                 type: Optional[NamePartType] = None,
                 value: Optional[str] = None,
                 qualifiers: Optional[List[NamePartQualifier]] = None) -> None:
        self.type = type
        self.value = value
        self.qualifiers = qualifiers if qualifiers else []
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.type:
            type_as_dict['type'] = self.type.value
        if self.value:
            type_as_dict['value'] = self.value
        if self.qualifiers:
            type_as_dict['qualifiers'] = [q.value for q in self.qualifiers]
        Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls,data):
        name_part =NamePart(type=NamePartType(data['type']) if 'type' in data else None,
                            value=data.get('value'),
                            qualifiers=[NamePartQualifier(q) for q in data.get('qualifiers')])
        return name_part

    def __eq__(self, other):
        if not isinstance(other, NamePart):
            return NotImplemented
        return (self.type == other.type and
                self.value == other.value and
                self.qualifiers == other.qualifiers)    

    def __str__(self) -> str:
        parts = []
        if self.type is not None:
            parts.append(f"type={getattr(self.type, 'name', str(self.type))}")
        if self.value is not None:
            parts.append(f"value={self.value!r}")
        if self.qualifiers:
            parts.append(f"qualifiers={len(self.qualifiers)}")
        return f"NamePart({', '.join(parts)})" if parts else "NamePart()"

    def __repr__(self) -> str:
        if self.type is not None:
            tcls = self.type.__class__.__name__
            tname = getattr(self.type, "name", str(self.type))
            tval = getattr(self.type, "value", self.type)
            type_repr = f"<{tcls}.{tname}: {tval!r}>"
        else:
            type_repr = "None"
        return (
            f"{self.__class__.__name__}("
            f"type={type_repr}, "
            f"value={self.value!r}, "
            f"qualifiers={self.qualifiers!r})"
        )

class NameForm:
    """A representation of a name (a "name form") 
        within a given cultural context, such as a given language and script.
        As names are captured (both in records or in applications), the terms
        in the name are sometimes classified by type. For example, a certificate
        of death might prompt for **"given name(s)"** and **"surname"**. The parts
        list can be used to represent the terms in the name that have been classified.

    Args:
        lang (str | None): BCP-47 language tag for this name form (e.g., "en").
        fullText (str | None): The full, unparsed name string as written in the source.
            If provided, the name SHOULD be rendered as it would normally be spoken in
            the applicable cultural context.
        parts (list[NamePart] | None): Ordered structured components of the name
            (e.g., Given, Surname). If provided, ``fullText`` may be omitted. If
            provided, the list SHOULD be ordered such that the parts are in the order
            they would normally be spoken in the applicable cultural context.

    """
    identifier = 'http://gedcomx.org/v1/NameForm'
    version = 'http://gedcomx.org/conceptual-model/v1'

    def __init__(self, lang: Optional[str] = None,
                 fullText: Optional[str] = None,
                 parts: Optional[List[NamePart]] = None) -> None:
        
        self.lang = lang
        self.fullText = fullText
        self.parts = parts if parts else []
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = {}
        if self.lang:
            type_as_dict['lang'] = self.lang
        if self.fullText:
            type_as_dict['fullText'] = self.fullText
        if self.parts:
            type_as_dict['parts'] = [part._as_dict_ for part in self.parts if part]
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data: dict) -> "NameForm":
        """Build a NameForm from JSON-like dict."""
        return cls(
            lang=data.get("lang", "en"),
            fullText=data.get("fullText"),
            parts=[NamePart._from_json_(p) for p in ensure_list(data.get("parts"))],
        )
    
    def _fulltext_parts(self):
        pass

class Name(Conclusion):
    """**Defines a name of a person.**

            A Name is intended to represent a single variant of a person's name. 
            This means that nicknames, spelling variations, or other names 
            (often distinguishable by a name type) should be modeled with 
            separate instances of Name.

    .. admonition:: Advanced details
        :class: toggle
    
        The name forms of a name contain alternate representations of the name.
        A Name MUST contain at least one name form, presumably a representation
        of the name that is considered proper and well formed in the person's native,
        historical cultural context. Other name forms MAY be included, which can be
        used to represent this name in contexts where the native name form is not easily
        recognized and interpreted. Alternate forms are more likely in situations where
        conclusions are being analyzed across cultural context boundaries that have both
        language and writing script differences.
        

    Attributes:
        type (Optional[:class:`~gedcomx.NameType`]): Classification of the name
            (e.g., BirthName, AlsoKnownAs).
        nameForms (List[:class:`~gedcomx.NameForm`]): One or more structured
            representations of the name (full text and parts).
        date (Optional[:class:`~gedcomx.Date`]): Date context for this name
            (e.g., when the name was used or recorded).
    """
    identifier = 'http://gedcomx.org/v1/Name'
    version = 'http://gedcomx.org/conceptual-model/v1'

    @staticmethod
    def simple(text: str):
        """
        Takes a string and returns a GedcomX Name Object
        """
        if text:
            text = text.replace("/","")
            parts = text.rsplit(' ', 1)
        
            # Assign val1 and val2 based on the split
            given = parts[0] if len(parts) > 1 else ""
            surname = parts[1] if len(parts) > 1 else parts[0]
            
            # Remove any '/' characters from both val1 and val2
            #given = given.replace('/', '')
            #surname = surname.replace('/', '')

            given_name_part = NamePart(type = NamePartType.Given, value=given)
            surname_part = NamePart(type = NamePartType.Surname, value=surname)

            name_form = NameForm(fullText=text,parts=[given_name_part,surname_part])
            name = Name(type=NameType.BirthName,nameForms=[name_form])
        else:
            name = Name()
        return name

    def __init__(self, id: Optional[str] = None,
                 lang: Optional[str] = None,
                 sources: Optional[List[SourceReference]] = None,
                 analysis: Resource = None,
                 notes: Optional[List[Note]] = None,
                 confidence: Optional[ConfidenceLevel] = None,
                 attribution: Optional[Attribution] = None,
                 type: Optional[NameType] = None,
                 nameForms: Optional[List[NameForm]]= None,
                 date: Optional[Date] = None) -> None:
        super().__init__(id, lang, sources, analysis, notes, confidence, attribution)
        self.type = type
        self.nameForms = nameForms if nameForms else []
        self.date = date
    
    def _add_name_part(self, namepart_to_add: NamePart):
        if namepart_to_add and isinstance(namepart_to_add, NamePart):
            for current_namepart in self.nameForms[0].parts:
                if namepart_to_add == current_namepart:
                    return False
            self.nameForms[0].parts.append(namepart_to_add)
    
    @property
    def _as_dict_(self):
        from .Serialization import Serialization
        type_as_dict = super()._as_dict_
        if self.type:
            type_as_dict['type'] = getattr(self.type, 'value', self.type)
        if self.nameForms:
            type_as_dict['nameForms'] = [nf._as_dict_ for nf in self.nameForms if nf]
        if self.date:
            type_as_dict['date'] = self.date._as_dict_
        
        return Serialization.serialize_dict(type_as_dict)
    
    @classmethod
    def _from_json_(cls, data: dict) -> "Name":
        """Build a Name from JSON-like dict."""
        return cls(
            id=data.get("id"),
            lang=data.get("lang", "en"),
            sources=[SourceReference._from_json_(s) for s in ensure_list(data.get("sources"))],
            analysis=Resource._from_json_(data["analysis"]) if data.get("analysis") else None,
            notes=[Note._from_json_(n) for n in ensure_list(data.get("notes"))],
            confidence=ConfidenceLevel._from_json_(data["confidence"]) if data.get("confidence") else None,
            attribution=Attribution._from_json_(data["attribution"]) if data.get("attribution") else None,
            type=NameType(data["type"]) if data.get("type") else None,
            nameForms=[NameForm._from_json_(nf) for nf in ensure_list(data.get("nameForms"))],
            date=Date._from_json_(data["date"]) if data.get("date") else None,
        )
    
    def __str__(self) -> str:
        """Return a human-readable string for the Name-like object."""
        return f"Name(id={self.id}, type={self.type}, forms={len(self.nameForms)}, date={self.date})"

    def __repr__(self) -> str:
        """Return an unambiguous string representation of the Name-like object."""
        return (
            f"{self.__class__.__name__}("
            f"id={self.id!r}, "
            f"lang={self.lang!r}, "
            f"sources={self.sources!r}, "
            f"analysis={self.analysis!r}, "
            f"notes={self.notes!r}, "
            f"confidence={self.confidence!r}, "
            f"attribution={self.attribution!r}, "
            f"type={self.type!r}, "
            f"nameForms={self.nameForms!r}, "
            f"date={self.date!r})"
    )

class QuickName():
    def __new__(cls,name: str) -> Name:
        obj = Name(nameForms=[NameForm(fullText=name)])
        return obj
    
def ensure_list(val):
    if val is None:
        return []
    return val if isinstance(val, list) else [val]
    







