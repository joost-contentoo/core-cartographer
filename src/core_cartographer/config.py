"""Configuration management for Core Cartographer."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


def get_settings() -> Settings:
    """Load and return application settings."""
    return Settings()
