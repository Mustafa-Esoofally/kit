"""
Database Session
----------------

SQLite for sessions + ChromaDb for vector search. Zero setup — both are
local files under tmp/. Swap out for Postgres + pgvector if you outgrow
SQLite.
"""

from pathlib import Path

from agno.db.sqlite import SqliteDb
from agno.knowledge import Knowledge
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.vectordb.chroma import ChromaDb

from db.url import db_file

DB_ID = "kit-db"

_CHROMA_PATH = Path(__file__).parent.parent / "tmp" / "chromadb"


def get_db() -> SqliteDb:
    """Create a SqliteDb instance. Ensures tmp/ exists."""
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    return SqliteDb(id=DB_ID, db_file=db_file)


def create_knowledge(name: str, collection: str) -> Knowledge:
    """Create a Knowledge instance backed by ChromaDb.

    Args:
        name: Display name for the knowledge base.
        collection: ChromaDb collection name (one per logical store).

    Returns:
        Configured Knowledge instance sharing the SqliteDb as contents store.
    """
    _CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    return Knowledge(
        name=name,
        vector_db=ChromaDb(
            name=collection,
            path=str(_CHROMA_PATH),
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        ),
        contents_db=get_db(),
    )
