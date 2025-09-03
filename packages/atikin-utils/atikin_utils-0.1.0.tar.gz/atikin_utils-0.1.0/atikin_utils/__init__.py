"""
Atikin Utils - small utilities for everyday developer tasks.
"""

# Strings
from .strings import (
    snake_case,
    camel_case,
    kebab_case,
    title_case,
    truncate,
    safe_format,
    slugify,
)

# Date & Time
from .dt import (
    now,
    today_str,
    format_datetime,
    to_timestamp,
    from_timestamp,
    humanize_timedelta,
    parse_iso,
)

# Files
from .files import (
    ensure_dir,
    write_atomic,
    auto_create,
    auto_backup,
)

# Environment
from .env import Env

# Logging
from .logging_utils import log_info, log_error, log_warn

# Config
from .config import load_config

# Paths
from .paths import ensure_dir as ensure_dir_path, ensure_file

# Network
from .network import get_json

# CLI
from .cli import success, error, warn

# Security
from .security import gen_token, sha256

# Decorators
from .decorators import timeit, retry

# Async helpers
from .async_utils import run_async


__all__ = [
    # Strings
    "snake_case",
    "camel_case",
    "kebab_case",
    "title_case",
    "truncate",
    "safe_format",
    "slugify",
    # Date & Time
    "now",
    "today_str",
    "format_datetime",
    "to_timestamp",
    "from_timestamp",
    "humanize_timedelta",
    "parse_iso",
    # Files
    "ensure_dir",
    "write_atomic",
    "auto_create",
    "auto_backup",
    # Env
    "Env",
    # Logging
    "log_info",
    "log_error",
    "log_warn",
    # Config
    "load_config",
    # Paths
    "ensure_dir_path",
    "ensure_file",
    # Network
    "get_json",
    # CLI
    "success",
    "error",
    "warn",
    # Security
    "gen_token",
    "sha256",
    # Decorators
    "timeit",
    "retry",
    # Async
    "run_async",
]

__version__ = "1.0.0"
