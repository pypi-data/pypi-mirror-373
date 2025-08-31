"""
Application configuration using Pydantic v2 settings.
Production-ready configuration with validation and security.
"""

import secrets
from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    # Project metadata
    PROJECT_NAME: str = "FastAPI Full-stack"
    DESCRIPTION: str = "Production-ready FastAPI application with database and security"
    VERSION: str = "1.0.0"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # API settings
    API_V1_STR: str = "/api/v1"

    # Security settings
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_fullstack"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        """Assemble database connection string."""
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # MongoDB settings for Beanie backend
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "fastapi_fullstack"

    # Redis settings (for caching)
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]], info: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid BACKEND_CORS_ORIGINS format: {v}")

    # Host settings
    ALLOWED_HOSTS: List[str] = ["*"]

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]], info: Any) -> List[str]:
        """Parse allowed hosts from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid ALLOWED_HOSTS format: {v}")

    # Email settings
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # First superuser
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "admin"

    # Users settings
    USERS_OPEN_REGISTRATION: bool = True

    # Backend type for unified authentication
    BACKEND_TYPE: str = "sqlalchemy"

    @field_validator("BACKEND_TYPE")
    @classmethod
    def validate_backend_type(cls, v: str) -> str:
        """Validate backend type setting."""
        valid_backends = {"sqlalchemy", "beanie"}
        v_lower = v.lower()
        if v_lower not in valid_backends:
            raise ValueError(f"BACKEND_TYPE must be one of {valid_backends}")
        return v_lower

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        valid_environments = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        return v_lower

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # ignore unexpected env vars
    )


# Global settings instance
settings = Settings()
