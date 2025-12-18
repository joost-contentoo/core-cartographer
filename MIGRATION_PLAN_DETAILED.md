# Core Cartographer: Streamlit → Next.js + FastAPI Migration Plan

**Version:** 2.0
**Date:** December 2025
**Status:** Ready for Implementation

---

## Overview

Migrate from Streamlit GUI to modern Next.js frontend with FastAPI backend, addressing UX pain points and leveraging portal-localiser design system.

### Key Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State Persistence | **Stateless** (refresh = reset) | Simplest MVP, no backend storage needed |
| File Content Storage | **Backend cache** with file_id | Efficient, Supabase-ready for future |
| Extraction Progress | **SSE streaming** (mandatory) | Reliable for long operations |
| Timeline | **6 weeks** moderate | Buffer for unknowns |
| Settings UI | **Settings panel** | Clean, discoverable |

---

## Key Improvements Over Streamlit

1. **Eliminate data duplication** - Single workspace view (no 3-step wizard with repeated tables)
2. **Better file management** - Inline deletion, reliable dropdowns, drag-and-drop everywhere
3. **Natural button UX** - Clear visual hierarchy, proper feedback, smooth interactions
4. **Efficient data flow** - Backend caches file content, frontend only holds metadata
5. **Reliable extraction** - SSE streaming with per-file progress, cancellable
6. **Live cost estimation** - Always visible, updates in real-time

---

## Architecture

### High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │ File Upload │───→│  Zustand    │───→│    UI       │            │
│  │  Component  │    │   Store     │    │ Components  │            │
│  └─────────────┘    │ (metadata   │    └─────────────┘            │
│                      │  only, no   │                               │
│                      │  content)   │                               │
│                      └──────┬──────┘                               │
└─────────────────────────────┼───────────────────────────────────────┘
                              │ HTTP (file_ids, not content)
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │   Routes    │───→│ File Cache  │───→│   Python    │            │
│  │ /files      │    │ (temp dir)  │    │   Core      │            │
│  │ /analysis   │    │ file_id →   │    │ extractor   │            │
│  │ /extraction │    │ content     │    │ parser etc  │            │
│  └─────────────┘    └─────────────┘    └─────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Architecture Points

1. **Frontend stores metadata only** - File names, languages, subtypes, token counts, file_ids
2. **Backend caches content** - Parsed text stored in temp directory, keyed by file_id
3. **Extraction uses file_ids** - No large payloads over the wire
4. **SSE for progress** - Real-time updates, per-subtype status, cancellable
5. **Stateless sessions** - Refresh clears frontend state, backend cache expires after 1 hour

---

## 1. PROJECT STRUCTURE

```
core-cartographer/
├── backend/                        # NEW: FastAPI wrapper
│   ├── src/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py            # FastAPI app, CORS, lifespan
│   │   │   ├── dependencies.py    # Shared deps (settings, cache)
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── files.py       # Upload, parse, delete
│   │   │   │   ├── analysis.py    # Language detection, pairing
│   │   │   │   └── extraction.py  # SSE extraction endpoint
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── requests.py    # Pydantic request models
│   │   │       └── responses.py   # Pydantic response models
│   │   └── cache/
│   │       └── file_cache.py      # Temp file storage manager
│   ├── tests/
│   │   ├── test_files.py
│   │   ├── test_analysis.py
│   │   └── test_extraction.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                       # NEW: Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout with Inter font
│   │   │   ├── page.tsx           # Redirect to /workspace
│   │   │   └── workspace/
│   │   │       └── page.tsx       # Main workspace (single route)
│   │   ├── components/
│   │   │   ├── ui/                # Portal-localiser components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   └── progress.tsx
│   │   │   ├── project/
│   │   │   │   ├── FileUploadZone.tsx
│   │   │   │   ├── FileList.tsx
│   │   │   │   ├── FileItem.tsx
│   │   │   │   ├── SubtypeManager.tsx
│   │   │   │   ├── CostDisplay.tsx
│   │   │   │   ├── SettingsPanel.tsx
│   │   │   │   └── ExtractionProgress.tsx
│   │   │   ├── results/
│   │   │   │   ├── ResultsDialog.tsx
│   │   │   │   ├── CodeViewer.tsx
│   │   │   │   └── MarkdownViewer.tsx
│   │   │   └── errors/
│   │   │       ├── ErrorBoundary.tsx
│   │   │       └── ErrorToast.tsx
│   │   ├── lib/
│   │   │   ├── api.ts             # API client with error handling
│   │   │   ├── store.ts           # Zustand store (metadata only)
│   │   │   ├── types.ts           # TypeScript types (generated)
│   │   │   └── utils.ts
│   │   └── styles/
│   │       └── globals.css        # Portal-localiser theme
│   ├── scripts/
│   │   └── generate-types.ts      # Pydantic → TypeScript generator
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
│
├── docker-compose.yml              # Development orchestration
├── docker-compose.prod.yml         # Production (optional)
├── .env.example                    # Environment template
└── src/core_cartographer/          # EXISTING (minimal changes)
    ├── extractor.py               # ✓ Reuse as-is
    ├── parser.py                  # ✓ Reuse as-is
    ├── models.py                  # ✓ Reuse as-is
    ├── file_utils.py              # ✓ Reuse as-is
    ├── cost_estimator.py          # ✓ Reuse as-is
    └── config.py                  # ⚠ Add API settings
```

---

## 2. UX REDESIGN

### Main Workspace Layout (Single Page at `/workspace`)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Header                                                              │
│ ┌────────────────────┐  ┌──────────┐  ┌───────────────────────────┐│
│ │ Client Name        │  │ Settings │  │ Est. Cost: $0.25 (live)   ││
│ │ [________________] │  │    ⚙️    │  │ 15,234 tokens             ││
│ └────────────────────┘  └──────────┘  └───────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Left Panel (65%)                    │ Right Panel (35%)            │
│                                     │                              │
│ ┌─────────────────────────────────┐ │ ┌───────────────────────┐   │
│ │   📤 Drag & Drop Upload Zone    │ │ │   Actions             │   │
│ │   Drop files here or browse     │ │ │                       │   │
│ │   PDF, DOCX, TXT, MD (max 10MB) │ │ │ [🔍 Auto-Detect]      │   │
│ └─────────────────────────────────┘ │ │ [🧹 Clear Labels]     │   │
│                                     │ │                       │   │
│ Categories:                         │ │ ┌───────────────────┐ │   │
│ [general] [contracts] [+ Add]       │ │ │ ✨ Start          │ │   │
│                                     │ │ │    Extraction     │ │   │
│ ┌─────────────────────────────────┐ │ │ └───────────────────┘ │   │
│ │ Files (3)                    🗑️│ │ │  (primary button)     │   │
│ ├─────────────────────────────────┤ │ └───────────────────────┘   │
│ │ 📄 style_guide_EN.pdf          │ │                              │
│ │    EN │ [general    ▼] │ #1  ✕ │ │ ┌───────────────────────┐   │
│ ├─────────────────────────────────┤ │ │   Preview             │   │
│ │ 📄 style_guide_DE.pdf          │ │ │                       │   │
│ │    DE │ [general    ▼] │ #1  ✕ │ │ │   (selected file      │   │
│ ├─────────────────────────────────┤ │ │    first 500 chars)   │   │
│ │ 📄 legal_terms.docx            │ │ │                       │   │
│ │    EN │ [contracts  ▼] │  -  ✕ │ │ │                       │   │
│ └─────────────────────────────────┘ │ └───────────────────────┘   │
│                                     │                              │
└─────────────────────────────────────┴──────────────────────────────┘
```

### Settings Panel (Modal)

```
┌─────────────────────────────────────────┐
│ Settings                            ✕   │
├─────────────────────────────────────────┤
│                                         │
│ Processing Mode                         │
│ ○ Individual (one API call per subtype) │
│ ● Batch (single API call, recommended)  │
│                                         │
│ Model                                   │
│ [claude-opus-4-5-20251101          ▼]   │
│                                         │
│ Debug Mode                              │
│ [ ] Save prompts to disk (no API call)  │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │           [Save Settings]           │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Extraction Progress (Modal with SSE updates)

```
┌─────────────────────────────────────────┐
│ Extracting Rules & Guidelines       ✕   │
├─────────────────────────────────────────┤
│                                         │
│ Overall Progress                        │
│ ████████████░░░░░░░░░░░░░░  45%        │
│                                         │
│ Status:                                 │
│ ✅ general (completed)                  │
│ ⏳ contracts (processing...)            │
│ ○ marketing (pending)                   │
│                                         │
│ Time elapsed: 12s                       │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │            [Cancel]                 │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Error States

**API Error Toast:**
```
┌─────────────────────────────────────────┐
│ ❌ Extraction Failed                    │
│                                         │
│ Rate limit exceeded. Please wait 60s    │
│ and try again.                          │
│                                         │
│ [Retry] [Dismiss]                       │
└─────────────────────────────────────────┘
```

**File Parse Error (inline):**
```
│ 📄 corrupted.pdf                        │
│    ❌ Failed to parse: Invalid PDF      │
│    [Remove] [Retry]                     │
```

---

## 3. FASTAPI BACKEND

### File Cache System

```python
# backend/src/cache/file_cache.py
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
    file_id: str
    filename: str
    content: str
    tokens: int
    created_at: str

class FileCache:
    def __init__(self):
        CACHE_DIR.mkdir(exist_ok=True)

    def store(self, filename: str, content: str, tokens: int) -> str:
        """Store parsed content, return file_id."""
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
        """Retrieve cached file by ID."""
        path = CACHE_DIR / f"{file_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return CachedFile(**data)

    def delete(self, file_id: str) -> bool:
        """Delete cached file."""
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
                pass  # Skip malformed files

# Singleton instance
file_cache = FileCache()
```

### API Endpoints

```python
# backend/src/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .routes import files, analysis, extraction
from ..cache.file_cache import file_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: clean expired cache
    file_cache.cleanup_expired()

    # Background task to clean cache every 30 minutes
    async def cleanup_task():
        while True:
            await asyncio.sleep(1800)  # 30 minutes
            file_cache.cleanup_expired()

    task = asyncio.create_task(cleanup_task())
    yield
    task.cancel()

app = FastAPI(
    title="Core Cartographer API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Note: Different URLs for browser vs container
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Browser accessing frontend
        "http://frontend:3000",       # Container-to-container (if needed)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(extraction.router, prefix="/api/v1/extraction", tags=["extraction"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

```python
# backend/src/api/routes/files.py
from fastapi import APIRouter, UploadFile, HTTPException
from typing import List
import tempfile
from pathlib import Path

from core_cartographer.parser import parse_document
from core_cartographer.cost_estimator import count_tokens
from ...cache.file_cache import file_cache
from ..models.responses import FileParseResponse, FileMetadata

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/parse", response_model=FileParseResponse)
async def parse_file(file: UploadFile):
    """Upload and parse a single file. Returns file_id for later use."""
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # Validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)")

    # Save to temp file for parsing
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        # Parse using existing logic
        text_content = parse_document(tmp_path)
        tokens = count_tokens(text_content)

        # Store in cache
        file_id = file_cache.store(file.filename, text_content, tokens)

        # Return metadata + preview (first 500 chars)
        return FileParseResponse(
            file_id=file_id,
            filename=file.filename,
            tokens=tokens,
            preview=text_content[:500] + ("..." if len(text_content) > 500 else ""),
            success=True
        )
    except Exception as e:
        raise HTTPException(400, f"Failed to parse file: {str(e)}")
    finally:
        tmp_path.unlink()  # Cleanup temp file

@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete a cached file."""
    if file_cache.delete(file_id):
        return {"success": True}
    raise HTTPException(404, "File not found")

@router.post("/parse-batch", response_model=List[FileParseResponse])
async def parse_files(files: List[UploadFile]):
    """Parse multiple files. Returns list of results (some may have errors)."""
    results = []
    for file in files:
        try:
            result = await parse_file(file)
            results.append(result)
        except HTTPException as e:
            results.append(FileParseResponse(
                file_id="",
                filename=file.filename,
                tokens=0,
                preview="",
                success=False,
                error=e.detail
            ))
    return results
```

```python
# backend/src/api/routes/extraction.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
import json
import asyncio

from core_cartographer.extractor import extract_rules_and_guidelines
from core_cartographer.models import Document, DocumentSet
from core_cartographer.config import get_settings
from core_cartographer.cost_estimator import estimate_cost
from ...cache.file_cache import file_cache
from ..models.requests import ExtractionRequest

router = APIRouter()

@router.post("/extract-stream")
async def extract_with_streaming(request: ExtractionRequest):
    """
    Extract rules and guidelines with SSE progress streaming.

    Event types:
    - started: Extraction begun
    - progress: Per-subtype progress update
    - subtype_complete: One subtype finished
    - complete: All done, includes results
    - error: Something went wrong
    """
    async def event_stream():
        settings = get_settings()
        settings.debug_mode = request.debug_mode
        settings.batch_processing = request.batch_processing

        # Build document sets from file_ids
        document_sets = []
        for ds_req in request.document_sets:
            documents = []
            for file_ref in ds_req.files:
                cached = file_cache.get(file_ref.file_id)
                if not cached:
                    yield f"data: {json.dumps({'type': 'error', 'message': f'File not found: {file_ref.file_id}'})}\n\n"
                    return

                documents.append(Document(
                    filename=cached.filename,
                    content=cached.content,
                    language=file_ref.language,
                    pair_id=file_ref.pair_id,
                    tokens=cached.tokens
                ))

            document_sets.append(DocumentSet(
                client_name=request.client_name,
                subtype=ds_req.subtype,
                documents=documents,
                total_tokens=sum(d.tokens for d in documents)
            ))

        # Send started event
        yield f"data: {json.dumps({'type': 'started', 'subtypes': [ds.subtype for ds in document_sets]})}\n\n"

        results = {}
        total = len(document_sets)

        try:
            for i, doc_set in enumerate(document_sets):
                # Send progress event
                yield f"data: {json.dumps({'type': 'progress', 'subtype': doc_set.subtype, 'current': i, 'total': total})}\n\n"

                # Run extraction (this blocks, but we're in async context)
                # In production, consider running in thread pool
                result = await asyncio.to_thread(
                    extract_rules_and_guidelines, settings, doc_set
                )

                results[doc_set.subtype] = {
                    "client_rules": result.client_rules,
                    "guidelines": result.guidelines,
                    "input_tokens": result.input_tokens,
                    "output_tokens": result.output_tokens
                }

                # Send subtype complete event
                yield f"data: {json.dumps({'type': 'subtype_complete', 'subtype': doc_set.subtype, 'current': i + 1, 'total': total})}\n\n"

            # Calculate totals
            total_input = sum(r["input_tokens"] for r in results.values())
            total_output = sum(r["output_tokens"] for r in results.values())
            total_cost = estimate_cost(total_input, total_output, settings.model)

            # Send complete event with all results
            yield f"data: {json.dumps({'type': 'complete', 'results': results, 'total_input_tokens': total_input, 'total_output_tokens': total_output, 'total_cost': total_cost})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

```python
# backend/src/api/routes/analysis.py
from fastapi import APIRouter
from typing import List

from core_cartographer.file_utils import detect_language, find_translation_pair
from ...cache.file_cache import file_cache
from ..models.requests import AnalysisRequest
from ..models.responses import AnalysisResponse

router = APIRouter()

@router.post("/auto-detect", response_model=AnalysisResponse)
async def run_auto_detect(request: AnalysisRequest):
    """Run language detection and pairing on cached files."""
    results = []

    # First pass: detect languages
    for file_ref in request.files:
        cached = file_cache.get(file_ref.file_id)
        if cached:
            # Detect language from content
            detected_lang = detect_language(cached.content[:1000])  # First 1000 chars
            results.append({
                "file_id": file_ref.file_id,
                "filename": cached.filename,
                "language": detected_lang,
                "pair_id": None
            })

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

    paired_count = len([r for r in results if r["pair_id"]])
    unpaired_count = len(results) - paired_count

    return AnalysisResponse(
        files=results,
        paired_count=paired_count // 2,  # Number of pairs, not paired files
        unpaired_count=unpaired_count
    )
```

### Pydantic Models

```python
# backend/src/api/models/requests.py
from pydantic import BaseModel
from typing import List, Optional

class FileReference(BaseModel):
    file_id: str
    language: str
    pair_id: Optional[str] = None

class DocumentSetRequest(BaseModel):
    subtype: str
    files: List[FileReference]

class ExtractionRequest(BaseModel):
    client_name: str
    document_sets: List[DocumentSetRequest]
    batch_processing: bool = True
    debug_mode: bool = False

class AnalysisFileRef(BaseModel):
    file_id: str

class AnalysisRequest(BaseModel):
    files: List[AnalysisFileRef]
```

```python
# backend/src/api/models/responses.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class FileParseResponse(BaseModel):
    file_id: str
    filename: str
    tokens: int
    preview: str
    success: bool
    error: Optional[str] = None

class FileMetadata(BaseModel):
    file_id: str
    filename: str
    language: str
    pair_id: Optional[str]

class AnalysisResponse(BaseModel):
    files: List[Dict[str, Any]]
    paired_count: int
    unpaired_count: int

class ExtractionResult(BaseModel):
    client_rules: str
    guidelines: str
    input_tokens: int
    output_tokens: int

class ExtractionResponse(BaseModel):
    results: Dict[str, ExtractionResult]
    total_input_tokens: int
    total_output_tokens: int
    total_cost: float
```

---

## 4. NEXT.JS FRONTEND

### Zustand Store (Metadata Only)

```typescript
// frontend/src/lib/store.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types
export interface FileMetadata {
  fileId: string;
  filename: string;
  language: string;
  subtype: string;
  pairId: string | null;
  tokens: number;
  preview: string;
  status: 'uploading' | 'ready' | 'error';
  error?: string;
}

export interface ExtractionResult {
  clientRules: string;
  guidelines: string;
  inputTokens: number;
  outputTokens: number;
}

export interface ExtractionProgress {
  status: 'idle' | 'running' | 'complete' | 'error';
  currentSubtype: string | null;
  completedSubtypes: string[];
  totalSubtypes: number;
  error?: string;
}

export interface Settings {
  batchProcessing: boolean;
  debugMode: boolean;
  model: string;
}

interface ProjectStore {
  // State
  clientName: string;
  files: FileMetadata[];
  subtypes: string[];
  selectedFileId: string | null;
  settings: Settings;
  extraction: ExtractionProgress;
  results: Record<string, ExtractionResult> | null;

  // File actions
  setClientName: (name: string) => void;
  addFile: (file: FileMetadata) => void;
  updateFile: (fileId: string, updates: Partial<FileMetadata>) => void;
  removeFile: (fileId: string) => void;
  setSelectedFile: (fileId: string | null) => void;
  clearAllFiles: () => void;

  // Subtype actions
  addSubtype: (subtype: string) => void;
  removeSubtype: (subtype: string) => void;

  // Settings actions
  updateSettings: (settings: Partial<Settings>) => void;

  // Extraction actions
  setExtractionProgress: (progress: Partial<ExtractionProgress>) => void;
  setResults: (results: Record<string, ExtractionResult>) => void;
  clearResults: () => void;

  // Computed
  totalTokens: () => number;
  estimatedCost: () => number;
}

export const useProjectStore = create<ProjectStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      clientName: '',
      files: [],
      subtypes: ['general'],
      selectedFileId: null,
      settings: {
        batchProcessing: true,
        debugMode: false,
        model: 'claude-opus-4-5-20251101'
      },
      extraction: {
        status: 'idle',
        currentSubtype: null,
        completedSubtypes: [],
        totalSubtypes: 0
      },
      results: null,

      // File actions
      setClientName: (name) => set({ clientName: name }),

      addFile: (file) => set((state) => ({
        files: [...state.files, file]
      })),

      updateFile: (fileId, updates) => set((state) => ({
        files: state.files.map(f =>
          f.fileId === fileId ? { ...f, ...updates } : f
        )
      })),

      removeFile: (fileId) => set((state) => ({
        files: state.files.filter(f => f.fileId !== fileId),
        selectedFileId: state.selectedFileId === fileId ? null : state.selectedFileId
      })),

      setSelectedFile: (fileId) => set({ selectedFileId: fileId }),

      clearAllFiles: () => set({ files: [], selectedFileId: null }),

      // Subtype actions
      addSubtype: (subtype) => set((state) => ({
        subtypes: state.subtypes.includes(subtype)
          ? state.subtypes
          : [...state.subtypes, subtype]
      })),

      removeSubtype: (subtype) => set((state) => ({
        subtypes: state.subtypes.filter(s => s !== subtype),
        files: state.files.map(f =>
          f.subtype === subtype ? { ...f, subtype: 'general' } : f
        )
      })),

      // Settings actions
      updateSettings: (settings) => set((state) => ({
        settings: { ...state.settings, ...settings }
      })),

      // Extraction actions
      setExtractionProgress: (progress) => set((state) => ({
        extraction: { ...state.extraction, ...progress }
      })),

      setResults: (results) => set({ results }),

      clearResults: () => set({ results: null }),

      // Computed (as functions since Zustand doesn't have computed)
      totalTokens: () => get().files.reduce((sum, f) => sum + f.tokens, 0),

      estimatedCost: () => {
        const tokens = get().totalTokens();
        // Rough estimate: $15/1M input tokens for Claude Opus
        return (tokens / 1_000_000) * 15;
      }
    }),
    { name: 'project-store' }
  )
);
```

### API Client with SSE Support

```typescript
// frontend/src/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ParseResult {
  fileId: string;
  filename: string;
  tokens: number;
  preview: string;
  success: boolean;
  error?: string;
}

export interface AnalysisResult {
  files: Array<{
    file_id: string;
    filename: string;
    language: string;
    pair_id: string | null;
  }>;
  paired_count: number;
  unpaired_count: number;
}

export interface SSEEvent {
  type: 'started' | 'progress' | 'subtype_complete' | 'complete' | 'error';
  subtype?: string;
  current?: number;
  total?: number;
  results?: Record<string, {
    client_rules: string;
    guidelines: string;
    input_tokens: number;
    output_tokens: number;
  }>;
  message?: string;
  total_cost?: number;
}

class APIClient {
  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async parseFile(file: File): Promise<ParseResult> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/api/v1/files/parse`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  async deleteFile(fileId: string): Promise<void> {
    await this.fetch(`/api/v1/files/${fileId}`, { method: 'DELETE' });
  }

  async runAutoDetect(fileIds: string[]): Promise<AnalysisResult> {
    return this.fetch('/api/v1/analysis/auto-detect', {
      method: 'POST',
      body: JSON.stringify({
        files: fileIds.map(file_id => ({ file_id }))
      }),
    });
  }

  extractWithSSE(
    request: {
      clientName: string;
      documentSets: Array<{
        subtype: string;
        files: Array<{
          fileId: string;
          language: string;
          pairId: string | null;
        }>;
      }>;
      batchProcessing: boolean;
      debugMode: boolean;
    },
    onEvent: (event: SSEEvent) => void,
    onError: (error: Error) => void
  ): () => void {
    const controller = new AbortController();

    fetch(`${API_BASE}/api/v1/extraction/extract-stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        client_name: request.clientName,
        document_sets: request.documentSets.map(ds => ({
          subtype: ds.subtype,
          files: ds.files.map(f => ({
            file_id: f.fileId,
            language: f.language,
            pair_id: f.pairId
          }))
        })),
        batch_processing: request.batchProcessing,
        debug_mode: request.debugMode
      }),
      signal: controller.signal
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No response body');

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const event = JSON.parse(line.slice(6)) as SSEEvent;
                onEvent(event);
              } catch (e) {
                console.error('Failed to parse SSE event:', line);
              }
            }
          }
        }
      })
      .catch((error) => {
        if (error.name !== 'AbortError') {
          onError(error);
        }
      });

    // Return cancel function
    return () => controller.abort();
  }
}

export const api = new APIClient();
```

### Type Generation Script

```typescript
// frontend/scripts/generate-types.ts
/**
 * Generate TypeScript types from backend Pydantic models.
 * Run: npx ts-node scripts/generate-types.ts
 *
 * Requires: pip install datamodel-code-generator
 * Then: datamodel-codegen --input ../backend/src/api/models --output src/lib/types.ts
 *
 * Or manually keep types.ts in sync with backend models.
 */

// For now, manually maintain types in store.ts and api.ts
// Add automated generation as a pre-commit hook later
```

### Portal-Localiser Theme

```css
/* frontend/src/styles/globals.css */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* Primary - Forest Green */
  --primary-50: #f2fdf7;
  --primary-100: #e1fceb;
  --primary-200: #d7ffc2;
  --primary-300: #86efac;
  --primary-400: #11cc5b;
  --primary-500: #049946;
  --primary-600: #037d39;
  --primary-700: #00543e;
  --primary-800: #064e3b;
  --primary-900: #022c22;

  --primary: var(--primary-700);
  --primary-foreground: #ffffff;

  /* Accent */
  --destructive: #ff4e00;
  --destructive-foreground: #ffffff;

  /* Neutrals */
  --background: #ffffff;
  --foreground: #0f172a;
  --muted: #f1f5f9;
  --muted-foreground: #64748b;
  --border: #e2e8f0;
  --card: #ffffff;
  --card-foreground: #0f172a;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #020617;
    --foreground: #f8fafc;
    --muted: #1e293b;
    --muted-foreground: #94a3b8;
    --border: #1e293b;
    --card: #0f172a;
    --card-foreground: #f8fafc;
    --primary: var(--primary-500);
  }
}

body {
  font-family: 'Inter', sans-serif;
  background: var(--background);
  color: var(--foreground);
  -webkit-font-smoothing: antialiased;
}

/* Component base styles */
.btn {
  @apply inline-flex items-center justify-center rounded-xl font-medium
         transition-all duration-200 focus:outline-none focus:ring-2
         focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed
         active:scale-[0.98];
}

.btn-primary {
  @apply bg-primary text-primary-foreground shadow-lg
         hover:bg-primary-500 hover:shadow-xl focus:ring-primary;
}

.btn-secondary {
  @apply bg-white text-neutral-900 border border-neutral-200 shadow-sm
         hover:bg-neutral-50 focus:ring-neutral-200;
}

.btn-ghost {
  @apply bg-transparent text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900;
}

.btn-destructive {
  @apply bg-destructive text-white shadow-sm hover:opacity-90 focus:ring-destructive;
}

.card {
  @apply rounded-[24px] bg-card border border-border shadow-lg overflow-hidden;
}

.card-glass {
  @apply rounded-[24px] bg-white/95 dark:bg-neutral-900/60 backdrop-blur-xl
         border-2 border-neutral-300/60 shadow-xl;
}
```

---

## 5. DOCKER SETUP

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cartographer-api
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - API_HOST=0.0.0.0
      - API_PORT=8000
    volumes:
      # Source code (hot reload)
      - ./backend/src:/app/src
      # Existing Python package
      - ./src/core_cartographer:/app/core_cartographer
      # Templates and instructions
      - ./templates:/app/templates
      - ./instructions:/app/instructions
      # Temp cache (persists across restarts)
      - cartographer-cache:/app/temp_cache
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - cartographer-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: cartographer-ui
    ports:
      - "3000:3000"
    environment:
      # Browser makes requests to localhost, not container hostname
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    command: npm run dev
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - cartographer-network

volumes:
  cartographer-cache:
    driver: local

networks:
  cartographer-network:
    driver: bridge
```

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create cache directory
RUN mkdir -p /app/temp_cache

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

---

## 6. MIGRATION STRATEGY (6 Weeks)

### Week 1: Walking Skeleton
**Goal:** End-to-end data flow with minimal UI

- [ ] Set up backend project structure
- [ ] Implement file cache system
- [ ] Create `/files/parse` endpoint
- [ ] Create `/extraction/extract-stream` endpoint (basic)
- [ ] Set up Next.js project with Tailwind
- [ ] Create minimal Zustand store
- [ ] Build ugly but functional upload → extract → results flow
- [ ] Docker Compose working

**Deliverable:** Can upload a file, hit extract, see results (ugly UI is fine)

### Week 2: Backend Completion + UI Foundation
**Goal:** All API endpoints working, design system in place

- [ ] Implement `/analysis/auto-detect` endpoint
- [ ] Add file deletion endpoint
- [ ] Add error handling to all endpoints
- [ ] Implement portal-localiser design system
- [ ] Create base UI components (Button, Card, Input, Select, Dialog)
- [ ] Apply styling to workspace layout

**Deliverable:** Backend feature-complete, UI looks good but sparse

### Week 3: File Management
**Goal:** Full file upload and organization UX

- [ ] Build FileUploadZone with drag-and-drop
- [ ] Build FileList with inline editing
- [ ] Implement file deletion with confirmation
- [ ] Build SubtypeManager (add/remove categories)
- [ ] Connect auto-detect to UI
- [ ] Show file preview when selected

**Deliverable:** File management fully functional

### Week 4: Extraction Flow
**Goal:** Complete extraction with progress and results

- [ ] Build SettingsPanel
- [ ] Build ExtractionProgress modal with SSE
- [ ] Implement cancellation
- [ ] Build ResultsDialog with tabs
- [ ] Add syntax highlighting for JS
- [ ] Add markdown rendering
- [ ] Implement download buttons

**Deliverable:** Full extraction flow working

### Week 5: Polish & Error Handling
**Goal:** Production-ready UX

- [ ] Add comprehensive error handling
- [ ] Error toasts for API failures
- [ ] Retry buttons where appropriate
- [ ] Loading states everywhere
- [ ] Empty states
- [ ] Keyboard shortcuts (Delete, Enter to extract)
- [ ] Add animations/transitions
- [ ] Cost estimation display

**Deliverable:** Polished, error-resilient application

### Week 6: Testing & Documentation
**Goal:** Ready for deployment

- [ ] End-to-end testing (manual test matrix)
- [ ] Compare results with Streamlit app
- [ ] Fix discovered bugs
- [ ] Write user guide
- [ ] Update README
- [ ] Production Docker config
- [ ] Final cleanup

**Deliverable:** Deployable application with documentation

---

## 7. CRITICAL FILES (Priority Order)

### Backend (Create)
1. `backend/src/cache/file_cache.py` - File caching system
2. `backend/src/api/main.py` - FastAPI app
3. `backend/src/api/routes/files.py` - File endpoints
4. `backend/src/api/routes/extraction.py` - SSE extraction
5. `backend/src/api/routes/analysis.py` - Auto-detection
6. `backend/src/api/models/requests.py` - Request models
7. `backend/src/api/models/responses.py` - Response models

### Frontend (Create)
8. `frontend/src/lib/store.ts` - Zustand store
9. `frontend/src/lib/api.ts` - API client with SSE
10. `frontend/src/app/workspace/page.tsx` - Main workspace
11. `frontend/src/components/project/FileUploadZone.tsx`
12. `frontend/src/components/project/FileList.tsx`
13. `frontend/src/components/project/SettingsPanel.tsx`
14. `frontend/src/components/project/ExtractionProgress.tsx`
15. `frontend/src/components/results/ResultsDialog.tsx`
16. `frontend/src/styles/globals.css` - Theme

### Infrastructure (Create)
17. `docker-compose.yml`
18. `backend/Dockerfile`
19. `frontend/Dockerfile`
20. `backend/requirements.txt`

### Modify (Minimal)
21. `src/core_cartographer/config.py` - Add API settings

---

## 8. DEPENDENCIES

### Backend (requirements.txt)
```txt
# Existing core
anthropic>=0.40.0
python-dotenv>=1.0.0
python-docx>=1.1.0
pypdf>=4.0.0
tiktoken>=0.8.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
langdetect>=1.0.9

# NEW: FastAPI
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6
sse-starlette>=1.8.0
```

### Frontend (package.json)
```json
{
  "name": "cartographer-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-progress": "^1.0.3",
    "lucide-react": "^0.312.0",
    "sonner": "^1.4.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33"
  }
}
```

---

## 9. MVP FEATURES

### Must-Have
- [x] File upload with drag-and-drop
- [x] Backend file caching (no large payloads)
- [x] File list with inline editing
- [x] Inline file deletion
- [x] Auto-detection (languages, pairs)
- [x] SSE extraction with progress
- [x] Cancellable extraction
- [x] Results viewer with syntax highlighting
- [x] Download results
- [x] Live cost estimation
- [x] Settings panel (batch mode, debug mode)
- [x] Error handling with toasts

### Future (V1.1+)
- [ ] Keyboard shortcuts
- [ ] File search/filter
- [ ] Bulk operations
- [ ] Dark mode toggle
- [ ] Supabase integration
- [ ] Project persistence

---

## 10. TESTING STRATEGY

### Manual Test Matrix

| Scenario | Steps | Expected |
|----------|-------|----------|
| Upload single file | Drag PDF to zone | File appears in list with tokens |
| Upload invalid file | Drag .exe | Error toast, file not added |
| Upload large file | 15MB PDF | Error toast (over 10MB limit) |
| Delete file | Click X, confirm | File removed, toast shown |
| Auto-detect | Upload EN+DE pair | Languages detected, pair #1 assigned |
| Change subtype | Select dropdown | Immediate update, no flicker |
| Extract single | One subtype, click Extract | Progress modal, results shown |
| Extract batch | Multiple subtypes | Per-subtype progress, all results |
| Cancel extraction | Click Cancel mid-way | Extraction stops, modal closes |
| Network error | Disconnect WiFi | Error toast with retry option |
| Refresh page | F5 during editing | State cleared (expected) |

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Upload file
curl -X POST http://localhost:8000/api/v1/files/parse \
  -F "file=@test.pdf"

# Auto-detect
curl -X POST http://localhost:8000/api/v1/analysis/auto-detect \
  -H "Content-Type: application/json" \
  -d '{"files": [{"file_id": "abc123"}]}'

# Extraction (SSE)
curl -X POST http://localhost:8000/api/v1/extraction/extract-stream \
  -H "Content-Type: application/json" \
  -d '{"client_name": "Test", "document_sets": [...], "batch_processing": true}'
```

---

## 11. RISK MITIGATION

| Risk | Mitigation | Status |
|------|------------|--------|
| Refresh loses work | Documented as expected behavior, clear UX | ✓ Addressed |
| Large payloads | Backend caching with file_ids | ✓ Addressed |
| Extraction timeout | SSE streaming mandatory | ✓ Addressed |
| Unreliable dropdowns | Radix UI primitives | ✓ Addressed |
| Docker networking | Separate localhost vs container URLs | ✓ Addressed |
| Type drift | Document manual sync, add generation later | ✓ Addressed |
| Cache fills disk | Auto-cleanup every 30 mins, 1hr expiry | ✓ Addressed |

---

## SUMMARY

This migration plan replaces the Streamlit 3-step wizard with a modern single-page workspace featuring:

- **Efficient data flow** - Backend caches file content, frontend only stores metadata
- **Reliable extraction** - SSE streaming with per-subtype progress, cancellable
- **Better UX** - Inline editing, reliable dropdowns (Radix UI), clear error states
- **Clean architecture** - FastAPI wraps existing Python, minimal code changes
- **Production-ready** - Docker Compose, error handling, documented testing

**Timeline:** 6 weeks
**Key Decisions:** Stateless (refresh=reset), backend cache, SSE mandatory, settings panel
**Future Ready:** Architecture supports Supabase integration for persistence later
