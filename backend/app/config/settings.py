from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Arena Enterprise"
    DEBUG: bool = True

    # Database - يقرأ من environment أو SQLite كـ fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ai_arena.db")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # AI Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    class Config:
        env_file = ".env"


settings = Settings()
