import tempfile
from pathlib import Path
from atikin_utils import auto_create, auto_backup

def test_auto_create_and_backup(tmp_path: Path):
    file = tmp_path / "foo" / "bar.txt"
    auto_create(file, "hello")
    assert file.exists()
    b = auto_backup(file)
    assert b.exists()
