from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = "sqlite:///./agent.db"
    redis_url: str = "redis://localhost:6379/0"
    frontend_origin: str = "http://localhost:5173"
    workflow_cache_ttl: int = 3600
    dashboard_log_limit: int = 200
    gemini_api_key: str = ""


settings = Settings()
