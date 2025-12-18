"""
File cache system for storing parsed document content temporarily.
Uses file-based storage with automatic cleanup of expired entries.
"""

import os
import uuid
import json
import fcntl
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager

logger = logging.getLogger(__name__)

CACHE_DIR = Path(os.environ.get("CACHE_DIR", "./temp_cache"))
CACHE_EXPIRY_HOURS = int(os.environ.get("CACHE_EXPIRY_HOURS", "1"))


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

    @contextmanager
    def _file_lock(self, path: Path, exclusive: bool = True):
        """Context manager for file locking."""
        lock_path = path.with_suffix('.lock')
        lock_file = open(lock_path, 'w')
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            # Clean up lock file
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass

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
        with self._file_lock(path):
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
        with self._file_lock(path, exclusive=False):
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
        if not path.exists():
            return False
        with self._file_lock(path):
            if path.exists():
                path.unlink()
                return True
        return False

    def cleanup_expired(self):
        """Remove files older than CACHE_EXPIRY_HOURS."""
        cutoff = datetime.utcnow() - timedelta(hours=CACHE_EXPIRY_HOURS)
        cleaned = 0
        errors = 0
        skipped = 0

        for path in CACHE_DIR.glob("*.json"):
            # Skip lock files
            if path.suffix == '.lock':
                continue

            lock_path = path.with_suffix('.lock')
            lock_file = None

            try:
                # Try non-blocking lock to avoid waiting on files in use
                lock_file = open(lock_path, 'w')
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

                # Check if file still exists after acquiring lock
                if not path.exists():
                    continue

                data = json.loads(path.read_text())
                created = datetime.fromisoformat(data["created_at"])
                if created < cutoff:
                    path.unlink()
                    cleaned += 1

            except BlockingIOError:
                # File is in use, skip it
                skipped += 1
            except json.JSONDecodeError as e:
                logger.warning(f"Malformed JSON in cache file {path}: {e}")
                # Delete malformed files
                try:
                    path.unlink()
                    errors += 1
                except FileNotFoundError:
                    pass
            except KeyError as e:
                logger.warning(f"Missing field in cache file {path}: {e}")
                try:
                    path.unlink()
                    errors += 1
                except FileNotFoundError:
                    pass
            except FileNotFoundError:
                # File was deleted between glob and processing
                pass
            except Exception as e:
                logger.error(f"Unexpected error cleaning {path}: {e}")
                errors += 1
            finally:
                if lock_file:
                    try:
                        fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                        lock_file.close()
                        lock_path.unlink()
                    except (OSError, FileNotFoundError):
                        pass

        if cleaned > 0 or errors > 0 or skipped > 0:
            logger.info(f"Cache cleanup: removed {cleaned} expired, {errors} malformed, {skipped} skipped (in use)")


# Singleton instance
file_cache = FileCache()
