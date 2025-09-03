import json
import os
from typing import Any, Dict

try:
    import yaml
except ImportError:
    yaml = None

def load_config(path: str, defaults: Dict[str, Any] = None) -> Dict[str, Any]:
    """Load config from JSON or YAML file. Falls back to defaults."""
    if defaults is None:
        defaults = {}

    if not os.path.exists(path):
        return defaults

    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".json"):
            data = json.load(f)
        elif path.endswith(".yaml") or path.endswith(".yml"):
            if yaml is None:
                raise ImportError("PyYAML is required for YAML config files.")
            data = yaml.safe_load(f)
        else:
            raise ValueError("Unsupported config file format.")

    return {**defaults, **(data or {})}
