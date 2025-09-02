'''
The "Link" Data Type
The Link data type defines a representation of an available transition from one application state to another. 
The base definition of a link is provided by RFC 5988.

Instances of Link can be reasonably expected as extension elements to any GEDCOM X data type,
except data types that are defined by the GEDCOM X Conceptual Model to explicitly restrict extension properties.
'''

'''
8/25/25, 0.5.5, built serialization, type checking in init for href
'''

from typing import List, Optional
from ...URI import URI
from ...Exceptions import GedcomClassAttributeError


class rsLink():
    """A link description object. RS Extension to GedcomX by FamilySearch.

    Args:
        rel (str): Link relation identifier. Required.
        href (str, optional): Link target URI. If omitted, provide `template`.
        template (str, optional): URI Template (see RFC 6570). If omitted, provide `href`.
        type (str, optional): Media type(s) of the linked resource (RFC 2616 §3.7).
        accept (str, optional): Acceptable media type(s) for updating the linked resource (RFC 2616 §3.7).
        allow (str, optional): Allowable HTTP methods to transition to the linked resource (RFC 2616 §14.7).
        hreflang (str, optional): Language of the linked resource (e.g., BCP-47 tag).
        title (str, optional): Human-readable label for the link.

    Raises:
        ValueError: If neither `href` nor `template` is provided.
    """

    """Attribution Information for a Genealogy, Conclusion, Subject and child classes

    Args:
        contributor (Agent, optional):            Contributor to object being attributed.
        modified (timestamp, optional):           timestamp for when this record was modified.
        changeMessage (str, optional):            Birth date (YYYY-MM-DD).
        creator (Agent, optional):      Creator of object being attributed.
        created (timestamp, optional):            timestamp for when this record was created

    Raises:
        
    """
    identifier = "http://gedcomx.org/v1/Link"

    def __init__(self,rel: Optional[URI] = None,
                 href:  Optional[URI] = None,
                 template: Optional[str] = None,
                 type: Optional[str] = None,
                 accept: Optional[str] = None,
                 allow: Optional[str] = None,
                 hreflang: Optional[str] = None,
                 title: Optional[str] = None) -> None:
        
        self.rel = rel
        self.href = href if isinstance(href,URI) else URI.from_url(href) if isinstance(href,str) else None
        self.template = template
        self.type = type
        self.accept = accept
        self.allow = allow
        self.hreflang = hreflang
        self.title = title
    
        if self.href is None and self.template is None:
            raise GedcomClassAttributeError("href or template are required")
    
    @property
    def _as_dict_(self):
        from ...Serialization import Serialization
        type_as_dict = {
            "rel": self.rel._as_dict_ if self.rel else None,
            "href": self.href._as_dict_ if self.href else None,
            "template": self.template,   # RFC 6570 template if used
            "type": self.type,           # media type (note: shadows built-in 'type')
            "accept": self.accept,
            "allow": self.allow,
            "hreflang": self.hreflang,
            "title": self.title,
        }
        return Serialization.serialize_dict(type_as_dict)
    
    @property
    def json(self):
        import json
        return json.dumps(self._as_dict_)

class _rsLinkList():
    def __init__(self) -> None:
        self.links = {}

    def add(self,link: rsLink):
        if link and isinstance(link,rsLink):
            if link.rel in self.links.keys():
                self.links[link.rel].append(link.href)
            else:
                self.links[link.rel] = [link.href]
        

    @classmethod
    def _from_json_(cls,data: dict):
        
        link_list = _rsLinkList()
        for rel in data.keys():
            link_list.add(rsLink(rel,data[rel]))
        return link_list
    
    @property
    def _as_dict_(self) -> dict:
        return self.links


        