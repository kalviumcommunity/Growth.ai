from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and .env files."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Growth.ai"
    database_url: str = Field(default="sqlite:///./data/growth_ai.db")
    log_level: str = Field(default="INFO")
    reports_directory: Path = Field(default=Path("artifacts/reports"))
    demo_mode: bool = Field(default=False)

    def ensure_directories(self) -> None:
        self.reports_directory.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
