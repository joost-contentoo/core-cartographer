"""
File cache system for storing parsed document content temporarily.
Uses file-based storage with automatic cleanup of expired entries.
"""

import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict

CACHE_DIR = Path("./temp_cache")
CACHE_EXPIRY_HOURS = 1


@dataclass
class CachedFile:
    """Represents a cached file with metadata."""
    file_id: str
    filename: str
    content: str
    tokens: int
    created_at: str


class FileCache:
    """
    Manages temporary file storage for parsed documents.

    Files are stored as JSON with a unique file_id and automatically
    cleaned up after CACHE_EXPIRY_HOURS.
    """

    def __init__(self):
        """Initialize cache directory."""
        CACHE_DIR.mkdir(exist_ok=True)

    def store(self, filename: str, content: str, tokens: int) -> str:
        """
        Store parsed content and return a unique file_id.

        Args:
            filename: Original filename
            content: Parsed text content
            tokens: Token count for cost estimation

        Returns:
            Unique file_id for later retrieval
        """
        file_id = str(uuid.uuid4())
        cached = CachedFile(
            file_id=file_id,
            filename=filename,
            content=content,
            tokens=tokens,
            created_at=datetime.utcnow().isoformat()
        )
        path = CACHE_DIR / f"{file_id}.json"
        path.write_text(json.dumps(asdict(cached)))
        return file_id

    def get(self, file_id: str) -> Optional[CachedFile]:
        """
        Retrieve cached file by ID.

        Args:
            file_id: Unique file identifier

        Returns:
            CachedFile object or None if not found
        """
        path = CACHE_DIR / f"{file_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return CachedFile(**data)

    def delete(self, file_id: str) -> bool:
        """
        Delete cached file.

        Args:
            file_id: Unique file identifier

        Returns:
            True if file was deleted, False if not found
        """
        path = CACHE_DIR / f"{file_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def cleanup_expired(self):
        """Remove files older than CACHE_EXPIRY_HOURS."""
        cutoff = datetime.utcnow() - timedelta(hours=CACHE_EXPIRY_HOURS)
        for path in CACHE_DIR.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                created = datetime.fromisoformat(data["created_at"])
                if created < cutoff:
                    path.unlink()
            except Exception:
                # Skip malformed files
                pass


# Singleton instance
file_cache = FileCache()
