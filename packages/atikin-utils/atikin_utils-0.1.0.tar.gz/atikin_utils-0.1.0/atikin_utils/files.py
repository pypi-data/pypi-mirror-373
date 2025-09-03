"""File handling shortcuts."""

from __future__ import annotations
from pathlib import Path
import shutil
import tempfile
import os
from typing import Union


PathLike = Union[str, Path]


def ensure_dir(path: PathLike) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_atomic(path: PathLike, data: str, mode: str = "w", encoding: str = "utf-8") -> None:
    """
    Atomic write: write to temp file then replace.
    """
    p = Path(path)
    ensure_dir(p.parent)
    fd, tmp = tempfile.mkstemp(prefix=p.name, dir=str(p.parent))
    os.close(fd)
    with open(tmp, mode=mode, encoding=encoding) as fh:
        fh.write(data)
    os.replace(tmp, str(p))


def auto_create(path: PathLike, content: str = "", exist_ok: bool = True) -> Path:
    """
    Create file and parent directories if missing. If file exists and exist_ok is False -> raises.
    Returns Path object of the created/existing file.
    """
    p = Path(path)
    ensure_dir(p.parent)
    if p.exists():
        if not exist_ok:
            raise FileExistsError(f"{p} already exists")
        return p
    write_atomic(p, content)
    return p


def auto_backup(file_path: PathLike, backups_dir: PathLike | None = None, keep: int = 5) -> Path:
    """
    Create a timestamped backup of `file_path`. Returns path to backup file.
    By default backups are stored in a `.backups` directory sibling to the file.
    Keeps only `keep` newest backups per original file.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"{p} does not exist to backup")

    parent = p.parent
    backups_dir = Path(backups_dir) if backups_dir else parent / ".backups"
    ensure_dir(backups_dir)

    ts = datetime_now_for_filename()
    backup_name = f"{p.name}.{ts}.bak"
    dest = backups_dir / backup_name
    shutil.copy2(p, dest)

    # rotate
    keep_most_recent_backups(backups_dir, p.name, keep)
    return dest


def datetime_now_for_filename() -> str:
    from datetime import datetime

    return datetime.now().strftime("%Y%m%d%H%M%S")


def keep_most_recent_backups(backups_dir: Path, orig_name: str, keep: int) -> None:
    pattern = f"{orig_name}.*.bak"
    files = sorted(backups_dir.glob(f"{orig_name}.*.bak"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in files[keep:]:
        try:
            old.unlink()
        except Exception:
            pass
