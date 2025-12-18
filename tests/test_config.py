"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from core_cartographer.config import Settings, get_settings
from core_cartographer.exceptions import ConfigurationError


class TestSettings:
    """Tests for Settings class."""

    def test_settings_with_api_key(self) -> None:
        """Test creating settings with API key."""
        settings = Settings(anthropic_api_key="test-key-123")
        assert settings.anthropic_api_key == "test-key-123"

    def test_default_model(self) -> None:
        """Test that default model is set correctly."""
        settings = Settings(anthropic_api_key="test-key")
        assert settings.model == "claude-opus-4-5-20251101"

    def test_custom_model(self) -> None:
        """Test setting custom model."""
        settings = Settings(anthropic_api_key="test-key", model="claude-sonnet-4-20250514")
        assert settings.model == "claude-sonnet-4-20250514"

    def test_default_directories(self) -> None:
        """Test default directory paths."""
        settings = Settings(anthropic_api_key="test-key")
        assert settings.input_dir == Path("./input")
        assert settings.output_dir == Path("./output")
        assert settings.templates_dir == Path("./templates")
        assert settings.instructions_dir == Path("./instructions")

    def test_custom_directories(self) -> None:
        """Test setting custom directory paths."""
        settings = Settings(
            anthropic_api_key="test-key",
            input_dir=Path("/custom/input"),
            output_dir=Path("/custom/output"),
        )
        assert settings.input_dir == Path("/custom/input")
        assert settings.output_dir == Path("/custom/output")

    def test_api_key_validation_empty(self) -> None:
        """Test that empty API key raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Settings(anthropic_api_key="")

    def test_api_key_validation_whitespace(self) -> None:
        """Test that whitespace-only API key raises validation error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Settings(anthropic_api_key="   ")

    def test_api_key_strips_whitespace(self) -> None:
        """Test that API key whitespace is stripped."""
        settings = Settings(anthropic_api_key="  test-key  ")
        assert settings.anthropic_api_key == "test-key"


class TestSettingsPropertyPaths:
    """Tests for Settings property paths."""

    def test_client_rules_example_path(self) -> None:
        """Test client rules example path property."""
        settings = Settings(anthropic_api_key="test-key")
        expected = Path("./templates/client_rules_example_condensed.js")
        assert settings.client_rules_example_path == expected

    def test_guidelines_example_path(self) -> None:
        """Test guidelines example path property."""
        settings = Settings(anthropic_api_key="test-key")
        expected = Path("./templates/guidelines_example_condensed.md")
        assert settings.guidelines_example_path == expected

    def test_extraction_instructions_path(self) -> None:
        """Test extraction instructions path property."""
        settings = Settings(anthropic_api_key="test-key")
        expected = Path("./instructions/extraction_instructions.md")
        assert settings.extraction_instructions_path == expected

    def test_custom_templates_dir_affects_paths(self) -> None:
        """Test that custom templates_dir affects path properties."""
        settings = Settings(anthropic_api_key="test-key", templates_dir=Path("/custom/templates"))
        expected_rules = Path("/custom/templates/client_rules_example_condensed.js")
        expected_guidelines = Path("/custom/templates/guidelines_example_condensed.md")
        assert settings.client_rules_example_path == expected_rules
        assert settings.guidelines_example_path == expected_guidelines


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_with_env_var(self) -> None:
        """Test loading settings from environment variable."""
        # Clear the lru_cache
        get_settings.cache_clear()

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "env-test-key"}):
            settings = get_settings()
            assert settings.anthropic_api_key == "env-test-key"

        # Clear cache after test
        get_settings.cache_clear()

    def test_get_settings_caches_result(self) -> None:
        """Test that get_settings caches the result."""
        get_settings.cache_clear()

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "cached-key"}):
            settings1 = get_settings()
            settings2 = get_settings()
            assert settings1 is settings2

        get_settings.cache_clear()

    def test_get_settings_missing_api_key_raises_error(self, tmp_path: Path, monkeypatch) -> None:
        """Test that missing API key raises ConfigurationError."""
        get_settings.cache_clear()

        # Change to a temp directory without .env file
        monkeypatch.chdir(tmp_path)

        # Remove ANTHROPIC_API_KEY from environment
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ConfigurationError):
            get_settings()

        get_settings.cache_clear()


class TestSettingsFromEnv:
    """Tests for loading settings from environment variables."""

    def test_model_from_env(self) -> None:
        """Test loading model from environment."""
        get_settings.cache_clear()

        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "test-key", "MODEL": "claude-sonnet-4-20250514"}
        ):
            settings = get_settings()
            assert settings.model == "claude-sonnet-4-20250514"

        get_settings.cache_clear()

    def test_directories_from_env(self) -> None:
        """Test loading directories from environment."""
        get_settings.cache_clear()

        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "test-key",
                "INPUT_DIR": "/env/input",
                "OUTPUT_DIR": "/env/output",
            },
        ):
            settings = get_settings()
            assert settings.input_dir == Path("/env/input")
            assert settings.output_dir == Path("/env/output")

        get_settings.cache_clear()
