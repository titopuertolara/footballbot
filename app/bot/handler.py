import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from strands import Agent

from app.agent.agent import create_mcp_client, create_model, SYSTEM_PROMPT
from app.agent.hooks import UserContextHook
from app.config import settings

logger = logging.getLogger(__name__)

mcp_client = None
user_agents: dict[str, Agent] = {}


def get_mcp_client():
    """Lazily initialize and return the shared MCP client."""
    global mcp_client
    if mcp_client is None:
        mcp_client = create_mcp_client()
        mcp_client.__enter__()
    return mcp_client


def get_agent_for_user(user_key: str) -> Agent:
    """Get or create an agent for a specific user, preserving conversation history."""
    if user_key not in user_agents:
        client = get_mcp_client()
        model = create_model()
        tools = client.list_tools_sync()
        user_agents[user_key] = Agent(
            model=model,
            tools=tools,
            system_prompt=SYSTEM_PROMPT.format(
                today=datetime.now(ZoneInfo(settings.timezone)).strftime("%Y-%m-%d %H:%M %Z"),
            ),
            hooks=[UserContextHook()],
        )
    return user_agents[user_key]


def _extract_tool_metadata(messages: list) -> dict | None:
    """Check recent agent messages for actionable tool results."""
    metadata = {}
    # Only check the last few messages (current turn)
    for msg in messages[-4:]:
        content = msg.get("content", [])
        for block in content:
            if not isinstance(block, dict) or "toolResult" not in block:
                continue
            tool_content = block["toolResult"].get("content", [])
            for item in tool_content:
                if not isinstance(item, dict) or "text" not in item:
                    continue
                try:
                    data = json.loads(item["text"])
                except (json.JSONDecodeError, TypeError):
                    continue
                if not data.get("success"):
                    continue
                # Join request created → notify organizer
                if data.get("request_id") and data.get("organizer_platform_user_id"):
                    metadata["notify_organizer"] = data
                # Player accepted → notify player
                if data.get("player_added") is not True and data.get("player_platform_user_id") and data.get("spots_remaining") is not None:
                    metadata["accepted_player"] = data
                # Player rejected → notify player
                if data.get("player_platform_user_id") and data.get("request_id") and data.get("spots_remaining") is None:
                    metadata["rejected_player"] = data
    return metadata if metadata else None


async def process_message(platform: str, user_id: str, username: str, name: str, text: str) -> tuple[str, dict | None]:
    """Process a user message through the agent without blocking the event loop."""
    prompt = (
        f"[Platform: {platform}, User: user_id={user_id}, "
        f"username=@{username or 'unknown'}, "
        f"name={name or 'unknown'}]\n"
        f"{text}"
    )
    logger.info(f"[{platform}] Message from {user_id} (@{username}): {text}")

    user_key = f"{platform}:{user_id}"
    agent = get_agent_for_user(user_key)

    # Pass user context via invocation_state so the hook injects it into tool calls
    invocation_state = {
        "platform": platform,
        "organizer_user_id": user_id,
        "organizer_username": username,
        "organizer_name": name,
        "player_user_id": user_id,
        "player_username": username,
        "player_name": name,
    }

    result = await agent.invoke_async(prompt, invocation_state=invocation_state)

    # Extract text response
    content = result.message.get("content", [])
    texts = [block["text"] for block in content if isinstance(block, dict) and "text" in block]
    response_text = texts[-1] if texts else str(result)

    # Check for actionable tool results (join requests, accepted players)
    metadata = _extract_tool_metadata(agent.messages[-4:])

    return response_text, metadata
