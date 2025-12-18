# PRD: Core Cartographer Migration (Streamlit → Next.js + FastAPI + Supabase)

## Goal
Migrate the existing Streamlit prototype to a scalable, production-ready web application using:
- **Frontend**: Next.js (React) for a premium, responsive UI.
- **Backend**: FastAPI (Python) to expose the existing Core Cartographer logic as an API.
- **Infrastructure**: Supabase for Authentication, Database (Postgres), and File Storage.

## User Review Required
> [!IMPORTANT]
> **Architecture Shift**: This is a complete rewrite of the frontend and a significant refactoring of the entry points. The core logic (`extractor.py`, `parser.py`) remains, but `gui.py` and `app.py` will be retired.

> [!WARNING]
> **Data Migration**: Current local session data is ephemeral. The new system will persist data in Supabase. There is no "old data" to migrate, but this changes the data lifecycle.

## Architecture

### 1. Frontend (Next.js)
- **Framework**: Next.js 14+ (App Router).
- **Styling**: Tailwind CSS + Shadcn UI (for premium look).
- **State**: React Query (Server State) + Zustand (Client State).
- **Auth**: Supabase Auth (Email/Password, Magic Link).
- **Responsibilities**:
  - User Authentication & Session Management.
  - File Upload (Drag & Drop) -> Direct to Supabase Storage.
  - Organization Interface (Data Grid for categorizing files).
  - Results Visualization (Markdown rendering, Code blocks).

### 2. Backend (FastAPI - Python)
- **Framework**: FastAPI.
- **Responsibilities**:
  - **Parsing**: Fetch file from Storage -> Text.
  - **Analysis**: Auto-detect language and pairs.
  - **Extraction**: Construct prompts (using `extractor.py`) -> Call Claude -> Return JSON.
  - **Stateless**: The API should be stateless. It receives references to files (URLs or Storage Paths), processes them, and returns results.

### 3. Database & Storage (Supabase)
- **Storage**: Bucket `raw-documents`.
- **Database Schema**:
  - `profiles`: User data.
  - `projects`: A container for a set of documents (replaces current "Client Name" session).
  - `documents`: Metadata (filename, creation_date, project_id, storage_path, language, pair_id, subtype).
  - `extractions`: Results (subtype, client_rules_json, guidelines_md, input_tokens, output_tokens).

## Database Schema (Proposed)

```sql
-- Projects
create table projects (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users not null,
  name text not null,
  created_at timestamptz default now()
);

-- Documents
create table documents (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects on delete cascade,
  filename text not null,
  storage_path text not null,
  content_type text, -- 'application/pdf', 'text/markdown', etc.
  size_bytes bigint,
  
  -- Analysis Metadata
  language text default 'UNKNOWN',
  subtype text default 'general',
  pair_id text, -- null represents unpaired
  
  created_at timestamptz default now()
);

-- Extractions (Results)
create table extractions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects on delete cascade,
  subtype text not null,
  client_rules text, -- The generated JS
  guidelines text, -- The generated Markdown
  
  -- Metrics
  input_tokens int,
  output_tokens int,
  cost_usd numeric,
  
  created_at timestamptz default now()
);
```

## API Endpoints (Python Backend)

### `POST /api/v1/analyze`
**Input**: List of storage paths or signed URLs.
**Action**: 
1. Download files.
2. Run `parser.py` code.
3. Run `data_manager.py` logic (Language detection, Pairing).
**Output**: List of objects with `{ filename, language, pair_id }`.

### `POST /api/v1/extract`
**Input**: 
- `project_id`.
- List of document metadata (subtypes, pairs).
- `settings` (Model, Batch Mode).
**Action**:
1. Reconstruct `DocumentSet` objects.
2. Call `extract_rules_and_guidelines`.
**Output**: `ExtractionResult` object.

## Implementation Steps

### Phase 1: Backend API Setup [Python]
1.  Initialize FastAPI project structure in `src/api`.
2.  Port `config.py` to be environment-variable aware (remove Streamlit dependencies).
3.  Create endpoints that wrap `parser.py` and `extractor.py`.
4.  Verify API works with `curl` (local testing).

### Phase 2: Supabase Setup
1.  Create Supabase project (User must provide credentials/URL).
2.  Apply SQL Schema.
3.  Generate Types (Supabase CLI).

### Phase 3: Frontend Construction [Node/React]
1.  Initialize Next.js app.
2.  Implement Auth (Login Screen).
3.  Implement "Create Project" flow.
4.  Implement "Upload & Organize" view (recreating Step 1 & 2 of current GUI).
5.  Implement "Results" view.

### Phase 4: Integration
1.  Connect React Frontend to Python Backend.
2.  End-to-End test of the flow: Login -> Create Project -> Upload -> Analyze (API) -> Organize -> Extract (API) -> View Results.
