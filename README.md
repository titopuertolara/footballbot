# FootballBot

A Discord/Telegram chatbot that helps soccer players organize and find matches. Built with [Strands Agents](https://github.com/strands-agents/sdk-python), [FastMCP](https://gofastmcp.com), and OpenAI.

## Architecture

```
Discord/Telegram  -->  Strands Agent (OpenAI)  -->  MCP Server (FastMCP)  -->  PostgreSQL
                        + UserContextHook           streamable-http
                        + per-user history           async SQLAlchemy
```

- **Strands Agent** — per-user conversation history, async invocation (`invoke_async`), `UserContextHook` for secure param injection
- **MCP Server** — FastMCP with `streamable-http` transport, `stateless_http=True`, `@lifespan` for DB lifecycle, `exclude_args` to hide sensitive params from the LLM
- **Database** — PostgreSQL with async SQLAlchemy + asyncpg

## Features

- **Create games** — organize matches with location, date, time, game type, grass type, players needed
- **Find games** — search by location, date, or position
- **Join request flow** — players send requests, organizers get DM notifications with Accept/Reject buttons
- **Player subscription** — register with position, skill level, location, availability
- **Find players** — organizers search for available players by filters
- **Auto-close** — games close automatically 2 hours before start
- **Clickable mentions** — Discord `<@user_id>` mentions for easy DM contact
- **Guardrails** — bot only responds to soccer/football topics
- **Timezone-aware** — resolves relative dates ("tomorrow", "next Saturday") correctly

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL
- Discord bot token (and/or Telegram bot token)
- OpenAI API key

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Database

Start PostgreSQL with Docker:

```bash
docker compose up -d
```

Or use an existing PostgreSQL instance. Tables are created automatically on MCP server startup.

### Configure

```bash
cp .env.example .env
# Edit .env with your tokens and credentials
```

### Run

Start the MCP server and bot in separate terminals:

```bash
# Terminal 1: MCP Server
python -m app.mcp_server.server

# Terminal 2: Bot
python -m app.main
```

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
  mcp_server/
    server.py         # FastMCP tools with exclude_args
    database/
      models.py       # SQLAlchemy models (User, Game, GamePlayer, JoinRequest)
      connection.py   # Async engine and session factory
    services/
      game_service.py # Game CRUD, join requests, auto-close
      user_service.py # User CRUD, player subscription, search
  config.py           # Pydantic settings from .env
  main.py             # Entry point
docs/
  manual_usuario.md   # User manual (Spanish)
```

## MCP Tools

| Tool | Description | Hidden params |
|------|-------------|---------------|
| `create_game` | Create a match | platform, organizer identity |
| `find_games` | Search open games | — |
| `get_game_details` | Game info with players | — |
| `request_to_join_game` | Send join request | platform, player identity |
| `accept_join_request` | Accept a request | platform, organizer identity |
| `reject_join_request` | Reject a request | platform, organizer identity |
| `get_pending_requests` | View pending requests | platform, organizer identity |
| `add_player_to_game` | Direct add (organizer) | platform, both identities |
| `subscribe_player` | Register as player | platform, player identity |
| `update_player_profile` | Update profile | platform, player identity |
| `find_players` | Search players | — |

Hidden params are injected at runtime by `UserContextHook` via `invocation_state`, following the same pattern as [pbn-ml-mcp-server](https://github.com/Provectus-PBN/pbn-ml-mcp-server).

## License

MIT
