"""
Kit Agent
=========

The single agent users interact with. Handles chat, memory, learnings,
files, and web search.

Mirrors pal/agents/navigator.py but without the team leader, wiki tools,
Gmail, Calendar, or SQL tools.
"""

from agno.agent import Agent
from agno.learn import LearnedKnowledgeConfig, LearningMachine, LearningMode
from agno.models.openai import OpenAIChat

from kit.agents.settings import agent_db, kit_learnings
from kit.config import KIT_MODEL
from kit.instructions import build_navigator_instructions
from kit.tools import build_navigator_tools

navigator = Agent(
    id="navigator",
    name="Kit",
    role="Personal agent for user interaction, memory, learnings, files, and web search",
    model=OpenAIChat(id=KIT_MODEL),
    db=agent_db,
    instructions=build_navigator_instructions(),
    knowledge=kit_learnings,
    search_knowledge=True,
    learning=LearningMachine(
        knowledge=kit_learnings,
        learned_knowledge=LearnedKnowledgeConfig(mode=LearningMode.AGENTIC),
    ),
    tools=build_navigator_tools(kit_learnings),
    enable_agentic_memory=True,
    search_past_sessions=True,
    num_past_sessions_to_search=5,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=10,
    markdown=True,
)
