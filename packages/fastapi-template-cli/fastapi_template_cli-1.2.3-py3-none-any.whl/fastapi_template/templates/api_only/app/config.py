"""
Application configuration using Pydantic settings.
"""

from typing import List

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings."""

    # Project metadata
    PROJECT_NAME: str = "FastAPI API Only"
    DESCRIPTION: str = "A modular FastAPI application template"
    VERSION: str = "1.0.0"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = {"development", "staging", "production"}
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v.lower()

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
