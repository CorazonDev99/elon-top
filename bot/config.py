from pydantic_settings import BaseSettings
from pydantic import SecretStr
import json


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_ids: list[int] = []
    admin_card_number: str = ""
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    bot_channel_id: int = 0  # Telegram channel ID for auto-posting news
    guarantee_hours: int = 48  # Auto-refund after N hours if not published

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
