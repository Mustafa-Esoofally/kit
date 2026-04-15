"""Custom knowledge tool — lets the agent save metadata to kit_learnings."""

from agno.knowledge import Knowledge
from agno.tools import tool


def create_update_knowledge(knowledge: Knowledge):
    """Create an update_knowledge tool bound to a specific knowledge base.

    The returned tool lets the agent save metadata (discoveries, source
    capabilities, patterns) to the knowledge base.

    Args:
        knowledge: The Knowledge instance to insert into.

    Returns:
        A tool function that the agent can call.
    """

    @tool
    def update_knowledge(title: str, content: str) -> str:
        """Save metadata to the knowledge base.

        Use this to record structural information about Kit's context:
        - Discoveries: where information was found for specific topics
        - Source capabilities: what tools are available
        - Patterns: how recurring tasks are handled

        Args:
            title: A descriptive title prefixed with its category
                (e.g. "Discovery: Project X", "Source: Files",
                "Pattern: Weekly standup").
            content: The metadata content describing the resource.

        Returns:
            Confirmation message.
        """
        knowledge.insert(name=title, text_content=content)
        return f"Knowledge updated: {title}"

    return update_knowledge
