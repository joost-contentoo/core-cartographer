# Core Cartographer

**Modern, Fast, Reliable** ✨

Extract **validation rules** and **localization guidelines** from documentation using Claude AI.

<img src="https://img.shields.io/badge/Next.js-14-black" alt="Next.js 14" />
<img src="https://img.shields.io/badge/FastAPI-0.115-009688" alt="FastAPI 0.115" />
<img src="https://img.shields.io/badge/Claude-Opus_4.5-7C3AED" alt="Claude Opus 4.5" />
<img src="https://img.shields.io/badge/TypeScript-5.x-3178C6" alt="TypeScript 5" />

---

## What It Does

Core Cartographer analyzes your localization documentation (style guides, brand docs, translation memories) and automatically extracts:

1. **Client Rules (JavaScript)** - Machine-readable validation config for automated content checking
2. **Guidelines (Markdown)** - Human-readable style guides for translators and writers

**Key Benefits:**
- ✅ **AI-Powered Analysis** - Claude Opus 4.5 identifies patterns and rules
- ✅ **Multi-Language Support** - Automatic language detection and translation pairing
- ✅ **Category-Based Organization** - Separate rules for technical, legal, marketing content
- ✅ **Real-Time Feedback** - Live cost estimation and progress tracking
- ✅ **Modern UI** - Beautiful, responsive interface built with Next.js

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │ File Upload  │───▶│   Zustand    │───▶│  React UI    │          │
│  │  Components  │    │    Store     │    │  Components  │          │
│  └──────────────┘    │  (metadata)  │    └──────────────┘          │
│                      └──────┬───────┘                               │
└─────────────────────────────┼──────────────────────────────────────┘
                              │ REST API + SSE
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        BACKEND (FastAPI)                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │
│  │   API Routes │───▶│  File Cache  │───▶│    Python    │          │
│  │   /files     │    │   (temp)     │    │     Core     │          │
│  │   /analysis  │    └──────────────┘    │  extractor   │          │
│  │   /extraction│                         │   parser     │          │
│  └──────────────┘                         └──────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- **Stateless Architecture** - No database required, refresh clears state
- **Backend File Caching** - Efficient handling of large documents
- **SSE Streaming** - Real-time extraction progress updates
- **Metadata-Only Frontend** - Fast, responsive UI with minimal memory footprint

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **npm or yarn**
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))

### Installation

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/core-cartographer.git
cd core-cartographer
```

#### 2. Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (use root .env file)
# Note: The .env file should be at the project root, not in backend/
# The backend automatically reads from ../.env
# If you prefer backend/.env, copy: cp .env.example .env
```

#### 3. Setup Frontend

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install
# or: yarn install

# Configure environment (optional - only needed if API is not at localhost:8000)
# Create .env.local with: NEXT_PUBLIC_API_URL=http://your-backend-url:8000
```

### Running the Application

#### Option 1: Using Startup Scripts (Recommended)

```bash
# From project root
./start-backend.sh   # Terminal 1
./start-frontend.sh  # Terminal 2
```

Then open `http://localhost:3000` in your browser.

#### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

#### Option 3: Docker Compose

**Development:**
```bash
docker-compose up
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed Docker deployment instructions.

---

## Usage

### Step-by-Step Workflow

1. **Enter Client Name**
   - Type your client's name in the input field
   - This name appears in the extracted guidelines

2. **Upload Documentation Files**
   - Click or drag & drop files into the upload zone
   - Supported formats: PDF, DOCX, TXT, MD
   - Max file size: 10MB

3. **Auto-Detect Languages** (Optional)
   - Click "Auto-Detect Languages" button
   - Identifies file languages (EN, DE, FR, etc.)
   - Automatically pairs translation files

4. **Organize by Category** (Optional)
   - Add custom categories: "technical", "legal", "marketing"
   - Assign files to categories via dropdown
   - Each category produces separate output

5. **Configure Settings** (Optional)
   - Click "Settings" button
   - Choose processing mode (Batch/Individual)
   - Select AI model (Opus 4.5, Sonnet 4, etc.)
   - Enable debug mode if needed

6. **Start Extraction**
   - Click "Start Extraction" button (or press Enter)
   - Watch real-time progress
   - Cancel anytime if needed

7. **Review Results**
   - Results dialog opens automatically
   - Switch between categories (if multiple)
   - View Client Rules (syntax-highlighted JS)
   - View Guidelines (rendered Markdown)
   - Download individual files or all at once

### Example Output

**Client Rules (`technical_client_rules.js`):**
```javascript
const clientRules = {
  terminology: {
    translate: ["user", "settings", "dashboard"],
    doNotTranslate: ["API", "OAuth", "Acme Corp"],
  },
  formatting: {
    dates: "DD/MM/YYYY",
    numbers: "1.234,56",
    currency: "€",
  },
  style: {
    formality: "formal",
    tone: "professional",
    person: "second",
  },
};
```

**Guidelines (`technical_guidelines.md`):**
```markdown
# Acme Corporation - Technical Documentation Guidelines

## Overview
Guidelines for translating Acme's technical documentation and API references.

## Target Audience
- Software developers
- Technical integrators
- IT administrators

## Tone and Style
- **Formality:** Formal, professional tone
- **Person:** Second person ("you")
- **Voice:** Active voice preferred

## Terminology
- **API:** Do not translate (keep as "API")
- **Dashboard:** Translate (e.g., "Tableau de bord" in French)
```

---

## Features

### File Management
- ✅ Drag & drop or click to upload
- ✅ Preview file content (first 500 chars)
- ✅ Delete files individually
- ✅ Auto-detect file languages
- ✅ Automatic translation pairing

### Category Organization
- ✅ Create custom categories
- ✅ Assign files to categories
- ✅ Separate output per category
- ✅ Visual category badges

### Extraction Settings
- ✅ **Batch Mode** - Single API call (faster, cheaper)
- ✅ **Individual Mode** - Separate calls per category
- ✅ **Model Selection** - Opus 4.5, Sonnet 4, Sonnet 3.5
- ✅ **Debug Mode** - Save prompts without API calls

### Real-Time Feedback
- ✅ Live cost estimation
- ✅ Token count tracking
- ✅ SSE streaming progress
- ✅ Per-category status updates
- ✅ Cancellable extractions

### Results Display
- ✅ Syntax-highlighted JavaScript
- ✅ Rendered Markdown
- ✅ Download individual files
- ✅ Bulk download all results
- ✅ Token usage statistics

### Polish & UX
- ✅ Error handling with retry
- ✅ Keyboard shortcuts (Delete, Enter)
- ✅ Smooth animations & transitions
- ✅ Enhanced empty states
- ✅ Responsive design

---

## Keyboard Shortcuts

| Key | Action | Requirements |
|-----|--------|--------------|
| **Delete** | Delete selected file | File must be selected |
| **Enter** | Start extraction | Client name + files uploaded |

---

## Project Structure

```
core-cartographer/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/
│   │   │   ├── main.py        # FastAPI app
│   │   │   ├── routes/
│   │   │   │   ├── files.py   # Upload & parse
│   │   │   │   ├── analysis.py# Language detection
│   │   │   │   └── extraction.py # SSE extraction
│   │   │   └── models/        # Pydantic models
│   │   ├── cache/             # File caching
│   │   └── core_cartographer/ # Python core (unchanged)
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx     # Root layout
│   │   │   ├── page.tsx       # Landing page
│   │   │   └── workspace/     # Main workspace
│   │   ├── components/
│   │   │   ├── project/       # File upload, list, etc.
│   │   │   ├── results/       # Results dialog, viewers
│   │   │   └── ui/            # Reusable UI components
│   │   ├── lib/
│   │   │   ├── api.ts         # Backend API client
│   │   │   ├── store.ts       # Zustand state
│   │   │   └── types.ts       # TypeScript types
│   │   └── styles/
│   ├── public/
│   ├── package.json
│   └── next.config.js
│
├── templates/                  # Example outputs for AI
│   ├── client_rules_example_condensed.js
│   └── guidelines_example_condensed.md
├── instructions/               # Extraction instructions
│   ├── extraction_instructions.md
│   └── archive/
│       └── extraction_instructions_v1.md
│
├── .env.example
├── docker-compose.yml           # Development Docker setup
├── docker-compose.prod.yml      # Production Docker setup
├── start-backend.sh
├── start-frontend.sh
├── README.md
├── QUICKSTART.md
├── USER_GUIDE.md
└── DEPLOYMENT.md
```

---

## Configuration

### Backend Environment Variables

```bash
# .env in project root (or backend/.env)
ANTHROPIC_API_KEY=sk-ant-...    # Required
MODEL=claude-opus-4-5-20251101  # Optional (default)
DEBUG_MODE=false                 # Optional (default)
CACHE_EXPIRY_HOURS=1            # Optional (default)
```

**Note:** The backend can read `.env` from either the project root or `backend/.env`. The project root is recommended for simpler configuration.

### Frontend Environment Variables

```bash
# .env.local in frontend/ (optional)
NEXT_PUBLIC_API_URL=http://localhost:8000  # Default value, only set if different
```

**Note:** The frontend defaults to `http://localhost:8000` for the backend API. Only create `.env.local` if you need a different URL.

---

## API Documentation

When the backend is running, visit:
- **Interactive API docs:** `http://localhost:8000/docs`
- **OpenAPI schema:** `http://localhost:8000/openapi.json`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/files/parse` | Upload and parse file |
| `DELETE` | `/files/{file_id}` | Delete cached file |
| `POST` | `/analysis/auto-detect` | Detect languages & pairs |
| `POST` | `/extraction/extract-stream` | Extract rules (SSE) |

---

## Development

### Backend Development

```bash
cd backend
source .venv/bin/activate

# Run with auto-reload
uvicorn src.api.main:app --reload --port 8000

# Run tests
pytest

# Format code
black src/
ruff check src/
```

### Frontend Development

```bash
cd frontend

# Run dev server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build production
npm run build
```

---

## Testing

### Automated Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

---

## Deployment

### Production Build

**Backend:**
```bash
cd backend
pip install -r requirements.txt
gunicorn src.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```

### Docker Deployment

```bash
docker-compose -f docker-compose.prod.yml up -d
```

For complete deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running quickly
- **[User Guide](USER_GUIDE.md)** - Complete user documentation
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when backend is running)

---

## Troubleshooting

### Backend Won't Start

```bash
# Check Python version
python --version  # Should be 3.11+

# Verify virtual environment is activated
which python  # Should point to .venv

# Check dependencies
pip install -r requirements.txt

# Verify API key
grep ANTHROPIC_API_KEY backend/.env
```

### Frontend Won't Start

```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000
```

### Upload Fails

- ✅ Check file format (PDF, DOCX, TXT, MD only)
- ✅ Verify file size <10MB
- ✅ Ensure backend is running
- ✅ Check CORS configuration

### Extraction Fails

- ✅ Verify `ANTHROPIC_API_KEY` is set
- ✅ Check API key has credits
- ✅ Review backend logs for errors
- ✅ Try with smaller files first

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Roadmap

### v2.1 (Current)
- ✅ Next.js + FastAPI migration complete
- ✅ Full extraction workflow
- ✅ Real-time progress with SSE
- ✅ Results display with syntax highlighting
- ✅ Download functionality
- ✅ Keyboard shortcuts & animations

### v2.2 (Next)
- [ ] Expanded automated testing suite
- [ ] Result persistence (optional)
- [ ] User authentication (optional)
- [ ] API rate limiting
- [ ] Enhanced error recovery

### v3.0 (Future)
- [ ] Multi-project support
- [ ] Version control for rules
- [ ] Integration with TMS systems
- [ ] Collaborative editing
- [ ] Advanced analytics

---

## License

ISC

---

## Credits

Built with:
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Claude AI](https://www.anthropic.com/) - AI extraction engine
- [Zustand](https://github.com/pmndrs/zustand) - State management
- [Tailwind CSS](https://tailwindcss.com/) - Styling
- [Radix UI](https://www.radix-ui.com/) - Accessible components

Inspired by the portal-localiser design system.

---

**Core Cartographer v2.0** - Modern, Fast, Reliable ✨

For questions or support, please open an issue on GitHub.
