# Core Cartographer - Quick Start

## Prerequisites
- Python 3.11+ (or 3.12 recommended)
- Node.js 20+
- Anthropic API key

## Setup (First Time Only)

1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Note: The .env.example is at the project root
   # The .env file will also be created at the project root
   ```

2. **Add your API key to `.env` (in the project root):**
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

3. **Run setup:**
   ```bash
   ./run-manual.sh
   ```

## Running the Application

**Terminal 1 - Start Backend:**
```bash
./start-backend.sh
```
Wait until you see: `Application startup complete.`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```
Wait until you see: `✓ Ready in X.Xs`

## Access the App

Open your browser to: **http://localhost:3000**

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

1. Enter a client name
2. Upload files (PDF, DOCX, TXT, MD)
3. Click "Auto-Detect" for language detection
4. Assign files to categories
5. Click "Start Extraction"
6. View and download results

## Stopping

Press `Ctrl+C` in each terminal to stop the services.

## Troubleshooting

**"Port already in use":**
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**"Module not found":**
- Make sure you ran `./run-manual.sh` first
- Check that `.env` exists and has your API key

**Frontend won't connect:**
- Verify backend is running at http://localhost:8000/health
- Check `frontend/.env.local` has: `NEXT_PUBLIC_API_URL=http://localhost:8000`
