"""Shared settings for the Kit agent — DB and knowledge bases."""

from db import create_knowledge, get_db

agent_db = get_db()
kit_learnings = create_knowledge("Kit Learnings", "kit_learnings")
