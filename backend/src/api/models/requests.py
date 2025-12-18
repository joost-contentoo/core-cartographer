"""Request models for API endpoints."""


from pydantic import BaseModel


class FileReference(BaseModel):
    """Reference to a cached file with language and pairing info."""
    file_id: str
    language: str
    pair_id: str | None = None


class DocumentSetRequest(BaseModel):
    """Group of files for a specific subtype."""
    subtype: str
    files: list[FileReference]


class ExtractionRequest(BaseModel):
    """Request to extract rules and guidelines from document sets."""
    client_name: str
    document_sets: list[DocumentSetRequest]
    batch_processing: bool = True
    debug_mode: bool = False


class AnalysisFileRef(BaseModel):
    """File reference for analysis operations."""
    file_id: str


class AnalysisRequest(BaseModel):
    """Request to analyze files for language detection and pairing."""
    files: list[AnalysisFileRef]
