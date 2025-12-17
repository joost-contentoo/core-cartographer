# GUI Quick Start Guide

## 🚀 Launch the GUI

**Option 1: One-click script (easiest)**
```bash
./start-gui.sh
```

**Option 2: Manual launch**
```bash
source .venv/bin/activate
streamlit run src/core_cartographer/gui.py
```

The GUI will automatically open in your browser at `http://localhost:8501`

**Troubleshooting:**
- If you get import errors, make sure the virtual environment is activated
- If the browser doesn't open automatically, manually go to `http://localhost:8501`

## 🎯 Using the GUI

### 1. **Configure** (Sidebar)
   - Enter client name (e.g., "dundle")
   - Enter document subtype (e.g., "gift_cards")

### 2. **Upload Documents**
   - Click "Browse files" or drag & drop
   - Upload multiple documents (.txt, .md, .docx, .pdf)

### 3. **Review Summary**
   - Check document count
   - View estimated token usage
   - See estimated API cost

### 4. **Extract**
   - Click "Extract Rules & Guidelines"
   - Wait for Claude to analyze (typically 30-60 seconds)

### 5. **Download Results**
   - View JavaScript rules and Markdown guidelines
   - Download both files

## 💡 Tips

- **Keep it running**: Streamlit auto-reloads on code changes
- **Multiple sessions**: Open multiple browser tabs for different clients
- **Keyboard shortcuts**:
  - `r` - Rerun the app
  - `c` - Clear cache
  - `?` - Show keyboard shortcuts

## 🛑 Stopping the GUI

Press `Ctrl+C` in the terminal to stop the server

## 🎨 GUI Features

- ✅ Drag & drop file upload
- ✅ Real-time cost estimation
- ✅ Syntax-highlighted JavaScript preview
- ✅ Rendered Markdown preview
- ✅ One-click file downloads
- ✅ Clean, professional interface
- ✅ 100% Python - no Node.js required!
