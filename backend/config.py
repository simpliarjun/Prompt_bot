"""
Application configuration using pydantic-settings.
Loads and validates all environment variables from §15.
"""

from typing import Optional, Union
from pydantic import Field, field_validator, SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    All configuration loaded from environment variables / .env file.
    """

    # --- AI ---
    GEMINI_API_KEY: SecretStr = Field(..., description="Google Gemini API key")
    GEMINI_MODEL_NAME: str = Field(
        default="gemini-3.5-flash",
        description="Gemini model ID for letter generation",
    )

    # --- MongoDB ---
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    MONGODB_DB_NAME: str = Field(
        default="cgms",
        description="MongoDB database name",
    )

    # --- JWT ---
    JWT_SECRET_KEY: SecretStr = Field(..., description="JWT signing secret (32+ random bytes)")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, gt=0)

    # --- CORS ---
    # Correction #11: Accept a comma-separated string and split it.
    CORS_ALLOWED_ORIGINS: Union[str, list[str]] = Field(
        default=["http://localhost:5173"],
        description="Comma-separated list of allowed CORS origins",
    )

    @field_validator("CORS_ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Accept both a JSON list and a bare comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # --- Rate Limiting ---
    RATE_LIMIT_GENERATIONS_PER_DAY: int = Field(
        default=20, gt=0, description="Max AI generation calls per user per UTC day"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton — imported by other modules.
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Return the cached Settings instance (created on first call)."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
