# Post-Migration Task List: Streamlit to Next.js + FastAPI

**Created:** December 18, 2025
**Purpose:** Cleanup and bug fixes after migration from Streamlit to Next.js + FastAPI
**Audience:** Junior developers

---

## Table of Contents

1. [Overview](#overview)
2. [Part 1: Streamlit Artifact Removal](#part-1-streamlit-artifact-removal)
3. [Part 2: High Priority Bug Fixes](#part-2-high-priority-bug-fixes)
4. [Part 3: Medium Priority Improvements](#part-3-medium-priority-improvements)
5. [Part 4: Low Priority Enhancements](#part-4-low-priority-enhancements)
6. [Testing Checklist](#testing-checklist)

---

## Overview

The migration from Streamlit to Next.js + FastAPI is **95% complete**. The new architecture is:

- **Frontend:** Next.js 14 with React 18, Zustand state management, Tailwind CSS
- **Backend:** FastAPI with SSE streaming, file caching system
- **Core Package:** Python extraction logic (unchanged, reused by FastAPI)

This document covers:
- Removing old Streamlit code that's no longer needed
- Fixing implementation bugs discovered during review
- Improving code quality and type safety

---

## Part 1: Streamlit Artifact Removal

### Priority: HIGH
### Estimated Time: 30-45 minutes

The old Streamlit GUI code still exists in the codebase and should be removed.

---

### Task 1.1: Delete Streamlit GUI Directory

**Files to delete:**
```
src/core_cartographer/gui/
├── __init__.py
├── app.py           # Main Streamlit app (455 lines)
├── components.py    # Streamlit UI components
└── data_manager.py  # Data processing for Streamlit
```

**Command:**
```bash
rm -rf src/core_cartographer/gui/
```

**Verification:**
```bash
# Should return nothing
ls src/core_cartographer/gui/
```

---

### Task 1.2: Delete Streamlit Entry Point

**File to delete:** `src/core_cartographer/gui.py`

This file contains:
```python
"""Streamlit GUI for Core Cartographer."""
from .gui.app import main
```

**Command:**
```bash
rm src/core_cartographer/gui.py
```

---

### Task 1.3: Delete Streamlit CSS

**File to delete:** `src/core_cartographer/styles.css`

This CSS file was used by Streamlit's custom theming.

**Command:**
```bash
rm src/core_cartographer/styles.css
```

---

### Task 1.4: Delete Streamlit Launcher Script

**File to delete:** `start-gui.sh`

This script launches the old Streamlit GUI:
```bash
streamlit run src/core_cartographer/gui.py
```

**Command:**
```bash
rm start-gui.sh
```

---

### Task 1.5: Delete Build Artifacts

**Directory to delete:** `build/`

Contains compiled versions of old code including the Streamlit GUI.

**Command:**
```bash
rm -rf build/
```

---

### Task 1.6: Update pyproject.toml

**File:** `pyproject.toml`

Remove the Streamlit optional dependency and script entry point.

**Changes to make:**

1. **Remove lines 41-43** (gui optional dependency):
```toml
# DELETE THIS:
gui = [
    "streamlit>=1.30.0",
]
```

2. **Remove line 47** (gui script entry):
```toml
# DELETE THIS LINE:
cartographer-gui = "core_cartographer.gui:main"
```

**After editing, the `[project.optional-dependencies]` section should only contain:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.8.0",
    "mypy>=1.0.0",
]
```

**And `[project.scripts]` should only contain:**
```toml
[project.scripts]
cartographer = "core_cartographer.cli:main"
```

---

### Task 1.7: Verify No Streamlit References Remain

**Run this command to check for any remaining Streamlit references:**

```bash
grep -r "streamlit" --include="*.py" --include="*.toml" --include="*.txt" --include="*.sh" . \
  --exclude-dir=.venv \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude="*.md"
```

**Expected result:** No output (or only references in documentation/markdown files which are OK).

---

## Part 2: High Priority Bug Fixes

### Priority: HIGH
### Estimated Time: 2-3 hours

These bugs could cause data loss or system failures in production.

---

### Task 2.1: Fix Production Cache Directory Mismatch

**Problem:** The backend code expects cache at `./temp_cache` but the production Dockerfile creates `/tmp/cartographer_cache`. This means extraction results are lost when the container restarts.

**Files involved:**
- `backend/src/cache/file_cache.py` (line 13)
- `backend/Dockerfile.prod` (line 25)

**Current code in `file_cache.py`:**
```python
CACHE_DIR = Path("./temp_cache")
```

**Current code in `Dockerfile.prod`:**
```dockerfile
RUN mkdir -p /tmp/cartographer_cache
```

**Fix Option A (Recommended): Use environment variable for cache path**

1. **Edit `backend/src/cache/file_cache.py`:**

Replace line 13:
```python
CACHE_DIR = Path("./temp_cache")
```

With:
```python
import os
CACHE_DIR = Path(os.environ.get("CACHE_DIR", "./temp_cache"))
```

2. **Edit `backend/Dockerfile.prod`:**

Add environment variable after line 25:
```dockerfile
RUN mkdir -p /app/temp_cache
ENV CACHE_DIR=/app/temp_cache
```

Also update the chown line (around line 28-29):
```dockerfile
RUN useradd -m -u 1000 cartographer && \
    chown -R cartographer:cartographer /app
```

3. **Edit `docker-compose.prod.yml`:**

Add volume mount for cache persistence:
```yaml
backend:
  volumes:
    - cartographer-cache:/app/temp_cache
  environment:
    - CACHE_DIR=/app/temp_cache
```

---

### Task 2.2: Fix SSE Stream Exiting on First Error

**Problem:** If extraction fails for one subtype, the entire stream closes and results from completed subtypes are lost.

**File:** `backend/src/api/routes/extraction.py` (lines 125-131)

**Current code:**
```python
except Exception as e:
    error = handle_anthropic_error(e)
    error_msg = f"Failed to extract {doc_set.subtype}: {error.detail}"
    logger.error(error_msg)
    yield f"data: {json.dumps({'type': 'error', 'message': error_msg, 'subtype': doc_set.subtype})}\n\n"
    return  # <-- This exits the entire stream!
```

**Fixed code:**
```python
except Exception as e:
    error = handle_anthropic_error(e)
    error_msg = f"Failed to extract {doc_set.subtype}: {error.detail}"
    logger.error(error_msg)
    # Send error for this subtype but continue processing others
    yield f"data: {json.dumps({'type': 'subtype_error', 'message': error_msg, 'subtype': doc_set.subtype})}\n\n"
    # Don't return - continue to next subtype
    continue
```

**Also update the completion logic (after line 136):**

Replace:
```python
# Calculate totals
total_input = sum(r["input_tokens"] for r in results.values())
```

With:
```python
# Calculate totals (only from successful results)
if not results:
    yield f"data: {json.dumps({'type': 'error', 'message': 'All extractions failed'})}\n\n"
    return

total_input = sum(r["input_tokens"] for r in results.values())
```

**Frontend update required:** Update `frontend/src/lib/api.ts` to handle the new `subtype_error` event type.

Add to the SSEEvent interface (line 29):
```typescript
export interface SSEEvent {
  type: "started" | "progress" | "subtype_complete" | "subtype_error" | "complete" | "error";
  // ... rest stays the same
}
```

---

### Task 2.3: Add File Locking to Cache Operations

**Problem:** Multiple concurrent requests can cause race conditions when reading/writing cache files.

**File:** `backend/src/cache/file_cache.py`

**Add this import at the top:**
```python
import fcntl
from contextlib import contextmanager
```

**Add this helper method to the FileCache class (after line 36):**
```python
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
```

**Update the `store` method:**
```python
def store(self, filename: str, content: str, tokens: int) -> str:
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
```

**Update the `get` method:**
```python
def get(self, file_id: str) -> Optional[CachedFile]:
    path = CACHE_DIR / f"{file_id}.json"
    if not path.exists():
        return None
    with self._file_lock(path, exclusive=False):
        data = json.loads(path.read_text())
    return CachedFile(**data)
```

**Update the `delete` method:**
```python
def delete(self, file_id: str) -> bool:
    path = CACHE_DIR / f"{file_id}.json"
    if not path.exists():
        return False
    with self._file_lock(path):
        if path.exists():
            path.unlink()
            return True
    return False
```

---

## Part 3: Medium Priority Improvements

### Priority: MEDIUM
### Estimated Time: 1-2 hours

These issues affect user experience or code maintainability.

---

### Task 3.1: Fix Frontend Cost Estimation

**Problem:** Frontend shows different cost than backend calculates. Frontend hardcodes $15/1M tokens, but backend uses actual pricing per model.

**File:** `frontend/src/lib/store.ts` (lines 124-128)

**Current code:**
```typescript
estimatedCost: () => {
  const tokens = get().totalTokens();
  // Rough estimate: $15/1M input tokens for Claude Opus
  return (tokens / 1_000_000) * 15;
},
```

**Fix:** Get cost from backend API or use more accurate pricing.

**Option A: Show "estimate" label clearly (quick fix):**
```typescript
estimatedCost: () => {
  const tokens = get().totalTokens();
  const model = get().settings.model;

  // Pricing per 1M tokens (input only estimate)
  const pricing: Record<string, number> = {
    "claude-opus-4-5-20251101": 15,
    "claude-sonnet-4-20250514": 3,
    "claude-3-5-sonnet-20241022": 3,
    "claude-3-5-haiku-20241022": 0.80,
  };

  const rate = pricing[model] || 15;
  return (tokens / 1_000_000) * rate;
},
```

**Option B: Add cost endpoint to backend (better long-term):**

Create new endpoint in backend to return estimated cost based on tokens and model.

---

### Task 3.2: Fix SSE Parse Error Handling

**Problem:** Malformed SSE events are silently ignored (only logged to console).

**File:** `frontend/src/lib/api.ts` (lines 161-169)

**Current code:**
```typescript
for (const line of lines) {
  if (line.startsWith("data: ")) {
    try {
      const event = JSON.parse(line.slice(6)) as SSEEvent;
      onEvent(event);
    } catch (e) {
      console.error("Failed to parse SSE event:", line);
    }
  }
}
```

**Fixed code:**
```typescript
for (const line of lines) {
  if (line.startsWith("data: ")) {
    try {
      const event = JSON.parse(line.slice(6)) as SSEEvent;
      onEvent(event);
    } catch (e) {
      console.error("Failed to parse SSE event:", line);
      // Propagate parse error to caller
      onError(new Error(`Failed to parse server event: ${line.substring(0, 100)}`));
    }
  }
}
```

---

### Task 3.3: Improve Cache Cleanup Error Handling

**Problem:** The cleanup function silently catches ALL exceptions, making debugging difficult.

**File:** `backend/src/cache/file_cache.py` (lines 95-106)

**Current code:**
```python
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
```

**Fixed code:**
```python
def cleanup_expired(self):
    """Remove files older than CACHE_EXPIRY_HOURS."""
    import logging
    logger = logging.getLogger(__name__)

    cutoff = datetime.utcnow() - timedelta(hours=CACHE_EXPIRY_HOURS)
    cleaned = 0
    errors = 0

    for path in CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text())
            created = datetime.fromisoformat(data["created_at"])
            if created < cutoff:
                path.unlink()
                cleaned += 1
        except json.JSONDecodeError as e:
            logger.warning(f"Malformed JSON in cache file {path}: {e}")
            # Delete malformed files
            path.unlink()
            errors += 1
        except KeyError as e:
            logger.warning(f"Missing field in cache file {path}: {e}")
            path.unlink()
            errors += 1
        except Exception as e:
            logger.error(f"Unexpected error cleaning {path}: {e}")
            errors += 1

    if cleaned > 0 or errors > 0:
        logger.info(f"Cache cleanup: removed {cleaned} expired, {errors} malformed")
```

---

### Task 3.4: Set NEXT_PUBLIC_API_URL in Production

**Problem:** Production frontend defaults to `localhost:8000` if env var not set.

**File:** `frontend/Dockerfile.prod`

**Add build argument and environment variable:**

After line 15 (before `RUN npm run build`), add:
```dockerfile
# Build-time argument for API URL
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
```

**Update `docker-compose.prod.yml` to pass the argument:**
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile.prod
    args:
      - NEXT_PUBLIC_API_URL=http://api.yourdomain.com
```

---

## Part 4: Low Priority Enhancements

### Priority: LOW
### Estimated Time: 1 hour

These are code quality improvements that don't affect functionality.

---

### Task 4.1: Use Discriminated Union Types for SSE Events

**Problem:** TypeScript can't verify correct fields per event type.

**File:** `frontend/src/lib/types.ts` (or add to `api.ts`)

**Replace the SSEEvent interface with discriminated unions:**

```typescript
// Base event properties
interface SSEEventBase {
  type: string;
}

// Specific event types
interface SSEStartedEvent extends SSEEventBase {
  type: "started";
  subtypes: string[];
}

interface SSEProgressEvent extends SSEEventBase {
  type: "progress";
  subtype: string;
  current: number;
  total: number;
}

interface SSESubtypeCompleteEvent extends SSEEventBase {
  type: "subtype_complete";
  subtype: string;
  current: number;
  total: number;
}

interface SSESubtypeErrorEvent extends SSEEventBase {
  type: "subtype_error";
  subtype: string;
  message: string;
}

interface SSECompleteEvent extends SSEEventBase {
  type: "complete";
  results: Record<string, {
    client_rules: string;
    guidelines: string;
    input_tokens: number;
    output_tokens: number;
  }>;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost: number;
}

interface SSEErrorEvent extends SSEEventBase {
  type: "error";
  message: string;
}

// Union type
export type SSEEvent =
  | SSEStartedEvent
  | SSEProgressEvent
  | SSESubtypeCompleteEvent
  | SSESubtypeErrorEvent
  | SSECompleteEvent
  | SSEErrorEvent;
```

---

### Task 4.2: Fix Misleading CORS Comment

**File:** `backend/src/api/main.py` (around lines 52-54)

**Current code:**
```python
allow_origins=[
    "http://localhost:3000",      # Browser accessing frontend
    "http://frontend:3000",       # Container-to-container (if needed)
],
```

**Fixed comment:**
```python
allow_origins=[
    "http://localhost:3000",      # Development: Browser requests
    "http://frontend:3000",       # Docker: Container hostname (not typically needed)
],
```

---

### Task 4.3: Add Response Model to Extraction Endpoint

**File:** `backend/src/api/routes/extraction.py` (line 25)

The endpoint doesn't document its response schema. While SSE doesn't have a traditional response model, we can add documentation.

**Add docstring improvement:**
```python
@router.post("/extract-stream")
async def extract_with_streaming(request: ExtractionRequest):
    """
    Extract rules and guidelines with SSE progress streaming.

    This endpoint returns a Server-Sent Events stream with the following event types:

    - `started`: Extraction begun. Fields: `subtypes` (list of subtypes to process)
    - `progress`: Processing update. Fields: `subtype`, `current`, `total`
    - `subtype_complete`: One subtype finished. Fields: `subtype`, `current`, `total`
    - `subtype_error`: One subtype failed. Fields: `subtype`, `message`
    - `complete`: All done. Fields: `results`, `total_input_tokens`, `total_output_tokens`, `total_cost`
    - `error`: Fatal error. Fields: `message`

    Args:
        request: Extraction configuration with document sets

    Returns:
        StreamingResponse with Server-Sent Events (text/event-stream)
    """
```

---

## Testing Checklist

After completing all tasks, verify the following:

### Cleanup Verification

- [ ] `src/core_cartographer/gui/` directory does not exist
- [ ] `src/core_cartographer/gui.py` does not exist
- [ ] `src/core_cartographer/styles.css` does not exist
- [ ] `start-gui.sh` does not exist
- [ ] `build/` directory does not exist
- [ ] `pyproject.toml` has no `streamlit` references
- [ ] `grep -r "streamlit" .` returns no Python/config file matches

### Backend Testing

```bash
# Start backend
cd backend
pip install -r requirements.txt
uvicorn src.api.main:app --reload

# Test health endpoint
curl http://localhost:8000/health

# Test file upload
curl -X POST http://localhost:8000/api/v1/files/parse \
  -F "file=@test.pdf"

# Check cache locking works (run multiple uploads simultaneously)
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/v1/files/parse \
    -F "file=@test.pdf" &
done
wait
```

### Frontend Testing

```bash
# Start frontend
cd frontend
npm install
npm run dev

# Open http://localhost:3000
# Test:
# 1. File upload works
# 2. Auto-detect works
# 3. Extraction shows progress
# 4. Extraction error for one subtype doesn't lose other results
# 5. Cost estimation shows reasonable values
```

### Docker Testing

```bash
# Build and run
docker-compose up --build

# Verify both services healthy
docker-compose ps

# Test extraction works through Docker
# Open http://localhost:3000 and run full workflow
```

---

## Summary

| Section | Tasks | Priority | Time |
|---------|-------|----------|------|
| Part 1: Streamlit Removal | 7 tasks | HIGH | 30-45 min |
| Part 2: Bug Fixes | 3 tasks | HIGH | 2-3 hours |
| Part 3: Improvements | 4 tasks | MEDIUM | 1-2 hours |
| Part 4: Enhancements | 3 tasks | LOW | 1 hour |

**Total estimated time:** 5-7 hours

**Recommended order:**
1. Complete Part 1 first (cleanup)
2. Complete Part 2 (critical bugs)
3. Test thoroughly
4. Complete Part 3 and 4 as time permits
