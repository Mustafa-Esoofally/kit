"""
Kit AgentOS
===========

The main entry point for Kit.

Run:
    python -m app.main
"""

from contextlib import asynccontextmanager
from os import getenv
from pathlib import Path

from agno.os import AgentOS

from app.router import create_router
from db import get_postgres_db
from kit.agents import navigator
from kit.agents.settings import kit_learnings
from kit.config import TELEGRAM_TOKEN

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
runtime_env = getenv("RUNTIME_ENV", "dev")
scheduler_base_url = getenv("AGENTOS_URL", "http://127.0.0.1:7777")

# ---------------------------------------------------------------------------
# Interfaces
# ---------------------------------------------------------------------------
interfaces: list = []

if TELEGRAM_TOKEN:
    from agno.os.interfaces.telegram import Telegram

    interfaces.append(
        Telegram(
            agent=navigator,
            token=TELEGRAM_TOKEN,
            streaming=True,
            reply_to_mentions_only=False,
        )
    )


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    _register_schedules()
    yield


# ---------------------------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------------------------
agent_os = AgentOS(
    name="Kit",
    tracing=True,
    scheduler=True,
    scheduler_base_url=scheduler_base_url,
    authorization=runtime_env == "prd",
    lifespan=lifespan,
    db=get_postgres_db(),
    agents=[navigator],
    knowledge=[kit_learnings],
    interfaces=interfaces,
    config=str(Path(__file__).parent / "config.yaml"),
)

app = agent_os.get_app()
app.include_router(create_router(agent_os.settings))


# ---------------------------------------------------------------------------
# Startup helpers
# ---------------------------------------------------------------------------
def _register_schedules() -> None:
    """Register scheduled tasks (idempotent — safe on every startup)."""
    from agno.scheduler import ScheduleManager

    mgr = ScheduleManager(get_postgres_db())

    mgr.create(
        name="morning-briefing",
        cron="0 8 * * 1-5",
        endpoint="/agents/navigator/runs",
        payload={
            "message": (
                "Good morning. Give me a quick briefing to start the day:\n"
                "1. Summarize what we talked about yesterday.\n"
                "2. List any open items or follow-ups you remember.\n"
                "3. Flag anything I might have forgotten.\n"
                "Keep it short — a morning scan, not a full report."
            ),
        },
        timezone="America/New_York",
        description="Weekday morning briefing",
        if_exists="update",
    )


if __name__ == "__main__":
    agent_os.serve(
        app="app.main:app",
        reload=runtime_env == "dev",
    )
