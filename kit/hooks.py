"""Post-hooks for the Kit agent — autonomous learning from errors."""

from datetime import datetime

from agno.agent import Agent
from agno.run.agent import RunOutput
from agno.run.base import RunStatus
from agno.utils.log import log_info, log_warning


def error_learning_hook(
    run_output: RunOutput,
    agent: Agent,
    **kwargs,
) -> None:
    """Catch failed runs and save them as Correction learnings.

    When the agent errors out, we save a dated entry to the learning store so
    that similar future requests retrieve the error via vector search. The
    agent sees what went wrong last time and can try a different approach
    instead of repeating the same mistake.

    This is the mechanism behind "Day 30 Kit > Day 1 Kit".
    """
    if run_output is None or run_output.status != RunStatus.error:
        return

    if agent.knowledge is None:
        return

    # Pull the user message that triggered the failed run
    user_msg = ""
    if run_output.messages:
        for msg in run_output.messages:
            if msg.role == "user" and msg.content:
                user_msg = msg.get_content_string()
                break

    if not user_msg:
        return

    title_snippet = user_msg[:60] + ("..." if len(user_msg) > 60 else "")
    title = f"Correction: {title_snippet}"
    error_content = run_output.content or "(no error content captured)"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = (
        f"Date: {timestamp}\n"
        f"User request: {user_msg}\n"
        f"Error: {error_content}\n\n"
        f"Next time a similar request comes in, check this entry first and try "
        f"a different tool or approach — do not repeat the same steps that failed here."
    )

    try:
        agent.knowledge.insert(name=title, text_content=content)
        log_info(f"[kit.hooks] Saved error learning: {title}")
    except Exception as e:
        log_warning(f"[kit.hooks] Failed to save error learning: {e}")
