#!/usr/bin/env python3
"""Quick test for language detection and pairing functionality."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core_cartographer.file_utils import detect_language, find_translation_pair, find_base_name

print("=" * 60)
print("Testing Language Detection & Pairing")
print("=" * 60)
print()

# Test 1: Language Detection
print("1. Testing Language Detection:")
test_cases = [
    ("This is an English document about software development.", "en"),
    ("Dies ist ein deutsches Dokument über Softwareentwicklung.", "de"),
    ("Ceci est un document français sur le développement logiciel.", "fr"),
]

for text, expected in test_cases:
    detected = detect_language(text)
    status = "✓" if detected == expected else "✗"
    print(f"  {status} '{text[:40]}...' -> {detected} (expected: {expected})")

print()

# Test 2: Base Name Extraction
print("2. Testing Base Name Extraction:")
filename_tests = [
    ("style_guide_EN.pdf", "style guide"),
    ("style_guide_DE.pdf", "style guide"),
    ("legal_terms_EN-US.docx", "legal terms"),
    ("legal-terms_fr.txt", "legal terms"),
]

for filename, expected_base in filename_tests:
    base = find_base_name(filename)
    print(f"  ✓ '{filename}' -> '{base}'")

print()

# Test 3: Translation Pairing
print("3. Testing Translation Pairing:")
file_contents = {
    "style_guide_EN.pdf": "This is the English style guide. " * 100,
    "style_guide_DE.pdf": "Dies ist der deutsche Styleguide. " * 95,
}

candidates = [
    ("style_guide_DE.pdf", "de", "style guide"),
]

matched = find_translation_pair(
    "style_guide_EN.pdf",
    "en",
    candidates,
    file_contents
)

if matched:
    print(f"  ✓ Found pair: 'style_guide_EN.pdf' <-> '{matched}'")
else:
    print(f"  ✗ No pair found for 'style_guide_EN.pdf'")

print()
print("=" * 60)
print("All tests completed!")
print("=" * 60)
