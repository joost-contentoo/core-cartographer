# Core Cartographer Migration Guide

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- Anthropic API key

### Setup

1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Workflow

**Hot Reload:** Both frontend and backend support hot reload. Changes to source files will automatically restart the services.

**View Logs:**
```bash
docker-compose logs -f
```

**Stop Services:**
```bash
docker-compose down
```

**Clean Everything (including cache):**
```bash
docker-compose down -v
```

## Manual Setup (Without Docker)

### Backend

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Run the server:**
   ```bash
   uvicorn src.api.main:app --reload
   ```

### Frontend

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Set environment variables:**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

## Architecture Overview

### Backend (FastAPI)
- **File Cache:** Temporary storage for parsed documents (1-hour expiry)
- **API Routes:**
  - `/api/v1/files/parse` - Upload and parse files
  - `/api/v1/files/{file_id}` - Delete cached files
  - `/api/v1/analysis/auto-detect` - Language detection and pairing
  - `/api/v1/extraction/extract-stream` - SSE extraction with progress

### Frontend (Next.js)
- **Single Page:** `/workspace` - Main workspace with all functionality
- **Zustand Store:** Metadata-only state management (no file content)
- **SSE Client:** Real-time extraction progress updates

### Data Flow
1. User uploads files → Frontend sends to backend
2. Backend parses files, stores in cache, returns `file_id`
3. Frontend stores metadata only (filename, tokens, file_id)
4. User triggers extraction → Frontend sends file_ids
5. Backend retrieves content from cache, processes with Claude
6. Backend streams progress via SSE → Frontend updates UI
7. Results displayed in frontend

## Migration Status

### ✅ Week 1: Walking Skeleton (COMPLETE)
- [x] Backend project structure
- [x] File cache system
- [x] /files/parse endpoint
- [x] /extraction/extract-stream endpoint
- [x] Next.js setup with Tailwind
- [x] Zustand store
- [x] Basic upload → extract → results flow
- [x] Docker Compose

### 🔄 Week 2-6: Remaining Work
See `MIGRATION_PLAN_DETAILED.md` for full timeline and remaining tasks.

## Testing

### Test File Upload
```bash
curl -X POST http://localhost:8000/api/v1/files/parse \
  -F "file=@test.pdf"
```

### Test Health Check
```bash
curl http://localhost:8000/health
```

### Test Frontend
Open http://localhost:3000 and:
1. Enter a client name
2. Upload files
3. Click "Auto-Detect"
4. Click "Start Extraction"
5. View results

## Troubleshooting

### Backend Issues
- **"Module not found":** Ensure you're running from project root
- **CORS errors:** Check `allow_origins` in `backend/src/api/main.py`
- **File parsing fails:** Verify file format is supported (PDF, DOCX, TXT, MD)

### Frontend Issues
- **Can't connect to API:** Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- **White screen:** Check browser console for errors
- **SSE not working:** Check network tab, verify backend is running

### Docker Issues
- **Port conflicts:** Change ports in `docker-compose.yml`
- **Cache not clearing:** Run `docker-compose down -v`
- **Build fails:** Try `docker-compose build --no-cache`

## Next Steps

1. **Polish UI** (Week 2-3): Implement portal-localiser design system
2. **File Management** (Week 3): Drag-and-drop, better file list
3. **Extraction Flow** (Week 4): Progress modal, results dialog
4. **Error Handling** (Week 5): Comprehensive error states
5. **Testing** (Week 6): End-to-end testing, deployment

See `MIGRATION_PLAN_DETAILED.md` for complete implementation plan.
