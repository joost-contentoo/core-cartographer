"""Shared file utilities for language detection and file pairing.

This module provides utilities for detecting document languages
and pairing translation files based on filename patterns and content similarity.
"""

import re
from pathlib import Path

from langdetect import LangDetectException, detect

# Common language codes for filename detection
LANGUAGE_CODES = frozenset([
    "EN", "DE", "FR", "NL", "ES", "IT", "PT", "PL", "RU", "JA", "ZH", "KO",
    "AR", "HE", "TR", "CS", "SK", "HU", "RO", "BG", "HR", "SL", "SR", "UK",
    "DA", "NO", "SV", "FI", "EL", "TH", "VI", "ID", "MS", "TL",
])


def detect_language(text: str, sample_size: int = 1000) -> str:
    """
    Detect language from text content using langdetect.

    Args:
        text: The text content to analyze.
        sample_size: Number of characters to sample for detection.

    Returns:
        Two-letter language code in uppercase, or "UNKNOWN" if detection fails.
    """
    if not text or not text.strip():
        return "UNKNOWN"

    try:
        sample = text[:sample_size]
        lang_code: str = detect(sample)
        return lang_code.upper()
    except LangDetectException:
        return "UNKNOWN"


def extract_language_from_filename(filename: str) -> str | None:
    """
    Extract language code from filename patterns.

    Recognizes patterns like:
    - card_EN.txt -> EN
    - document-DE.docx -> DE
    - file(FR).pdf -> FR
    - content[NL].md -> NL

    Args:
        filename: The filename to parse.

    Returns:
        Two-letter language code if found, None otherwise.
    """
    # Get the stem (filename without extension)
    stem = Path(filename).stem.upper()

    # Pattern 1: language code at end after delimiter: _EN, -EN
    pattern_end = r"[_\-]([A-Z]{2})$"
    match = re.search(pattern_end, stem)
    if match:
        code = match.group(1)
        if code in LANGUAGE_CODES:
            return code

    # Pattern 2: language code in brackets or parentheses: (EN), [EN]
    pattern_brackets = r"[\(\[]([A-Z]{2})[\)\]]"
    match = re.search(pattern_brackets, stem)
    if match:
        code = match.group(1)
        if code in LANGUAGE_CODES:
            return code

    # Pattern 3: language code between delimiters: _EN_, -EN-
    pattern_between = r"[_\-]([A-Z]{2})[_\-]"
    match = re.search(pattern_between, stem)
    if match:
        code = match.group(1)
        if code in LANGUAGE_CODES:
            return code

    return None


def find_base_name(filename: str) -> str:
    """
    Extract base name without language code and extension.

    Strips language codes and normalizes the filename for comparison.

    Args:
        filename: The filename to process.

    Returns:
        Normalized base name in lowercase.

    Examples:
        >>> find_base_name("card_EN.txt")
        'card'
        >>> find_base_name("gift-cards-DE.docx")
        'gift-cards'
        >>> find_base_name("de-DE_amazon__product.docx")
        'amazon_product'
        >>> find_base_name("en-MC-_jeton-cash__product.docx")
        'jeton-cash_product'
    """
    name = Path(filename).stem

    # Remove leading locale patterns: en-GB_, de-DE_, EN-MC_, en-MC-_, "de-DE _", etc.
    # Pattern: two letters, dash, two letters, optional dash, optional space, underscore at start
    name = re.sub(r"^[a-z]{2}-[a-z]{2}-?\s*_", "", name, flags=re.IGNORECASE)

    # Build pattern for valid language codes only
    lang_pattern = "|".join(LANGUAGE_CODES)

    # Remove language codes in various formats (but only valid ones)
    # Pattern: language code between delimiters like _EN_, -DE-, (FR), [NL]
    name = re.sub(rf"[_\-\(\[]({lang_pattern})[_\-\)\]]", "", name, flags=re.IGNORECASE)

    # Remove trailing language codes without delimiters
    name = re.sub(rf"[\s_\-]*({lang_pattern})[\s_\-]*$", "", name, flags=re.IGNORECASE)

    # Normalize multiple separators (including double underscores, dash-underscore combos)
    name = re.sub(r"[\s_\-]{2,}", "_", name)

    # Strip trailing/leading separators
    name = name.strip("_- ")

    # Remove trailing dashes from brand names (e.g., "steam-" -> "steam", "xbox-" -> "xbox")
    # This handles inconsistencies like "de-DE_steam-__product" vs "en-UK_steam__product"
    name = re.sub(r"-+_", "_", name)

    return name.lower()


def fuzzy_similarity(s1: str, s2: str) -> float:
    """
    Calculate simple similarity ratio between two strings.

    Uses a combination of substring matching and character overlap.

    Args:
        s1: First string to compare.
        s2: Second string to compare.

    Returns:
        Similarity score between 0.0 and 1.0.
    """
    if not s1 or not s2:
        return 0.0

    s1, s2 = s1.lower(), s2.lower()

    # Exact match
    if s1 == s2:
        return 1.0

    # Substring match
    if s1 in s2 or s2 in s1:
        return 0.8

    # Character overlap
    common = sum(1 for c in s1 if c in s2)
    return common / max(len(s1), len(s2))


def calculate_content_similarity(content1: str, content2: str) -> float:
    """
    Calculate similarity between two documents based on content length.

    This is a simple heuristic: translation pairs typically have
    similar content lengths.

    Args:
        content1: First document content.
        content2: Second document content.

    Returns:
        Similarity ratio between 0.0 and 1.0.
    """
    if not content1 or not content2:
        return 0.0

    len1, len2 = len(content1), len(content2)
    return min(len1, len2) / max(len1, len2)


def find_translation_pair(
    filename: str,
    language: str,
    candidates: list[tuple[str, str, str]],  # (filename, language, base_name)
    file_contents: dict[str, str],
) -> str | None:
    """
    Find the best translation pair for a file among candidates.

    Only pairs files that have the exact same base name but different languages.

    Args:
        filename: The source filename.
        language: The source file's language code.
        candidates: List of (filename, language, base_name) tuples to search.
        file_contents: Dictionary mapping filenames to their content.

    Returns:
        The matched filename, or None if no suitable pair found.
    """
    my_base = find_base_name(filename)

    for cand_filename, cand_lang, cand_base in candidates:
        # Skip same language
        if cand_lang == language:
            continue

        # Only pair files with exact matching base names
        if my_base and cand_base and my_base == cand_base:
            return cand_filename

    return None
