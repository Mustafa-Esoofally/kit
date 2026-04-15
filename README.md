# Kit (a simpler Pal)

Kit is a single-agent personal assistant that lives in Telegram, remembers you across sessions, and learns from its own mistakes. It's a pared-down sibling of [Pal](https://github.com/agno-agi/pal) — same codebase shape, same storage stack, fewer features.

You chat with Kit from Telegram on your phone and it quietly accumulates three layers of memory about you: the conversation history of the current thread, durable facts about who you are and what you prefer, and vector-searched corrections from anything that went wrong in previous runs. A post-run hook picks up failed runs and files them as `Correction:` entries so future similar requests retrieve the fix automatically — the mechanism behind "Day 30 Kit > Day 1 Kit".

Where Pal has five specialist agents, a wiki compilation pipeline, and integrations for Gmail, Calendar, and Slack, Kit has one agent, three memory layers, and Telegram. It exists as a readable starting point — clone it, read it in thirty minutes, extend it.

Chat with Kit via Telegram or the [AgentOS](https://os.agno.com) web UI. Every interaction goes through the same three layers:

1. **Session memory** — conversation history within a single Telegram thread
2. **User memory** — facts, preferences, and context that persist across sessions and threads
3. **Learned memory** — vector-searched corrections and patterns that compound over time

The whole thing runs in two Docker containers — one Postgres, one uvicorn — with no external services required.

## Quick Start

```sh
# Clone the repo
git clone https://github.com/Mustafa-Esoofally/kit
cd kit

# Add OPENAI_API_KEY and TELEGRAM_TOKEN
cp example.env .env
# Edit .env and add your keys

# Start the application
docker compose up -d --build
```

Confirm Kit is running at [http://localhost:8000/health](http://localhost:8000/health).

### Connect to the Web UI

1. Open [os.agno.com](https://os.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-example&utm_content=kit&utm_term=agentos) and login
2. Add OS → Local → `http://localhost:8000`
3. Click "Connect"

### Connect to Telegram

1. Create a bot with [@BotFather](https://t.me/botfather) and copy the token into `.env` as `TELEGRAM_TOKEN`
2. Expose your local kit with [ngrok](https://ngrok.com): `ngrok http 8000`
3. Register the webhook with Telegram:

```sh
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
     --data-urlencode "url=https://<your-ngrok-subdomain>.ngrok-free.app/telegram/webhook"
```

4. Open Telegram, search for your bot, and send a message. Kit will reply.

## How It Works

Kit is one agent, not a team:

```
Kit (kit/agents/navigator.py)
├── OpenAIChat (gpt-4o-mini)           — the default model, override via KIT_MODEL
├── FileTools                          — read/write user-authored context files
├── DuckDuckGoTools                    — free web search, no API key required
├── update_knowledge                   — save metadata to the learning store
├── LearningMachine (AGENTIC mode)     — vector-searched learned memory
└── post_hooks=[error_learning_hook]   — catches failed runs, saves Corrections
```

### Three Memory Layers

Kit's memory is modeled after the three-layer framework from [Memory: How Agents Learn](https://www.ashpreetbedi.com/articles/memory):

1. **Session memory** (`agno_sessions`): Conversation history per session, keyed by `session_id`. Automatically injected into the model context on each turn via `add_history_to_context=True` (last 10 runs).

2. **User memory** (`agno_memories`): Persistent facts about the user, extracted automatically by `enable_agentic_memory=True`. Survives across sessions and Telegram threads. Keyed by `user_id` (the Telegram user ID).

3. **Learned memory** (`kit_learnings_contents` + PgVector): Vector-searched reusable patterns and corrections. Populated automatically by the `error_learning_hook` post-hook when runs fail at the framework level, and explicitly by `save_learning` tool calls during normal conversation.

### Execution Loop

Every interaction follows the same loop (mirrored from Pal's Navigator):

1. **Classify** intent from the input message
2. **Recall** — search `kit_learnings` and session history
3. **Read** from the right sources: user memory, files, web
4. **Act** — execute tool calls
5. **Learn** — if the run errors out, the post-hook saves a `Correction:` entry automatically

### Error-Learning Post-Hook

The one feature Kit has that Pal doesn't: `kit/hooks.py` attaches to the agent via `post_hooks=[error_learning_hook]`. When an agent run fails at the framework level (`RunStatus.error`), the hook:

1. Extracts the user message that triggered the failed run
2. Builds a dated `Correction:` entry with the user request and the error text
3. Inserts it into the `kit_learnings` vector store

The next similar request retrieves the correction via hybrid search, and the agent sees what went wrong last time — and is instructed to try a different approach. This is the mechanism behind *"Day 30 Kit > Day 1 Kit"*: errors compound into fixes that compound into better default behavior.

Individual tool errors do **not** trigger the hook. Tool errors are normal recoverable events — agno wraps them as tool messages and the agent decides in-flight whether to retry, swap tools, or inform the user. Only when the whole run fails (model down, context overflow, hard crash) does the hook fire.

## Integrations

Kit starts with Telegram + Postgres. Everything else is the three memory layers and the local filesystem.

<details>
<summary><strong>Telegram (required)</strong></summary>

Kit needs a Telegram bot and a public URL for Telegram's Bot API to webhook into.

#### 1. Create a bot

1. Open Telegram, search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the prompts (pick a name and a username)
3. Copy the bot token → `TELEGRAM_TOKEN` in your `.env`

#### 2. Get a public URL

For local development, use [ngrok](https://ngrok.com/download/mac-os):

```sh
ngrok http 8000
```

Copy the `https://` URL (e.g. `https://abc123.ngrok-free.app`).

#### 3. Register the webhook

```sh
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
     --data-urlencode "url=https://<your-ngrok-subdomain>.ngrok-free.app/telegram/webhook" \
     --data-urlencode "drop_pending_updates=true"
```

Verify with:

```sh
curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"
```

#### 4. Dev vs. production secret tokens

For local testing, set `APP_ENV=development` in your `.env`. Telegram webhook secret validation is bypassed in development mode.

For production, set `TELEGRAM_WEBHOOK_SECRET_TOKEN` to a random string and pass the same value via the `secret_token` parameter when calling `setWebhook`:

```sh
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
     --data-urlencode "url=https://<your-domain>/telegram/webhook" \
     --data-urlencode "secret_token=${TELEGRAM_WEBHOOK_SECRET_TOKEN}"
```

#### 5. Restart Kit

```sh
docker compose up -d --build
```

Send a message to your bot from Telegram and you should get a response.

</details>

## Example Prompts

```
Remember that my name is Mustafa and I live in Jersey City.
What do you remember about me?
Search the web for recent news on personal AI agents and summarize the top three results.
Save a note at projects/standup.md with a summary of what we discussed.
What was the last thing I asked you about?
Tell me a one-line joke about docker containers.
Create a note at daily/briefing.md, then read it back to confirm the content.
Correction: my favorite editor isn't Vim — it's Cursor. Please update your memory.
```

## Scheduled Tasks

Kit ships with one cron task (all times `America/New_York`):

| Task | Schedule | Description |
|------|----------|-------------|
| Morning Briefing | Weekdays 8 AM | Summarizes yesterday's conversations, lists open items, flags anything forgotten |

Add more schedules in `app/main.py:_register_schedules()`. The `ScheduleManager` API mirrors pal's.

## Architecture

```
AgentOS (app/main.py)  [scheduler=True, tracing=True, authorization=(runtime_env == "prd")]
 ├── FastAPI / Uvicorn
 ├── Telegram Interface (agno.os.interfaces.telegram.Telegram)
 ├── Custom Router (app/router.py → /health)
 └── Kit Agent (kit/agents/navigator.py)
     ├─ OpenAIChat (gpt-4o-mini)
     ├─ db             → PostgresDb (sessions + user memory)
     ├─ knowledge      → kit_learnings (PgVector hybrid search)
     ├─ learning       → LearningMachine (LearnedKnowledgeConfig, AGENTIC mode)
     ├─ post_hooks     → [error_learning_hook]
     ├─ FileTools      → context/
     ├─ DuckDuckGoTools → web search
     └─ update_knowledge → custom tool factory (kit/tools/knowledge.py)

     Memory: three layers
       session  → agno_sessions (add_history_to_context, num_history_runs=10)
       user     → agno_memories (enable_agentic_memory)
       learned  → kit_learnings (PgVector + error_learning_hook)
```

### Sources

| Source | Purpose | Availability |
|--------|---------|--------------|
| `agno_memories` | User memory — auto-extracted preferences and facts | Always |
| `kit_learnings` | Learned memory — corrections, patterns, retrieval strategies | Always |
| `context/` | User-authored files (read/write via FileTools) | Always |
| DuckDuckGo | Free general web search | Always (can be rate-limited) |
| Telegram | Primary chat interface | Requires `TELEGRAM_TOKEN` |

### Storage

| Layer | What goes there |
|-------|-----------------|
| PostgreSQL | `agno_sessions`, `agno_memories`, `kit_learnings_contents`, PgVector embeddings, scheduler rows |
| `context/` | User-authored files and kit-generated notes, drafts, exports |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/agents/navigator/runs` | POST | Run the Kit agent with a prompt (auto-registered by AgentOS) |
| `/telegram/webhook` | POST | Telegram Bot API webhook receiver |
| `/telegram/status` | GET | Telegram interface status |
| `/health` | GET | Health check |

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | — | OpenAI key for gpt-4o-mini (or whatever `KIT_MODEL` is) |
| `TELEGRAM_TOKEN` | Yes | — | Telegram bot token from @BotFather |
| `TELEGRAM_WEBHOOK_SECRET_TOKEN` | Production | — | Required in production for webhook validation |
| `KIT_MODEL` | No | `gpt-4o-mini` | Override the default model |
| `KIT_CONTEXT_DIR` | No | `./context` | Directory for user-authored context files |
| `KIT_PORT` | No | `8000` | Host port mapping for the kit-api container |
| `DB_HOST` | No | `localhost` (host) / `kit-db` (compose) | PostgreSQL host |
| `DB_PORT` | No | `5432` | PostgreSQL port |
| `DB_USER` | No | `ai` | PostgreSQL user |
| `DB_PASS` | No | `ai` | PostgreSQL password |
| `DB_DATABASE` | No | `ai` | PostgreSQL database |
| `RUNTIME_ENV` | No | `dev` | `prd` enables JWT authorization |
| `APP_ENV` | No | — | Set to `development` to bypass Telegram webhook secret validation |
| `AGENTOS_URL` | No | `http://127.0.0.1:8000` | Scheduler callback URL |
| `JWT_VERIFICATION_KEY` | Production | — | RBAC public key from os.agno.com |

## Troubleshooting

**Telegram messages not arriving**: Run `curl "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"` — if `pending_update_count` is growing, the webhook URL is unreachable. Verify ngrok is running and the URL was registered via `setWebhook`.

**`ModuleNotFoundError: No module named 'ddgs'`**: The package was renamed from `duckduckgo-search` to `ddgs`. Ensure `pyproject.toml` lists `"ddgs"` in `dependencies`.

**`ImportError: pyTelegramBotAPI not installed`**: `pyproject.toml` must use `"agno[os,telegram]"` as the extras group. `agno[os]` alone does not include the Telegram Bot API library.

**`ValueError: At least one JWT verification key or JWKS file is required`**: You're running with `RUNTIME_ENV=prd` but haven't set `JWT_VERIFICATION_KEY`. For local use, either set `RUNTIME_ENV=dev` (recommended) or provide a real verification key.

**Port 8000 already in use**: Another project is listening on 8000. Set `KIT_PORT=7777` (or another free port) in your `.env` before running `docker compose up`. The container still uses 8000 internally; only the host mapping changes.

**Docker build fails with `ddgs` install error**: Rebuild with `docker compose build --no-cache kit-api` to invalidate the pip layer.

## Differences From Pal

| Pal | Kit |
|-----|-----|
| 5-agent team (Navigator, Researcher, Compiler, Linter, Syncer) | Single agent (`kit/agents/navigator.py`) |
| Slack as primary interface | Telegram as the only interface |
| Wiki compilation pipeline (`raw/` → `wiki/`) | Dropped |
| Git sync to GitHub (`Syncer` agent) | Dropped |
| Google OAuth (Gmail + Calendar) | Dropped |
| Agent-owned SQL schema (`pal_*` tables created on demand) | Dropped — memory layers only |
| Parallel web research + Exa MCP | DuckDuckGo only |
| 7 scheduled cron tasks | 1 scheduled cron task (morning briefing) |
| `gpt-5.4` default | `gpt-4o-mini` default |
| Governance tiers, approval flows | Dropped |
| `pal/team.py` + 5 agent files + wiki/ingest/git tools | `kit/agents/navigator.py` + `kit/hooks.py` only |
| ~48 source files, ~2500 LOC | ~32 source files, ~450 LOC |

Diff the two repos file by file to see exactly what was removed and what stayed. Most files in kit have an identical twin in pal.

## Links

- [Pal](https://github.com/agno-agi/pal) — the parent repo Kit was trimmed down from
- [Memory: How Agents Learn](https://www.ashpreetbedi.com/articles/memory) — the three-layer memory framework Kit is built around
- [Agent Engineering 101](https://www.ashpreetbedi.com/articles/agent-engineering) — framework + runtime + control plane triad
- [Agno Docs](https://docs.agno.com?utm_source=github&utm_medium=example-repo&utm_campaign=agent-example&utm_content=kit&utm_term=docs)
- [AgentOS Docs](https://docs.agno.com/agent-os/introduction?utm_source=github&utm_medium=example-repo&utm_campaign=agent-example&utm_content=kit&utm_term=docs)

## License

MIT
