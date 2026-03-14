from __future__ import annotations

import logging
from typing import Any

from strands.hooks import HookProvider, HookRegistry
from strands.hooks.events import BeforeToolCallEvent

# Maps each tool to the hidden params it accepts (excluded via exclude_args on the MCP server)
_TOOL_HIDDEN_PARAMS: dict[str, list[str]] = {
    "create_game": ["platform", "organizer_user_id", "organizer_username", "organizer_name"],
    "add_player_to_game": ["platform", "organizer_user_id", "player_user_id", "player_username", "player_name"],
    "subscribe_player": ["platform", "player_user_id", "player_username", "player_name"],
    "update_player_profile": ["platform", "player_user_id"],
    "request_to_join_game": ["platform", "player_user_id", "player_username", "player_name"],
    "accept_join_request": ["platform", "organizer_user_id"],
    "reject_join_request": ["platform", "organizer_user_id"],
    "get_pending_requests": ["platform", "organizer_user_id"],
}

logger = logging.getLogger(__name__)


class UserContextHook(HookProvider):
    """Injects user context from invocation_state into tool calls.

    Only injects hidden params that each specific tool accepts.
    """

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        state = event.invocation_state
        tool_name = event.tool_use.get("name", "unknown")
        tool_input: dict[str, Any] = event.tool_use["input"]

        hidden_params = _TOOL_HIDDEN_PARAMS.get(tool_name, [])
        injected = []
        for key in hidden_params:
            value = state.get(key)
            if value is not None and key not in tool_input:
                tool_input[key] = value
                injected.append(key)
        if injected:
            logger.info(f"[UserContextHook] Injected {injected} into {tool_name}")
