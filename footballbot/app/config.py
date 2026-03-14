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
    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str = "footballbot"
    db_user: str = "postgres"
    db_password: str = "postgres"
    mcp_server_url: str = "http://localhost:8000/mcp"
    timezone: str = "America/Bogota"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
