"""Tests for document parsing."""

from pathlib import Path

import pytest

from core_cartographer.exceptions import UnsupportedFormatError
from core_cartographer.parser import (
    SUPPORTED_EXTENSIONS,
    get_supported_files,
    parse_document,
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
        """Test that unsupported formats raise UnsupportedFormatError."""
        file_path = tmp_path / "test.xyz"
        file_path.write_text("content")

        with pytest.raises(UnsupportedFormatError, match="Unsupported file format"):
            parse_document(file_path)

    def test_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Test that missing files raise FileNotFoundError."""
        file_path = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            parse_document(file_path)

    def test_parse_utf8_content(self, tmp_path: Path) -> None:
        """Test parsing a file with UTF-8 characters."""
        file_path = tmp_path / "utf8.txt"
        content = "Héllo Wörld! 日本語 🎉"
        file_path.write_text(content, encoding="utf-8")

        result = parse_document(file_path)

        assert result == content

    def test_parse_empty_file(self, tmp_path: Path) -> None:
        """Test parsing an empty file."""
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        result = parse_document(file_path)

        assert result == ""


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

    def test_returns_sorted_files(self, tmp_path: Path) -> None:
        """Test that files are returned in sorted order."""
        (tmp_path / "z_file.txt").write_text("z")
        (tmp_path / "a_file.txt").write_text("a")
        (tmp_path / "m_file.txt").write_text("m")

        result = get_supported_files(tmp_path)

        assert result[0].name == "a_file.txt"
        assert result[1].name == "m_file.txt"
        assert result[2].name == "z_file.txt"


class TestSupportedExtensions:
    """Tests for SUPPORTED_EXTENSIONS constant."""

    def test_expected_extensions(self) -> None:
        """Test that expected extensions are supported."""
        expected = {".txt", ".md", ".docx", ".pdf"}
        assert SUPPORTED_EXTENSIONS == expected
