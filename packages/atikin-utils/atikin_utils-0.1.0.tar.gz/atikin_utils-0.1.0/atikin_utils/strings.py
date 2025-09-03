"""String helper utilities."""

from __future__ import annotations
import re
import unicodedata
from typing import Any


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text)


def snake_case(s: str) -> str:
    s = _normalize(s)
    s = re.sub(r"[^\w\s\-]", "", s)
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def camel_case(s: str, lower_first: bool = False) -> str:
    s = _normalize(s)
    parts = re.split(r"[_\-\s]+", s)
    if not parts:
        return ""
    result = "".join(p.capitalize() for p in parts if p)
    if lower_first and result:
        result = result[0].lower() + result[1:]
    return result


def kebab_case(s: str) -> str:
    s = _normalize(s)
    s = re.sub(r"[^\w\s\-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = s.strip("-").lower()
    return s


def title_case(s: str) -> str:
    return " ".join(word.capitalize() for word in s.split())


def truncate(s: str, max_len: int = 30, ellipsis: str = "...") -> str:
    if len(s) <= max_len:
        return s
    keep = max(0, max_len - len(ellipsis))
    return s[:keep] + ellipsis


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def safe_format(fmt: str, /, **kwargs: Any) -> str:
    """
    Format while leaving unknown placeholders intact.
    Example: safe_format("Hi {name} {missing}", name="Jamshed") -> "Hi Jamshed {missing}"
    """
    return fmt.format_map(_SafeDict(**kwargs))


def slugify(s: str, sep: str = "-") -> str:
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"[-\s]+", sep, s)
    return s
