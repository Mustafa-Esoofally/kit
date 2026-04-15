"""
Database File Path
------------------

Resolve the SQLite file path from env, with a sensible default.
"""

from os import getenv
from pathlib import Path

_DEFAULT = Path(__file__).parent.parent / "tmp" / "kit.db"
db_file = getenv("KIT_DB_FILE") or str(_DEFAULT)
