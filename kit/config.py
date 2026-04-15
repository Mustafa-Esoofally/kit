from os import getenv
from pathlib import Path

from kit.paths import CONTEXT_DIR

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
TELEGRAM_TOKEN = getenv("TELEGRAM_TOKEN", "")

SLACK_TOKEN = getenv("SLACK_TOKEN", "")
SLACK_SIGNING_SECRET = getenv("SLACK_SIGNING_SECRET", "")

KIT_CONTEXT_DIR = Path(getenv("KIT_CONTEXT_DIR") or str(CONTEXT_DIR))

KIT_MODEL = getenv("KIT_MODEL", "gpt-4o-mini")
