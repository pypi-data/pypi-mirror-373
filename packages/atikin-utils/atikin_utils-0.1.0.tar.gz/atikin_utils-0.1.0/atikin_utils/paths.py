import os

def ensure_dir(path: str) -> str:
    """Ensure a directory exists, if not create it."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

def ensure_file(path: str) -> str:
    """Ensure a file exists, if not create an empty one."""
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
    return path
