"""Document parsing utilities for various file formats."""

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader

from .exceptions import DocumentParsingError, UnsupportedFormatError
from .logging_config import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx", ".pdf"}


def parse_document(file_path: Path) -> str:
    """
    Parse a document and return its text content.

    Args:
        file_path: Path to the document file.

    Returns:
        Extracted text content from the document.

    Raises:
        UnsupportedFormatError: If the file format is not supported.
        FileNotFoundError: If the file does not exist.
        DocumentParsingError: If the document cannot be parsed.
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        logger.error(f"Unsupported file format: {suffix}")
        raise UnsupportedFormatError(
            f"Unsupported file format: {suffix}",
            file_path=str(file_path),
        )

    logger.debug(f"Parsing document: {file_path}")

    try:
        if suffix in {".txt", ".md"}:
            return _parse_text_file(file_path)
        elif suffix == ".docx":
            return _parse_docx(file_path)
        elif suffix == ".pdf":
            return _parse_pdf(file_path)
    except (UnsupportedFormatError, FileNotFoundError):
        raise
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        raise DocumentParsingError(
            f"Failed to parse document: {e}",
            file_path=str(file_path),
            original_error=e,
        )

    raise UnsupportedFormatError(
        f"Unsupported file format: {suffix}",
        file_path=str(file_path),
    )


def _parse_text_file(file_path: Path) -> str:
    """Parse a plain text or markdown file."""
    content = file_path.read_text(encoding="utf-8")
    logger.debug(f"Parsed text file: {file_path} ({len(content)} chars)")
    return content


def _parse_docx(file_path: Path) -> str:
    """Parse a Word document and extract text."""
    doc = DocxDocument(str(file_path))
    paragraphs = [paragraph.text for paragraph in doc.paragraphs]
    content = "\n\n".join(paragraphs)
    logger.debug(f"Parsed DOCX: {file_path} ({len(paragraphs)} paragraphs)")
    return content


def _parse_pdf(file_path: Path) -> str:
    """Parse a PDF document and extract text."""
    reader = PdfReader(file_path)
    text_parts = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)

    content = "\n\n".join(text_parts)
    logger.debug(f"Parsed PDF: {file_path} ({len(reader.pages)} pages)")
    return content


def get_supported_files(directory: Path) -> list[Path]:
    """
    Get all supported document files in a directory.

    Args:
        directory: Directory to scan for documents.

    Returns:
        List of paths to supported document files.
    """
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []

    files: list[Path] = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(directory.glob(f"*{ext}"))

    logger.debug(f"Found {len(files)} supported files in {directory}")
    return sorted(files)
