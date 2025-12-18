"""File upload and management endpoints."""

from fastapi import APIRouter, UploadFile
from typing import List
import tempfile
from pathlib import Path
import sys
import logging

# Add parent directory to path to import core_cartographer
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from core_cartographer.parser import parse_document
from core_cartographer.cost_estimator import count_tokens
from ...cache.file_cache import file_cache
from ..models.responses import FileParseResponse
from ..dependencies import ValidationError, ProcessingError, NotFoundError, logger

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/parse", response_model=FileParseResponse)
async def parse_file(file: UploadFile):
    """
    Upload and parse a single file. Returns file_id for later use.

    Args:
        file: Uploaded file (PDF, DOCX, TXT, or MD)

    Returns:
        FileParseResponse with file_id, tokens, and preview

    Raises:
        ValidationError: If file type unsupported or too large
        ProcessingError: If parsing fails
    """
    if not file.filename:
        raise ValidationError("No filename provided")

    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Unsupported file type '{ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate size
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise ProcessingError("Failed to read uploaded file")

    if len(content) > MAX_FILE_SIZE:
        raise ValidationError(
            f"File too large ({len(content) / 1024 / 1024:.1f}MB). "
            f"Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    if len(content) == 0:
        raise ValidationError("File is empty")

    # Save to temp file for parsing
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        # Parse using existing logic
        text_content = parse_document(tmp_path)

        if not text_content or len(text_content.strip()) == 0:
            raise ProcessingError(f"No text content could be extracted from {file.filename}")

        tokens = count_tokens(text_content)

        # Store in cache
        file_id = file_cache.store(file.filename, text_content, tokens)

        logger.info(f"Successfully parsed file: {file.filename} ({tokens} tokens)")

        # Return metadata + preview (first 500 chars)
        return FileParseResponse(
            file_id=file_id,
            filename=file.filename,
            tokens=tokens,
            preview=text_content[:500] + ("..." if len(text_content) > 500 else ""),
            success=True
        )
    except (ValidationError, ProcessingError):
        raise
    except Exception as e:
        logger.error(f"Failed to parse {file.filename}: {e}")
        raise ProcessingError(f"Failed to parse file: {str(e)}")
    finally:
        # Cleanup temp file
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a cached file.

    Args:
        file_id: Unique file identifier

    Returns:
        Success confirmation

    Raises:
        NotFoundError: If file not found
    """
    if not file_id:
        raise ValidationError("file_id is required")

    if file_cache.delete(file_id):
        logger.info(f"Deleted file: {file_id}")
        return {"success": True, "message": "File deleted successfully"}

    raise NotFoundError(f"File not found: {file_id}")


@router.post("/parse-batch", response_model=List[FileParseResponse])
async def parse_files(files: List[UploadFile]):
    """
    Parse multiple files. Returns list of results (some may have errors).

    Args:
        files: List of uploaded files

    Returns:
        List of FileParseResponse objects (successful and failed)
    """
    if not files:
        raise ValidationError("No files provided")

    if len(files) > 50:
        raise ValidationError("Maximum 50 files per batch")

    results = []
    for file in files:
        try:
            result = await parse_file(file)
            results.append(result)
        except (ValidationError, ProcessingError, NotFoundError) as e:
            logger.warning(f"Failed to parse {file.filename}: {e.detail}")
            results.append(FileParseResponse(
                file_id="",
                filename=file.filename or "unknown",
                tokens=0,
                preview="",
                success=False,
                error=e.detail
            ))
        except Exception as e:
            logger.error(f"Unexpected error parsing {file.filename}: {e}")
            results.append(FileParseResponse(
                file_id="",
                filename=file.filename or "unknown",
                tokens=0,
                preview="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            ))

    logger.info(f"Batch parse complete: {len([r for r in results if r.success])}/{len(results)} successful")
    return results
