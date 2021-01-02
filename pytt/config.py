import os
from pathlib import Path

DATA_DIR = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local/share")) / "pytt"

if not DATA_DIR.exists():
    DATA_DIR.mkdir()

DB_PATH = DATA_DIR / "db.sqlite"

if not DB_PATH.exists():
    DATA_DIR.touch()
