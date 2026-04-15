# Kit

A simpler personal agent. Based on [pal](https://github.com/agno-agi/pal).

Kit is a single-agent version of pal — no team, no wiki compilation pipeline, no Postgres. Just an agent that:

- Talks to you on Telegram
- Remembers what you tell it
- Learns reusable patterns from your interactions
- Uses tools to take action
- Runs scheduled tasks unattended

## Quick Start

```sh
# Clone
git clone https://github.com/agno-agi/kit
cd kit

# Install
pip install -e .

# Configure
cp example.env .env
# Edit .env: add OPENAI_API_KEY and TELEGRAM_TOKEN

# Run
python -m app.main
```

Then open Telegram and send your bot a message.

## How It Works

Kit is one agent doing the job PAL's five-member team does, without the wiki compilation pipeline. It has three context systems:

1. **Learnings** (`kit_learnings`) — operational memory of what works. Vector-searched via ChromaDb.
2. **Files** (`context/`) — user-authored preferences, notes, templates.
3. **User Memory** — auto-managed by Agno, remembers facts about the user across sessions.

## Architecture

Kit mirrors pal's structure so you can diff the two repos and see what changed:

| Pal | Kit | Change |
|---|---|---|
| 5-agent team (`pal/team.py`) | Single agent (`kit/agents/navigator.py`) | No coordinator, no specialists |
| Postgres + pgvector | SQLite + ChromaDb | Zero-setup start |
| Slack interface | Telegram (primary) + Slack (optional) | Phone-first |
| Wiki compilation pipeline | None | Dropped |
| Git sync | None | Dropped |
| Google OAuth (Gmail + Calendar) | None (opt-in later) | Dropped for v1 |
| 7 cron jobs | 1 cron job (morning briefing) | Trimmed |
| `gpt-5.4` | `gpt-4o-mini` | Cheaper by default |

## Interfaces

| Interface | Required? | Env var |
|---|---|---|
| Telegram | Yes | `TELEGRAM_TOKEN` |
| Slack | Optional | `SLACK_TOKEN` + `SLACK_SIGNING_SECRET` |

## License

MIT
