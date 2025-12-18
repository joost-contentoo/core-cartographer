"""Response models for API endpoints."""

from typing import Any

from pydantic import BaseModel


class FileParseResponse(BaseModel):
    """Response after parsing a file."""
    file_id: str
    filename: str
    tokens: int
    preview: str
    success: bool
    error: str | None = None


class FileMetadata(BaseModel):
    """Metadata for a cached file."""
    file_id: str
    filename: str
    language: str
    pair_id: str | None


class AnalysisResponse(BaseModel):
    """Response from auto-detection analysis."""
    files: list[dict[str, Any]]
    paired_count: int
    unpaired_count: int


class ExtractionResult(BaseModel):
    """Result from extracting rules and guidelines."""
    client_rules: str
    guidelines: str
    input_tokens: int
    output_tokens: int


class ExtractionResponse(BaseModel):
    """Complete extraction response with all results."""
    results: dict[str, ExtractionResult]
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
