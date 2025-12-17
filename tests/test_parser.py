"""Tests for document parsing."""

from pathlib import Path
import tempfile

import pytest

from core_cartographer.parser import (
    parse_document,
    get_supported_files,
    SUPPORTED_EXTENSIONS,
)


class TestParseDocument:
    """Tests for parse_document function."""

    def test_parse_txt_file(self, tmp_path: Path) -> None:
        """Test parsing a .txt file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello, world!")

        result = parse_document(file_path)

        assert result == "Hello, world!"

    def test_parse_md_file(self, tmp_path: Path) -> None:
        """Test parsing a .md file."""
        file_path = tmp_path / "test.md"
        file_path.write_text("# Header\n\nSome content")

        result = parse_document(file_path)

        assert "# Header" in result
        assert "Some content" in result

    def test_unsupported_format_raises_error(self, tmp_path: Path) -> None:
        """Test that unsupported formats raise ValueError."""
        file_path = tmp_path / "test.xyz"
        file_path.write_text("content")

        with pytest.raises(ValueError, match="Unsupported file format"):
            parse_document(file_path)

    def test_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Test that missing files raise FileNotFoundError."""
        file_path = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            parse_document(file_path)


class TestGetSupportedFiles:
    """Tests for get_supported_files function."""

    def test_finds_supported_files(self, tmp_path: Path) -> None:
        """Test that supported files are found."""
        (tmp_path / "doc1.txt").write_text("content")
        (tmp_path / "doc2.md").write_text("content")
        (tmp_path / "ignored.xyz").write_text("content")

        result = get_supported_files(tmp_path)

        assert len(result) == 2
        assert any(p.suffix == ".txt" for p in result)
        assert any(p.suffix == ".md" for p in result)

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Test behavior with empty directory."""
        result = get_supported_files(tmp_path)

        assert result == []

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test behavior with nonexistent directory."""
        result = get_supported_files(tmp_path / "nonexistent")

        assert result == []
