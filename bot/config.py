from pydantic_settings import BaseSettings
from pydantic import SecretStr
import json


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_ids: list[int] = []
    admin_card_number: str = ""
    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
