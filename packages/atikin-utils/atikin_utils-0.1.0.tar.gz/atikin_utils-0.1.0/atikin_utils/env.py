"""Tiny environment variable manager (reads/writes simple .env files)."""

from __future__ import annotations
from pathlib import Path
import os
from typing import Optional, Dict, Any


def _strip_quotes(v: str) -> str:
    v = v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def parse_dotenv(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = _strip_quotes(val)
        data[key] = val
    return data


def write_dotenv(path: Path, mapping: Dict[str, str]) -> None:
    lines = []
    for k, v in mapping.items():
        # quote if contains spaces or #
        if " " in v or "#" in v:
            v = f'"{v}"'
        lines.append(f"{k}={v}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class Env:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else Path(".env")
        self._data: Dict[str, str] = {}

    def load(self, override: bool = False) -> Dict[str, str]:
        """
        Load values from .env into os.environ.
        If override=True, overwrite existing environment variables.
        Returns the parsed mapping.
        """
        parsed = parse_dotenv(self.path)
        self._data.update(parsed)
        for k, v in parsed.items():
            if override or (k not in os.environ):
                os.environ[k] = v
        return parsed

    def get(self, key: str, default: Optional[Any] = None, cast: Optional[type] = None) -> Any:
        val = os.getenv(key, None)
        if val is None:
            return default
        if cast:
            try:
                if cast is bool:
                    return val.lower() in ("1", "true", "yes", "on")
                return cast(val)
            except Exception:
                return default
        return val

    def set(self, key: str, value: Any, persist: bool = False) -> None:
        os.environ[key] = str(value)
        self._data[key] = str(value)
        if persist:
            write_dotenv(self.path, self._data)

    def save(self, path: Optional[Path] = None) -> None:
        target = Path(path) if path else self.path
        write_dotenv(target, self._data if self._data else dict(os.environ))
