from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Optional, Union, Iterable, Tuple
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl, SplitResult

_DEFAULT_SCHEME = "gedcomx"

@dataclass(frozen=False, slots=True)
class URI:
    scheme: str = field(default=_DEFAULT_SCHEME)
    authority: str = field(default="")
    path: str = field(default="")
    query: str = field(default="")
    fragment: str = field(default="")

    # ---------- constructors ----------
    @classmethod
    def from_url(cls, url: str, *, default_scheme: str = _DEFAULT_SCHEME) -> "URI":
        s = urlsplit(url)
        scheme = s.scheme or default_scheme
        return cls(scheme=scheme, authority=s.netloc, path=s.path, query=s.query, fragment=s.fragment)

    @classmethod
    def parse(cls, value: str) -> "URI":
        return cls.from_url(value)

    @classmethod
    def from_parts(
        cls,
        *,
        scheme: Optional[str] = None,
        authority: str = "",
        path: str = "",
        query: Union[str, Mapping[str, str], Iterable[Tuple[str, str]]] = "",
        fragment: str = ""
    ) -> "URI":
        q = query if isinstance(query, str) else urlencode(query, doseq=True)
        return cls(scheme=scheme or _DEFAULT_SCHEME, authority=authority, path=path, query=q, fragment=fragment)

    # ---------- views ----------
    @property
    def value(self) -> str:
        return str(self)

    def split(self) -> SplitResult:
        return SplitResult(self.scheme, self.authority, self.path, self.query, self.fragment)

    def __str__(self) -> str:
        return urlunsplit(self.split())

    @property
    def _as_dict_(self) -> str:
        # Keeps a simple, explicit structure
        return urlunsplit(self.split())
        return {
            "scheme": self.scheme,
            "authority": self.authority,
            "path": self.path,
            "query": self.query,
            "fragment": self.fragment,
            "value": str(self),
        }

    # Accepts {'resource': '...'} or a plain string, mirroring your original
    @classmethod
    def from_jsonish(cls, data: Union[str, Mapping[str, str]]) -> "URI":
        if isinstance(data, str):
            return cls.from_url(data)
        if isinstance(data, Mapping):
            raw = data.get("resource") or data.get("value") or ""
            if raw:
                return cls.from_url(raw)
        raise ValueError(f"Cannot build URI from: {data!r}")

    # ---------- functional updaters ----------
    def with_scheme(self, scheme: str) -> "URI": return self.replace(scheme=scheme)
    def with_authority(self, authority: str) -> "URI": return self.replace(authority=authority)
    def with_path(self, path: str, *, join: bool = False) -> "URI":
        new_path = (self.path.rstrip("/") + "/" + path.lstrip("/")) if join else path
        return self.replace(path=new_path)
    def with_fragment(self, fragment: str | None) -> "URI":
        return self.replace(fragment=(fragment or ""))
    def without_fragment(self) -> "URI": return self.replace(fragment="")
    def with_query(self, query: Union[str, Mapping[str, str], Iterable[Tuple[str, str]]]) -> "URI":
        q = query if isinstance(query, str) else urlencode(query, doseq=True)
        return self.replace(query=q)
    def add_query_params(self, params: Mapping[str, Union[str, Iterable[str]]]) -> "URI":
        existing = parse_qsl(self.query, keep_blank_values=True)
        for k, v in params.items():
            if isinstance(v, str):
                existing.append((k, v))
            else:
                for vv in v:
                    existing.append((k, vv))
        return self.replace(query=urlencode(existing, doseq=True))

    # ---------- helpers ----------
    def replace(self, **kwargs) -> "URI":
        return URI(
            scheme=kwargs.get("scheme", self.scheme or _DEFAULT_SCHEME),
            authority=kwargs.get("authority", self.authority),
            path=kwargs.get("path", self.path),
            query=kwargs.get("query", self.query),
            fragment=kwargs.get("fragment", self.fragment),
        )
