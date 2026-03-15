# FootballBot

A Discord/Telegram chatbot that helps soccer players organize and find matches. Built with [Strands Agents](https://github.com/strands-agents/sdk-python), [FastMCP](https://gofastmcp.com), and OpenAI.

## Architecture

```
Discord/Telegram  -->  Strands Agent (OpenAI)  -->  MCP Server (FastMCP)  -->  PostgreSQL
                        + UserContextHook           (separate repo)
                        + per-user history           footballserver/
```

This repo contains the **bot** (agent + Discord/Telegram clients). The MCP server lives in a separate [`footballserver`](https://github.com/titopuertolara/footballserver) repo.

- **Strands Agent** — per-user conversation history, async invocation (`invoke_async`), `UserContextHook` for secure param injection
- **MCP Server** — connects via `FOOTBALLBOT_MCP_SERVER_URL` over `streamable-http`

## Features

- **Create games** — organize matches with location, date, time, game type, grass type, players needed
- **Find games** — search by location, date, or position
- **Join request flow** — players send requests, organizers get DM notifications with Accept/Reject buttons
- **Accept/Reject notifications** — players receive a DM when their request is accepted or rejected
- **Player subscription** — register with position, skill level, location, availability
- **Find players** — search for available players by filters with clickable mentions
- **Position synonyms** — "volante", "mediocampista", and "midfielder" are treated as equivalent
- **Auto-close** — games close automatically 2 hours before start
- **Guardrails** — bot only responds to soccer/football topics
- **Timezone-aware** — resolves relative dates ("tomorrow", "next Saturday") correctly

## Setup

### Prerequisites

- Python 3.12+
- Discord bot token (and/or Telegram bot token)
- OpenAI API key
- Running instance of [footballserver](https://github.com/titopuertolara/footballserver)

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your tokens and MCP server URL
```

### Run

```bash
python -m app.main
```

The bot connects to the MCP server at `FOOTBALLBOT_MCP_SERVER_URL` (default: `http://localhost:8000/mcp`).

## Project Structure

```
app/
  agent/
    agent.py          # Model and MCP client factory
    hooks.py          # UserContextHook — injects user identity into tool calls
    prompt.yaml       # System prompt (editable without code changes)
  bot/
    discord.py        # Discord client, button views, DM notifications
    handler.py        # Per-user agent management, invocation_state
    telegram.py       # Telegram handler
  config.py           # Pydantic settings from .env
  main.py             # Entry point
docs/
  manual_usuario.md   # User manual (Spanish)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FOOTBALLBOT_PLATFORM` | `discord` or `telegram` | `telegram` |
| `FOOTBALLBOT_DISCORD_TOKEN` | Discord bot token | — |
| `FOOTBALLBOT_TELEGRAM_TOKEN` | Telegram bot token | — |
| `FOOTBALLBOT_OPENAI_API_KEY` | OpenAI API key | — |
| `FOOTBALLBOT_OPENAI_MODEL_ID` | OpenAI model | `gpt-4o-mini` |
| `FOOTBALLBOT_MCP_SERVER_URL` | MCP server endpoint | `http://localhost:8000/mcp` |
| `FOOTBALLBOT_TIMEZONE` | Timezone for date resolution | `America/Bogota` |

## License

MIT.
