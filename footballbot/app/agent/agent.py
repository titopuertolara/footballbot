from pathlib import Path

import yaml
from strands import Agent
from strands.models.openai import OpenAIModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamable_http_client

from app.config import settings

PROMPT_PATH = Path(__file__).parent / "prompt.yaml"


def load_system_prompt() -> str:
    with open(PROMPT_PATH) as f:
        data = yaml.safe_load(f)
    return data["system_prompt"]


SYSTEM_PROMPT = load_system_prompt()


def create_model() -> OpenAIModel:
    return OpenAIModel(
        client_args={"api_key": settings.openai_api_key},
        model_id=settings.openai_model_id,
    )


def create_mcp_client() -> MCPClient:
    return MCPClient(
        lambda: streamable_http_client(url=settings.mcp_server_url)
    )
