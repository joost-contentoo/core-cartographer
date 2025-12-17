"""Document parsing utilities for various file formats."""

from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx", ".pdf"}


def parse_document(file_path: Path) -> str:
    """
    Parse a document and return its text content.

    Args:
        file_path: Path to the document file.

    Returns:
        Extracted text content from the document.

    Raises:
        ValueError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {suffix}")

    if suffix in {".txt", ".md"}:
        return _parse_text_file(file_path)
    elif suffix == ".docx":
        return _parse_docx(file_path)
    elif suffix == ".pdf":
        return _parse_pdf(file_path)

    raise ValueError(f"Unsupported file format: {suffix}")


def _parse_text_file(file_path: Path) -> str:
    """Parse a plain text or markdown file."""
    return file_path.read_text(encoding="utf-8")


def _parse_docx(file_path: Path) -> str:
    """Parse a Word document and extract text."""
    doc = Document(file_path)
    paragraphs = [paragraph.text for paragraph in doc.paragraphs]
    return "\n\n".join(paragraphs)


def _parse_pdf(file_path: Path) -> str:
    """Parse a PDF document and extract text."""
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    return "\n\n".join(text_parts)


def get_supported_files(directory: Path) -> list[Path]:
    """
    Get all supported document files in a directory.

    Args:
        directory: Directory to scan for documents.

    Returns:
        List of paths to supported document files.
    """
    if not directory.exists():
        return []

    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(directory.glob(f"*{ext}"))

    return sorted(files)
