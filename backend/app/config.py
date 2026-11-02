"""Application configuration loaded from environment variables or .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NyayaAI API"
    database_url: str = "sqlite:///./nyayaai.db"
    cors_origins: str = "http://localhost:5173"
    indian_kanoon_base_url: str = "https://api.indiankanoon.org"
    indian_kanoon_timeout_seconds: float = 20.0

    # Provider credentials are intentionally optional until those integrations
    # are implemented. They must never be shipped to the browser.
    indian_kanoon_api_token: str | None = None
    indian_kanoon_customer: str | None = None
    indian_kanoon_private_key_path: str | None = None
    gnani_api_key_id: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the running process."""
    return Settings()
