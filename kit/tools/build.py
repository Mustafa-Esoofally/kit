"""Tool assembly — builds the tool list for the Kit agent."""

from agno.knowledge import Knowledge
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools

from kit.config import KIT_CONTEXT_DIR
from kit.tools.knowledge import create_update_knowledge


def build_navigator_tools(knowledge: Knowledge) -> list:
    """Tools for the Kit agent — files, web search, knowledge."""
    KIT_CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
    return [
        FileTools(base_dir=KIT_CONTEXT_DIR, enable_delete_file=False),
        DuckDuckGoTools(),
        create_update_knowledge(knowledge),
    ]
