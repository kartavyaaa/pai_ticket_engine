from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.
    Values are loaded from .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # ===========================
    # API
    # ===========================
    APP_NAME: str = "PAI Ticket Engine"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ===========================
    # DATABASE
    # ===========================
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/pai.db"
    )

    # ===========================
    # OPENAI
    # ===========================
    OPENAI_API_KEY: str

    OPENAI_MODEL: str = "gpt-4.1-mini"

    OPENAI_TIMEOUT: int = 60

    # ===========================
    # FILES
    # ===========================
    MAX_UPLOAD_SIZE_MB: int = 50

    ALLOWED_FILE_TYPES: list[str] = [
        ".xlsx",
        ".xls",
        ".csv"
    ]

    # ===========================
    # LOGGING
    # ===========================
    LOG_LEVEL: str = "INFO"

    # ===========================
    # CORS
    # ===========================
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8501",
        "http://localhost:3000"
    ]


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()