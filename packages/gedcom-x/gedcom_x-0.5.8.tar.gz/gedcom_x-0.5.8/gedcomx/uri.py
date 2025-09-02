from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Sequence, Tuple, Union, Iterable
from urllib.parse import urlsplit, urlunsplit, urlencode, parse_qsl, SplitResult

_DEFAULT_SCHEME = "gedcomx"

# ---------- typing helpers for urlencode (Option A) ----------
QuerySeq = Sequence[Tuple[str, str]]
QueryMap = Mapping[str, str]
QueryLike = Union[str, QueryMap, QuerySeq]

def _encode_query(q: QueryLike) -> str:
    """Return a properly encoded query string."""
    if isinstance(q, str):
        return q
    if isinstance(q, Mapping):
        return urlencode(q, doseq=True)          # mapping is fine
    return urlencode(list(q), doseq=True)        # coerce iterable to a sequence


@dataclass(slots=True)
class URI:
    scheme: str = field(default=_DEFAULT_SCHEME)
    authority: str = field(default="")
    path: str = field(default="")
    query: str = field(default="")
    fragment: str = field(default="")

    # ---------- constructors ----------
    @classmethod
    def from_url(cls, url: str, *, default_scheme: str = _DEFAULT_SCHEME) -> URI:
        s = urlsplit(url)
        scheme = s.scheme or default_scheme
        return cls(scheme=scheme, authority=s.netloc, path=s.path, query=s.query, fragment=s.fragment)

    @classmethod
    def parse(cls, value: str) -> URI:
        return cls.from_url(value)

    @classmethod
    def from_parts(
        cls,
        *,
        scheme: str | None = None,
        authority: str = "",
        path: str = "",
        query: QueryLike = "",
        fragment: str = "",
    ) -> URI:
        q = _encode_query(query)
        return cls(scheme=scheme or _DEFAULT_SCHEME, authority=authority, path=path, query=q, fragment=fragment)

    # ---------- views ----------
    @property
    def uri(self) -> str:
        return str(self)
    
    @property
    def value(self) -> str:
        return str(self)

    def split(self) -> SplitResult:
        return SplitResult(self.scheme, self.authority, self.path, self.query, self.fragment)

    def __str__(self) -> str:
        return urlunsplit(self.split())

    @property
    def _as_dict_(self) -> dict[str, object]:
        return {
            "scheme": self.scheme,
            "authority": self.authority,
            "path": self.path,
            "query": self.query,
            "fragment": self.fragment,
            "value": str(self),
        }

    # Accepts {'resource': '...'} or a plain string
    @classmethod
    def from_jsonish(cls, data: str | Mapping[str, object]) -> URI:
        if isinstance(data, str):
            return cls.from_url(data)
        if isinstance(data, Mapping):
            raw = data.get("resource") or data.get("value") or ""
            if isinstance(raw, str) and raw:
                return cls.from_url(raw)
        raise ValueError(f"Cannot build URI from: {data!r}")

    # ---------- functional updaters ----------
    def with_scheme(self, scheme: str) -> URI: return self.replace(scheme=scheme)
    def with_authority(self, authority: str) -> URI: return self.replace(authority=authority)
    def with_path(self, path: str, *, join: bool = False) -> URI:
        new_path = (self.path.rstrip("/") + "/" + path.lstrip("/")) if join else path
        return self.replace(path=new_path)
    def with_fragment(self, fragment: str | None) -> URI:
        return self.replace(fragment=(fragment or ""))
    def without_fragment(self) -> URI: return self.replace(fragment="")
    def with_query(self, query: QueryLike) -> URI:
        return self.replace(query=_encode_query(query))
    def add_query_params(self, params: Mapping[str, Union[str, Iterable[str]]]) -> URI:
        existing = parse_qsl(self.query, keep_blank_values=True)
        for k, v in params.items():
            if isinstance(v, str):
                existing.append((k, v))
            else:
                for vv in v:
                    existing.append((k, vv))
        return self.replace(query=urlencode(existing, doseq=True))

    # ---------- helpers ----------
    def replace(self, **kwargs) -> URI:
        cls = type(self)
        return cls(
            scheme=kwargs.get("scheme", self.scheme or _DEFAULT_SCHEME),
            authority=kwargs.get("authority", self.authority),
            path=kwargs.get("path", self.path),
            query=kwargs.get("query", self.query),
            fragment=kwargs.get("fragment", self.fragment),
        )
