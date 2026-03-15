from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FOOTBALLBOT_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    platform: str = "telegram"  # "telegram" or "discord"
    telegram_token: str = ""
    discord_token: str = ""
    openai_api_key: str = ""
    openai_model_id: str = "gpt-4o-mini"
    mcp_server_url: str = "http://localhost:8000/mcp"
    timezone: str = "America/Bogota"


settings = Settings()
