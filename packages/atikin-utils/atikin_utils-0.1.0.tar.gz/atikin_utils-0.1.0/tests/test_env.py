from pathlib import Path
from atikin_utils import Env

def test_env(tmp_path: Path):
    envfile = tmp_path / ".env"
    envfile.write_text("X=1\nY=hello\n")
    e = Env(envfile)
    parsed = e.load()
    assert parsed["X"] == "1"
    assert e.get("Y") == "hello"
    e.set("Z", "world", persist=True)
    assert (envfile.exists())
