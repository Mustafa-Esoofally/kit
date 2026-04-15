# Kit

A simpler personal agent. Based on [pal](https://github.com/agno-agi/pal).

Kit is a single-agent version of pal — no team, no wiki compilation pipeline. Just an agent that:

- Talks to you on Telegram
- Remembers what you tell it
- Learns from its mistakes

## Quick Start

```sh
# Clone
git clone https://github.com/agno-agi/kit
cd kit

# Configure
cp example.env .env
# Edit .env: add OPENAI_API_KEY and TELEGRAM_TOKEN

# Run
docker compose up -d --build
```

Then open Telegram and send your bot a message.

## How It Works

Kit has three memory layers (Ashpreet's canonical framing):

1. **Session Memory** — conversation history, kept in Postgres keyed by `session_id`
2. **User Memory** — auto-extracted facts about the user, kept in Postgres keyed by `user_id`
3. **Learned Memory** — corrections and patterns, vector-searched via PgVector

Plus one mechanism that makes kit get better over time:

- **Error-learning post_hook** — when a run fails, the hook saves a `Correction` entry to the learned-memory store. Future similar requests retrieve the correction via vector search and the agent tries a different approach.

## Architecture

Kit mirrors pal's structure so you can diff the two repos and see what changed:

| Pal | Kit | Change |
|---|---|---|
| 5-agent team | Single agent | No coordinator, no specialists |
| Slack interface | Telegram | Phone-first |
| Wiki compilation pipeline | None | Dropped |
| Git sync | None | Dropped |
| Google OAuth | None | Dropped for v1 |
| 7 cron jobs | 1 cron job | Trimmed |
| `gpt-5.4` | `gpt-4o-mini` | Cheaper by default |

## Interface

Telegram only. Set `TELEGRAM_TOKEN` in your `.env`.

## License

MIT
