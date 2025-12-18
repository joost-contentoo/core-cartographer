"""Request models for API endpoints."""

from pydantic import BaseModel
from typing import List, Optional


class FileReference(BaseModel):
    """Reference to a cached file with language and pairing info."""
    file_id: str
    language: str
    pair_id: Optional[str] = None


class DocumentSetRequest(BaseModel):
    """Group of files for a specific subtype."""
    subtype: str
    files: List[FileReference]


class ExtractionRequest(BaseModel):
    """Request to extract rules and guidelines from document sets."""
    client_name: str
    document_sets: List[DocumentSetRequest]
    batch_processing: bool = True
    debug_mode: bool = False


class AnalysisFileRef(BaseModel):
    """File reference for analysis operations."""
    file_id: str


class AnalysisRequest(BaseModel):
    """Request to analyze files for language detection and pairing."""
    files: List[AnalysisFileRef]
