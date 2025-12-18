"""Tests for file utilities."""

import pytest

from core_cartographer.file_utils import (
    LANGUAGE_CODES,
    calculate_content_similarity,
    detect_language,
    extract_language_from_filename,
    find_base_name,
    find_translation_pair,
    fuzzy_similarity,
)


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_detect_english(self) -> None:
        """Test detecting English text."""
        text = "Hello, this is a sample text in English for testing purposes."
        result = detect_language(text)
        assert result == "EN"

    def test_detect_german(self) -> None:
        """Test detecting German text."""
        text = "Hallo, dies ist ein Beispieltext auf Deutsch für Testzwecke."
        result = detect_language(text)
        assert result == "DE"

    def test_detect_french(self) -> None:
        """Test detecting French text."""
        text = "Bonjour, ceci est un texte exemple en français à des fins de test."
        result = detect_language(text)
        assert result == "FR"

    def test_empty_text(self) -> None:
        """Test with empty text."""
        result = detect_language("")
        assert result == "UNKNOWN"

    def test_whitespace_only(self) -> None:
        """Test with whitespace-only text."""
        result = detect_language("   \n\t   ")
        assert result == "UNKNOWN"

    def test_sample_size_limit(self) -> None:
        """Test that only sample_size characters are used."""
        # Create a long text
        long_text = "This is English. " * 1000
        result = detect_language(long_text, sample_size=100)
        assert result == "EN"


class TestExtractLanguageFromFilename:
    """Tests for extract_language_from_filename function."""

    def test_underscore_format(self) -> None:
        """Test extracting language from underscore format."""
        assert extract_language_from_filename("card_EN.txt") == "EN"
        assert extract_language_from_filename("document_DE.docx") == "DE"

    def test_hyphen_format(self) -> None:
        """Test extracting language from hyphen format."""
        assert extract_language_from_filename("card-EN.txt") == "EN"
        assert extract_language_from_filename("document-FR.docx") == "FR"

    def test_parentheses_format(self) -> None:
        """Test extracting language from parentheses format."""
        assert extract_language_from_filename("card(EN).txt") == "EN"
        assert extract_language_from_filename("document(NL).docx") == "NL"

    def test_brackets_format(self) -> None:
        """Test extracting language from brackets format."""
        assert extract_language_from_filename("card[EN].txt") == "EN"
        assert extract_language_from_filename("document[ES].docx") == "ES"

    def test_lowercase_filename(self) -> None:
        """Test with lowercase filename (should still work)."""
        assert extract_language_from_filename("card_en.txt") == "EN"

    def test_no_language_code(self) -> None:
        """Test when there's no language code."""
        assert extract_language_from_filename("document.txt") is None
        assert extract_language_from_filename("myfile.docx") is None

    def test_invalid_language_code(self) -> None:
        """Test with invalid language code (not in LANGUAGE_CODES)."""
        assert extract_language_from_filename("card_XX.txt") is None


class TestFindBaseName:
    """Tests for find_base_name function."""

    def test_remove_underscore_language(self) -> None:
        """Test removing underscore language code."""
        assert find_base_name("card_EN.txt") == "card"
        assert find_base_name("gift_cards_DE.txt") == "gift_cards"

    def test_remove_hyphen_language(self) -> None:
        """Test removing hyphen language code."""
        assert find_base_name("card-EN.txt") == "card"
        assert find_base_name("gift-cards-FR.txt") == "gift-cards"

    def test_remove_trailing_language(self) -> None:
        """Test removing trailing language code."""
        assert find_base_name("card_EN.txt") == "card"
        assert find_base_name("gift_cards DE.txt") == "gift_cards"

    def test_normalize_separators(self) -> None:
        """Test that multiple separators are normalized."""
        assert find_base_name("card__EN.txt") == "card"

    def test_lowercase_result(self) -> None:
        """Test that result is lowercase."""
        assert find_base_name("MyCard_EN.txt") == "mycard"

    def test_strip_leading_trailing(self) -> None:
        """Test stripping leading/trailing separators."""
        assert find_base_name("_card_EN.txt") == "card"


class TestFuzzySimilarity:
    """Tests for fuzzy_similarity function."""

    def test_exact_match(self) -> None:
        """Test exact string match."""
        assert fuzzy_similarity("card", "card") == 1.0

    def test_substring_match(self) -> None:
        """Test substring match."""
        assert fuzzy_similarity("card", "cards") == 0.8
        assert fuzzy_similarity("gift", "gift_card") == 0.8

    def test_partial_match(self) -> None:
        """Test partial character overlap."""
        result = fuzzy_similarity("card", "cart")
        assert 0.0 < result < 1.0

    def test_no_match(self) -> None:
        """Test strings with no common characters."""
        result = fuzzy_similarity("abc", "xyz")
        assert result == 0.0

    def test_empty_string(self) -> None:
        """Test with empty strings."""
        assert fuzzy_similarity("", "card") == 0.0
        assert fuzzy_similarity("card", "") == 0.0
        assert fuzzy_similarity("", "") == 0.0

    def test_case_insensitive(self) -> None:
        """Test that comparison is case-insensitive."""
        assert fuzzy_similarity("Card", "CARD") == 1.0


class TestCalculateContentSimilarity:
    """Tests for calculate_content_similarity function."""

    def test_identical_length(self) -> None:
        """Test content with identical length."""
        assert calculate_content_similarity("hello", "world") == 1.0

    def test_different_lengths(self) -> None:
        """Test content with different lengths."""
        result = calculate_content_similarity("hello", "hi")
        assert result == pytest.approx(2 / 5)

    def test_empty_content(self) -> None:
        """Test with empty content."""
        assert calculate_content_similarity("", "hello") == 0.0
        assert calculate_content_similarity("hello", "") == 0.0
        assert calculate_content_similarity("", "") == 0.0


class TestFindTranslationPair:
    """Tests for find_translation_pair function."""

    def test_exact_base_name_match(self) -> None:
        """Test finding pair with exact base name match."""
        candidates = [
            ("document_DE.txt", "DE", "document"),
            ("other_FR.txt", "FR", "other"),
        ]
        file_contents = {
            "document_EN.txt": "English content",
            "document_DE.txt": "German content",
            "other_FR.txt": "French content",
        }

        result = find_translation_pair(
            "document_EN.txt",
            "EN",
            candidates,
            file_contents,
        )
        assert result == "document_DE.txt"

    def test_no_match_same_language(self) -> None:
        """Test that same language files are not matched."""
        candidates = [
            ("other_EN.txt", "EN", "other"),
        ]
        file_contents = {
            "document_EN.txt": "English content",
            "other_EN.txt": "Other English content",
        }

        result = find_translation_pair(
            "document_EN.txt",
            "EN",
            candidates,
            file_contents,
        )
        assert result is None

    def test_fuzzy_match_with_content_similarity(self) -> None:
        """Test exact base name matching (strict matching enforced)."""
        # After strict base name matching was enforced, only exact base matches work
        candidates = [
            ("document_DE.txt", "DE", "document"),  # Exact base match
            ("other_DE.txt", "DE", "other"),
        ]
        file_contents = {
            "document_EN.txt": "A" * 100,
            "document_DE.txt": "B" * 95,  # Exact base name match
            "other_DE.txt": "C" * 10,
        }

        result = find_translation_pair(
            "document_EN.txt",
            "EN",
            candidates,
            file_contents,
        )
        # Should match document_DE due to exact base name match
        assert result == "document_DE.txt"

    def test_no_suitable_candidates(self) -> None:
        """Test when no candidates meet threshold."""
        candidates = [
            ("xyz_DE.txt", "DE", "xyz"),
        ]
        file_contents = {
            "document_EN.txt": "A" * 100,
            "xyz_DE.txt": "B" * 10,
        }

        result = find_translation_pair(
            "document_EN.txt",
            "EN",
            candidates,
            file_contents,
        )
        assert result is None


class TestLanguageCodes:
    """Tests for LANGUAGE_CODES constant."""

    def test_common_codes_present(self) -> None:
        """Test that common language codes are present."""
        common = ["EN", "DE", "FR", "ES", "IT", "NL", "PT", "JA", "ZH", "KO"]
        for code in common:
            assert code in LANGUAGE_CODES

    def test_codes_are_uppercase(self) -> None:
        """Test that all codes are uppercase."""
        for code in LANGUAGE_CODES:
            assert code == code.upper()

    def test_codes_are_two_chars(self) -> None:
        """Test that all codes are two characters."""
        for code in LANGUAGE_CODES:
            assert len(code) == 2
