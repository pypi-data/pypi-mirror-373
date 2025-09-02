from __future__ import annotations
from functools import lru_cache

import enum
import logging
import types
from collections.abc import Sized
from typing import Any, Dict, List, Set, Tuple, Union, Annotated, ForwardRef, get_args, get_origin
from typing import Any, Callable, Mapping, List, Dict, Tuple, Set
from typing import List, Optional

"""
======================================================================
 Project: Gedcom-X
 File:    Serialization.py
 Author:  David J. Cartwright
 Purpose: Serialization/Deserialization of gedcomx Objects

 Created: 2025-08-25
 Updated:
   - 2025-08-31: cleaned up imports and documentation
   
======================================================================
"""

"""
======================================================================
GEDCOM Module Types
======================================================================
"""
from .Address import Address
from .Agent import Agent
from .Attribution import Attribution
from .Conclusion import ConfidenceLevel
from .Date import Date
from .Document import Document, DocumentType, TextType
from .EvidenceReference import EvidenceReference
from .Event import Event, EventType, EventRole, EventRoleType
from .Extensions.rs10.rsLink import _rsLinkList
from .Fact import Fact, FactType, FactQualifier
from .Gender import Gender, GenderType
from .Identifier import IdentifierList, Identifier
from .LoggingHub import hub, ChannelConfig
from .Name import Name, NameType, NameForm, NamePart, NamePartType, NamePartQualifier
from .Note import Note
from .OnlineAccount import OnlineAccount
from .Person import Person
from .PlaceDescription import PlaceDescription
from .PlaceReference import PlaceReference
from .Qualifier import Qualifier
from .Relationship import Relationship, RelationshipType
from .Resource import Resource
from .SourceDescription import SourceDescription, ResourceType, SourceCitation, Coverage
from .SourceReference import SourceReference
from .TextValue import TextValue
from .URI import URI
#======================================================================

log = logging.getLogger("gedcomx")
deserialization = "gedcomx.deserialization"

hub.start_channel(
    ChannelConfig(
        name=deserialization,
        path=f"logs/{deserialization}.log",
        level=logging.DEBUG,
        rotation="size:10MB:3",   # rotate by size, keep 3 backups
    )
)

_PRIMITIVES = (str, int, float, bool, type(None))

def _has_parent_class(obj) -> bool:
    return hasattr(obj, '__class__') and hasattr(obj.__class__, '__bases__') and len(obj.__class__.__bases__) > 0

class Serialization:
 
    @staticmethod
    def serialize_dict(dict_to_serialize: dict) -> dict:
        """
        Walk a dict and serialize nested GedcomX objects to JSON-compatible values.
        - Uses `_as_dict_` on your objects when present
        - Recurse into dicts / lists / sets / tuples
        - Drops None and empty containers
        """
        def _serialize(value):
            if isinstance(value, (str, int, float, bool, type(None))):
                return value
            if hasattr(value, "_as_dict_"):
                # Expect your objects expose a snapshot via _as_dict_
                return value._as_dict_
            if isinstance(value, dict):
                return {k: _serialize(v) for k, v in value.items()}
            if isinstance(value, (list, tuple, set)):
                return [_serialize(v) for v in value]
            # Fallback: string representation
            return str(value)

        if isinstance(dict_to_serialize, dict):
            cooked = {
                k: _serialize(v)
                for k, v in dict_to_serialize.items()
                if v is not None
            }
            # prune empty containers (after serialization)
            return {
                k: v
                for k, v in cooked.items()
                if not (isinstance(v, Sized) and len(v) == 0)
            }
        return {}

    # --- tiny helpers --------------------------------------------------------
    @staticmethod
    def _is_resource(obj: Any) -> bool:
        """
        try:
            from Resource import Resource
        except Exception:
            class Resource: pass
        """
        return isinstance(obj, Resource)

    @staticmethod
    def _has_resource_value(x: Any) -> bool:
        if Serialization._is_resource(x):
            return True
        if isinstance(x, (list, tuple, set)):
            return any(Serialization._has_resource_value(v) for v in x)
        if isinstance(x, dict):
            return any(Serialization._has_resource_value(v) for v in x.values())
        return False

    @staticmethod
    def _resolve_structure(x: Any, resolver: Callable[[Any], Any]) -> Any:
        """Return a deep copy with Resources resolved via resolver(Resource)->Any."""
        if Serialization._is_resource(x):
            return resolver(x)
        if isinstance(x, list):
            return [Serialization._resolve_structure(v, resolver) for v in x]
        if isinstance(x, tuple):
            return tuple(Serialization._resolve_structure(v, resolver) for v in x)
        if isinstance(x, set):
            return {Serialization._resolve_structure(v, resolver) for v in x}
        if isinstance(x, dict):
            return {k: Serialization._resolve_structure(v, resolver) for k, v in x.items()}
        return x

    @classmethod
    def apply_resource_resolutions(cls, inst: Any, resolver: Callable[[Any], Any]) -> None:
        """Resolve any queued attribute setters stored on the instance."""
        setters: List[Callable[[Any], None]] = getattr(inst, "_resource_setters", [])
        for set_fn in setters:
            set_fn(inst, resolver)
        # Optional: clear after applying
        inst._resource_setters = []

    # --- your deserialize with setters --------------------------------------
    @classmethod
    def deserialize(
        cls,
        data: Dict[str, Any],
        class_type: type,
        *,
        resolver: Callable[[Any], Any] | None = None,  # pass a function to resolve Resources now
        queue_setters: bool = True                     # also stash setters on instance for later
    ) -> Any:
        class_fields = cls.get_class_fields(class_type.__name__)
        result: Dict[str, Any] = {}
        # collect setters that know how to assign back to attributes
        pending_setters: List[Callable[[Any, Callable[[Any], Any]], None]] = []

        for name, typ in class_fields.items():
            if name not in data:
                continue
            coerced = cls._coerce_value(data[name], typ)
            result[name] = coerced

            # if this attribute (or inside it) has Resource(s), prepare a setter
            if cls._has_resource_value(coerced):
                def make_setter(attr_name: str, raw_value: Any):
                    # capture references to the *exact* object we just built for this attribute
                    def _setter(instance: Any, _resolver: Callable[[Any], Any]) -> None:
                        resolved = cls._resolve_structure(raw_value, _resolver)
                        setattr(instance, attr_name, resolved)
                    return _setter
                pending_setters.append(make_setter(name, coerced))

        # build the instance
        inst = class_type(**result)

        # apply now, if resolver provided
        if resolver is not None and pending_setters:
            for set_fn in pending_setters:
                set_fn(inst, resolver)

        # optionally store for later (gives you a real attribute assignment later)
        if queue_setters:
            # merge if already present
            existing = getattr(inst, "_resource_setters", [])
            inst._resource_setters = [*existing, *pending_setters]

        return inst

    @staticmethod
    def get_class_fields(cls_name) -> Dict:
        # NOTE: keep imports local to avoid circulars
        

        fields = {
            "GedcomX": {"persons": List[Person]},
            "Conclusion": {
                "id": str,
                "lang": str,
                "sources": List["SourceReference"],
                "analysis": Document | Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "uri": "Resource",
                "max_note_count": int,
                "links": _rsLinkList,
            },
            "Subject": {
                "id": str,
                "lang": str,
                "sources": List["SourceReference"],
                "analysis": Resource,
                "notes": List["Note"],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "uri": Resource,
                "links": _rsLinkList,
            },
            "Person": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "private": bool,
                "gender": Gender,
                "names": List[Name],
                "facts": List[Fact],
                "living": bool,
                "links": _rsLinkList,
                #"uri": URI,
            },
            "SourceReference": {
                "description": Resource,
                "descriptionId": str,
                "attribution": Attribution,
                "qualifiers": List[Qualifier],
            },
            "Attribution": {
                "contributor": Resource,
                "modified": str,
                "changeMessage": str,
                "creator": Resource,
                "created": str,
            },
            "SourceDescription": {
                "id": str,
                "resourceType": ResourceType,
                "citations": List[SourceCitation],
                "mediaType": str,
                "about": URI,
                "mediator": Resource,
                "publisher": Resource,          # forward-ref to avoid circular import
                "authors": List[Resource],
                "sources": List[SourceReference],         # SourceReference
                "analysis": Resource,          # analysis is typically a Document (kept union to avoid cycle)
                "componentOf": SourceReference,           # SourceReference
                "titles": List[TextValue],
                "notes": List[Note],
                "attribution": Attribution,
                "rights": List[Resource],
                "coverage": List[Coverage],               # Coverage
                "descriptions": List[TextValue],
                "identifiers": IdentifierList,
                "created": Date,
                "modified": Date,
                "published": Date,
                "repository": Agent,                    # forward-ref
                "max_note_count": int,
            },
            "Gender": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": GenderType,
            },
            "PlaceReference": {
                "original": str,
                "description": URI,
            },
            "Relationship": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": IdentifierList,
                "type": RelationshipType,
                "person1": Resource,
                "person2": Resource,
                "facts": List[Fact],
            },
            "Document": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": DocumentType,
                "extracted": bool,
                "textType": TextType,
                "text": str,
            },
            "PlaceDescription": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": List[IdentifierList],
                "names": List[TextValue],
                "type": str,
                "place": URI,
                "jurisdiction": Resource,
                "latitude": float,
                "longitude": float,
                "temporalDescription": Date,
                "spatialDescription": Resource,
            },
            "Agent": {
                "id": str,
                "identifiers": IdentifierList,
                "names": List[TextValue],
                "homepage": URI,
                "openid": URI,
                "accounts": List[OnlineAccount],
                "emails": List[URI],
                "phones": List[URI],
                "addresses": List[Address],
                "person": object | Resource,  # intended Person | Resource
                "attribution": object,         # GEDCOM5/7 compatibility
                "uri": URI | Resource,
            },
            "Event": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "extracted": bool,
                "evidence": List[EvidenceReference],
                "media": List[SourceReference],
                "identifiers": List[Identifier],
                "type": EventType,
                "date": Date,
                "place": PlaceReference,
                "roles": List[EventRole],
            },
            "EventRole": {
                "id:": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "person": Resource,
                "type": EventRoleType,
                "details": str,
            },
            "Resource":{
                "resource":URI,
                "id":str
            },
            "Qualifier":{
                "name":str,
                "value":str
            },
            "KnownSourceReference":{
                "name":str,
                "value":str
            },
            "Name": {
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": NameType,
                "nameForms": List[NameForm],  # use string to avoid circulars if needed
                "date": Date,
            },
            "NameForm": {
                "lang": str,
                "fullText": str,
                "parts": List[NamePart],  # use "NamePart" as a forward-ref to avoid circulars
            },
            "NamePart": {
                "type": NamePartType,
                "value": str,
                "qualifiers": List["NamePartQualifier"],  # quote if you want to avoid circulars
            },
            "Fact":{
                "id": str,
                "lang": str,
                "sources": List[SourceReference],
                "analysis": Resource | Document,
                "notes": List[Note],
                "confidence": ConfidenceLevel,
                "attribution": Attribution,
                "type": FactType,
                "date": Date,
                "place": PlaceReference,
                "value": str,
                "qualifiers": List[FactQualifier],
                "links": _rsLinkList,
            }
        }
        return fields.get(cls_name, {})


    @classmethod
    def _coerce_value(cls, value: Any, Typ: Any) -> Any:
        """Coerce `value` into `Typ` using the registry (recursively), with verbose logging."""
        log.debug("COERCE enter: value=%r (type=%s) -> Typ=%r", value, type(value).__name__, Typ)

        # Enums
        if cls._is_enum_type(Typ):
            U = cls._resolve_forward(cls._unwrap(Typ))
            log.debug("COERCE enum: casting %r to %s", value, getattr(U, "__name__", U))
            try:
                ret = U(value)
                log.debug("COERCE enum: success -> %r", ret)
                return ret
            except Exception:
                log.exception("COERCE enum: failed to cast %r to %s", value, U)
                return value

        # Unwrap typing once
        T = cls._resolve_forward(cls._unwrap(Typ))
        origin = get_origin(T) or T
        args = get_args(T)
        log.debug("COERCE typing: unwrapped Typ=%r -> T=%r, origin=%r, args=%r", Typ, T, origin, args)

        # Late imports to reduce circulars (and to allow logging if they aren't available)
        '''
        try:
            from gedcomx.Resource import Resource
            from gedcomx.URI import URI
            from gedcomx.Identifier import IdentifierList
            _gx_import_ok = True
        except Exception as _imp_err:
            _gx_import_ok = False
            Resource = URI = IdentifierList = object  # fallbacks avoid NameError
            log.debug("COERCE imports: gedcomx types not available (%r); using object fallbacks", _imp_err)
        '''

        # Strings to Resource/URI
        if isinstance(value, str):
            if T is Resource:
                log.debug("COERCE str->Resource: %r", value)
                try:
                    ret = Resource(uri=value)
                    log.debug("COERCE str->Resource: built %r", ret)
                    return ret
                except Exception:
                    log.exception("COERCE str->Resource: failed for %r", value)
                    return value
            if T is URI:
                log.debug("COERCE str->URI: %r", value)
                try:
                    ret: Any = URI.from_url(value)
                    log.debug("COERCE str->URI: built %r", ret)
                    return ret
                except Exception:
                    log.exception("COERCE str->URI: failed for %r", value)
                    return value
            log.debug("COERCE str passthrough: target %r is not Resource/URI", T)
            return value

        # Dict to Resource
        if T is Resource and isinstance(value, dict):
            log.debug("COERCE dict->Resource: %r", value)
            try:
                ret = Resource(uri=value.get("resource"), id=value.get("resourceId"))
                log.debug("COERCE dict->Resource: built %r", ret)
                return ret
            except Exception:
                log.exception("COERCE dict->Resource: failed for %r", value)
                return value

        # IdentifierList special
        if T is IdentifierList:
            log.debug("COERCE IdentifierList: %r", value)
            try:
                ret = IdentifierList._from_json_(value)
                log.debug("COERCE IdentifierList: built %r", ret)
                return ret
            except Exception:
                log.exception("COERCE IdentifierList: _from_json_ failed for %r", value)
                return value

        # Containers
        if cls._is_list_like(T):
            elem_t = args[0] if args else Any
            log.debug("COERCE list-like: len=%s, elem_t=%r", len(value or []), elem_t)
            try:
                ret = [cls._coerce_value(v, elem_t) for v in (value or [])]
                log.debug("COERCE list-like: result sample=%r", ret[:3] if isinstance(ret, list) else ret)
                return ret
            except Exception:
                log.exception("COERCE list-like: failed for value=%r elem_t=%r", value, elem_t)
                return value

        if cls._is_set_like(T):
            elem_t = args[0] if args else Any
            log.debug("COERCE set-like: len=%s, elem_t=%r", len(value or []), elem_t)
            try:
                ret = {cls._coerce_value(v, elem_t) for v in (value or [])}
                log.debug("COERCE set-like: result size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE set-like: failed for value=%r elem_t=%r", value, elem_t)
                return value

        if cls._is_tuple_like(T):
            log.debug("COERCE tuple-like: value=%r, args=%r", value, args)
            try:
                if not value:
                    log.debug("COERCE tuple-like: empty/None -> ()")
                    return tuple(value or ())
                if len(args) == 2 and args[1] is Ellipsis:
                    elem_t = args[0]
                    ret = tuple(cls._coerce_value(v, elem_t) for v in (value or ()))
                    log.debug("COERCE tuple-like variadic: size=%d", len(ret))
                    return ret
                ret = tuple(cls._coerce_value(v, t) for v, t in zip(value, args))
                log.debug("COERCE tuple-like fixed: size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE tuple-like: failed for value=%r args=%r", value, args)
                return value

        if cls._is_dict_like(T):
            k_t = args[0] if len(args) >= 1 else Any
            v_t = args[1] if len(args) >= 2 else Any
            log.debug("COERCE dict-like: keys=%s, k_t=%r, v_t=%r", len((value or {}).keys()), k_t, v_t)
            try:
                ret = {
                    cls._coerce_value(k, k_t): cls._coerce_value(v, v_t)
                    for k, v in (value or {}).items()
                }
                log.debug("COERCE dict-like: result size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE dict-like: failed for value=%r k_t=%r v_t=%r", value, k_t, v_t)
                return value

        # Objects via registry
        if isinstance(T, type) and isinstance(value, dict):
            fields = cls.get_class_fields(T.__name__) or {}
            log.debug(
                "COERCE object: class=%s, input_keys=%s, registered_fields=%s",
                T.__name__, list(value.keys()), list(fields.keys())
            )
            if fields:
                kwargs = {}
                present = []
                for fname, ftype in fields.items():
                    if fname in value:
                        resolved = cls._resolve_forward(cls._unwrap(ftype))
                        log.debug("COERCE object.field: %s.%s -> %r, raw=%r", T.__name__, fname, resolved, value[fname])
                        try:
                            coerced = cls._coerce_value(value[fname], resolved)
                            kwargs[fname] = coerced
                            present.append(fname)
                            log.debug("COERCE object.field: %s.%s coerced -> %r", T.__name__, fname, coerced)
                        except Exception:
                            log.exception("COERCE object.field: %s.%s failed", T.__name__, fname)
                unknown = [k for k in value.keys() if k not in fields]
                if unknown:
                    log.debug("COERCE object: %s unknown keys ignored: %s", T.__name__, unknown)
                try:
                    log.debug("COERCE object: instantiate %s(**%s)", T.__name__, present)
                    ret = T(**kwargs)
                    log.debug("COERCE object: success -> %r", ret)
                    return ret
                except TypeError as e:
                    log.error("COERCE object: instantiate %s failed with kwargs=%s: %s", T.__name__, list(kwargs.keys()), e)
                    log.debug("COERCE object: returning partially coerced dict")
                    return kwargs

        # Already correct type?
        try:
            if isinstance(value, T):
                log.debug("COERCE passthrough: value already instance of %r", T)
                return value
        except TypeError:
            log.debug("COERCE isinstance not applicable: T=%r", T)

        log.debug("COERCE fallback: returning original value=%r (type=%s)", value, type(value).__name__)
        return value


        # Dict to Resource
        if T is Resource and isinstance(value, dict):
            log.debug("COERCE dict->Resource: %r", value)
            try:
                ret = Resource(uri=value.get("resource"), id=value.get("resourceId"))
                log.debug("COERCE dict->Resource: built %r", ret)
                return ret
            except Exception:
                log.exception("COERCE dict->Resource: failed for %r", value)
                return value

        # IdentifierList special
        if T is IdentifierList:
            log.debug("COERCE IdentifierList: %r", value)
            try:
                ret = IdentifierList._from_json_(value)
                log.debug("COERCE IdentifierList: built %r", ret)
                return ret
            except Exception:
                log.exception("COERCE IdentifierList: _from_json_ failed for %r", value)
                return value

        # Containers
        if self._is_list_like(T):
            elem_t = args[0] if args else Any
            log.debug("COERCE list-like: len=%s, elem_t=%r", len(value or []), elem_t)
            try:
                ret = [self._coerce_value(v, elem_t) for v in (value or [])]
                log.debug("COERCE list-like: result sample=%r", ret[:3] if isinstance(ret, list) else ret)
                return ret
            except Exception:
                log.exception("COERCE list-like: failed for value=%r elem_t=%r", value, elem_t)
                return value

        if self._is_set_like(T):
            elem_t = args[0] if args else Any
            log.debug("COERCE set-like: len=%s, elem_t=%r", len(value or []), elem_t)
            try:
                ret = {self._coerce_value(v, elem_t) for v in (value or [])}
                log.debug("COERCE set-like: result size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE set-like: failed for value=%r elem_t=%r", value, elem_t)
                return value

        if self._is_tuple_like(T):
            log.debug("COERCE tuple-like: value=%r, args=%r", value, args)
            try:
                if not value:
                    log.debug("COERCE tuple-like: empty/None -> ()")
                    return tuple(value or ())
                if len(args) == 2 and args[1] is Ellipsis:
                    elem_t = args[0]
                    ret = tuple(self._coerce_value(v, elem_t) for v in (value or ()))
                    log.debug("COERCE tuple-like variadic: size=%d", len(ret))
                    return ret
                ret = tuple(self._coerce_value(v, t) for v, t in zip(value, args))
                log.debug("COERCE tuple-like fixed: size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE tuple-like: failed for value=%r args=%r", value, args)
                return value

        if self._is_dict_like(T):
            k_t = args[0] if len(args) >= 1 else Any
            v_t = args[1] if len(args) >= 2 else Any
            log.debug("COERCE dict-like: keys=%s, k_t=%r, v_t=%r", len((value or {}).keys()), k_t, v_t)
            try:
                ret = {
                    self._coerce_value(k, k_t): self._coerce_value(v, v_t)
                    for k, v in (value or {}).items()
                }
                log.debug("COERCE dict-like: result size=%d", len(ret))
                return ret
            except Exception:
                log.exception("COERCE dict-like: failed for value=%r k_t=%r v_t=%r", value, k_t, v_t)
                return value

        # Objects via registry
        if isinstance(T, type) and isinstance(value, dict):
            fields = self.get_class_fields(T.__name__) or {}
            log.debug(
                "COERCE object: class=%s, input_keys=%s, registered_fields=%s",
                T.__name__, list(value.keys()), list(fields.keys())
            )
            if fields:
                kwargs = {}
                present = []
                for fname, ftype in fields.items():
                    if fname in value:
                        resolved = self._resolve_forward(self._unwrap(ftype))
                        log.debug("COERCE object.field: %s.%s -> %r, raw=%r", T.__name__, fname, resolved, value[fname])
                        try:
                            coerced = self._coerce_value(value[fname], resolved)
                            kwargs[fname] = coerced
                            present.append(fname)
                            log.debug("COERCE object.field: %s.%s coerced -> %r", T.__name__, fname, coerced)
                        except Exception:
                            log.exception("COERCE object.field: %s.%s failed", T.__name__, fname)
                unknown = [k for k in value.keys() if k not in fields]
                if unknown:
                    log.debug("COERCE object: %s unknown keys ignored: %s", T.__name__, unknown)
                try:
                    log.debug("COERCE object: instantiate %s(**%s)", T.__name__, present)
                    ret = T(**kwargs)
                    log.debug("COERCE object: success -> %r", ret)
                    return ret
                except TypeError as e:
                    log.warning("COERCE object: instantiate %s failed with kwargs=%s: %s", T.__name__, list(kwargs.keys()), e)
                    log.debug("COERCE object: returning partially coerced dict")
                    return kwargs

        # Already correct type?
        try:
            if isinstance(value, T):
                log.debug("COERCE passthrough: value already instance of %r", T)
                return value
        except TypeError:
            log.debug("COERCE isinstance not applicable: T=%r", T)

        log.debug("COERCE fallback: returning original value=%r (type=%s)", value, type(value).__name__)
        return value

    # -------------------------- TYPE HELPERS --------------------------

    @staticmethod
    @lru_cache(maxsize=None)
    def _unwrap(T: Any) -> Any:
        origin = get_origin(T)
        if origin is None:
            return T
        if str(origin).endswith("Annotated"):
            args = get_args(T)
            return Serialization._unwrap(args[0]) if args else Any
        if origin in (Union, types.UnionType):
            args = tuple(a for a in get_args(T) if a is not type(None))
            return Serialization._unwrap(args[0]) if len(args) == 1 else tuple(Serialization._unwrap(a) for a in args)
        return T

    @staticmethod
    @lru_cache(maxsize=None)
    def _resolve_forward(T: Any) -> Any:
        if isinstance(T, ForwardRef):
            return globals().get(T.__forward_arg__, T)
        if isinstance(T, str):
            return globals().get(T, T)
        return T

    @staticmethod
    @lru_cache(maxsize=None)
    def _is_enum_type(T: Any) -> bool:
        U = Serialization._resolve_forward(Serialization._unwrap(T))
        try:
            return isinstance(U, type) and issubclass(U, enum.Enum)
        except TypeError:
            return False

    @staticmethod
    def _is_list_like(T: Any) -> bool:
        origin = get_origin(T) or T
        return origin in (list, List)

    @staticmethod
    def _is_set_like(T: Any) -> bool:
        origin = get_origin(T) or T
        return origin in (set, Set)

    @staticmethod
    def _is_tuple_like(T: Any) -> bool:
        origin = get_origin(T) or T
        return origin in (tuple, Tuple)

    @staticmethod
    def _is_dict_like(T: Any) -> bool:
        origin = get_origin(T) or T
        return origin in (dict, Dict)
