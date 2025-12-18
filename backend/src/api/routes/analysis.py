"""File analysis endpoints for language detection and pairing."""

from fastapi import APIRouter
from typing import List
import sys
from pathlib import Path

# Add parent directory to path to import core_cartographer
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from core_cartographer.file_utils import detect_language, find_translation_pair
from ...cache.file_cache import file_cache
from ..models.requests import AnalysisRequest
from ..models.responses import AnalysisResponse
from ..dependencies import ValidationError, ProcessingError, logger

router = APIRouter()


@router.post("/auto-detect", response_model=AnalysisResponse)
async def run_auto_detect(request: AnalysisRequest):
    """
    Run language detection and pairing on cached files.

    Args:
        request: List of file_ids to analyze

    Returns:
        AnalysisResponse with detected languages, pairs, and counts

    Raises:
        ValidationError: If no files provided
        ProcessingError: If language detection fails
    """
    if not request.files or len(request.files) == 0:
        raise ValidationError("No files provided for analysis")

    if len(request.files) > 100:
        raise ValidationError("Maximum 100 files per analysis request")

    logger.info(f"Starting auto-detect for {len(request.files)} files")

    results = []
    missing_files = []

    # First pass: detect languages
    for file_ref in request.files:
        cached = file_cache.get(file_ref.file_id)
        if not cached:
            missing_files.append(file_ref.file_id)
            continue

        try:
            # Detect language from content
            detected_lang = detect_language(cached.content[:1000])  # First 1000 chars

            if not detected_lang:
                detected_lang = "unknown"
                logger.warning(f"Could not detect language for {cached.filename}")

            results.append({
                "file_id": file_ref.file_id,
                "filename": cached.filename,
                "language": detected_lang,
                "pair_id": None
            })
        except Exception as e:
            logger.error(f"Failed to detect language for {file_ref.file_id}: {e}")
            raise ProcessingError(f"Language detection failed for {cached.filename}")

    if missing_files:
        raise ValidationError(f"Files not found in cache: {', '.join(missing_files[:5])}")

    if not results:
        raise ValidationError("No valid files to analyze")

    # Second pass: find pairs
    pair_counter = 1
    paired_ids = set()

    for i, file_a in enumerate(results):
        if file_a["file_id"] in paired_ids:
            continue

        for file_b in results[i+1:]:
            if file_b["file_id"] in paired_ids:
                continue

            # Check if they're a pair
            cached_a = file_cache.get(file_a["file_id"])
            cached_b = file_cache.get(file_b["file_id"])

            if cached_a and cached_b:
                try:
                    is_pair = find_translation_pair(
                        file_a["filename"],
                        file_a["language"],
                        [(file_b["filename"], file_b["language"])],
                        {file_a["filename"]: cached_a.content, file_b["filename"]: cached_b.content}
                    )

                    if is_pair:
                        file_a["pair_id"] = str(pair_counter)
                        file_b["pair_id"] = str(pair_counter)
                        paired_ids.add(file_a["file_id"])
                        paired_ids.add(file_b["file_id"])
                        pair_counter += 1
                        break
                except Exception as e:
                    logger.warning(f"Error checking pair for {file_a['filename']} and {file_b['filename']}: {e}")
                    continue

    paired_count = len([r for r in results if r["pair_id"]])
    unpaired_count = len(results) - paired_count

    logger.info(f"Auto-detect complete: {paired_count // 2} pairs found, {unpaired_count} unpaired files")

    return AnalysisResponse(
        files=results,
        paired_count=paired_count // 2,  # Number of pairs, not paired files
        unpaired_count=unpaired_count
    )
