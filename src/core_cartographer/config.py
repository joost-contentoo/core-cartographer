"""Configuration management for Core Cartographer."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError
from .logging_config import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API Configuration
    anthropic_api_key: str = Field(..., description="Anthropic API key")
    model: str = Field(
        default="claude-opus-4-5-20251101",
        description="Claude model to use for extraction",
    )

    # Directory Configuration
    input_dir: Path = Field(default=Path("./input"), description="Input documents directory")
    output_dir: Path = Field(default=Path("./output"), description="Output directory")
    templates_dir: Path = Field(default=Path("./templates"), description="Templates directory")
    instructions_dir: Path = Field(
        default=Path("./instructions"), description="Instructions directory"
    )

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that the API key is not empty."""
        if not v or not v.strip():
            raise ValueError("ANTHROPIC_API_KEY cannot be empty")
        return v.strip()

    @property
    def client_rules_example_path(self) -> Path:
        """Path to the client rules example file."""
        return self.templates_dir / "client_rules_example.js"

    @property
    def guidelines_example_path(self) -> Path:
        """Path to the guidelines example file."""
        return self.templates_dir / "guidelines_example.md"

    @property
    def extraction_instructions_path(self) -> Path:
        """Path to the extraction instructions."""
        return self.instructions_dir / "extraction_instructions.md"


@lru_cache
def get_settings() -> Settings:
    """
    Load and return application settings.

    Settings are cached after first load for performance.

    Returns:
        Configured Settings instance.

    Raises:
        ConfigurationError: If required settings are missing or invalid.
    """
    try:
        settings = Settings()
        logger.debug(f"Settings loaded: model={settings.model}")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        raise ConfigurationError(f"Failed to load settings: {e}")
