# ✅ Setup Complete!

## What's Installed

- ✅ Python 3.12.12
- ✅ Virtual environment (`.venv/`)
- ✅ All dependencies (including Streamlit GUI)
- ✅ Core Cartographer package
- ✅ Both CLI and GUI interfaces

## 🔑 Final Step: Add Your API Key

1. Edit the `.env` file:
   ```bash
   nano .env
   # or open with any text editor
   ```

2. Replace `sk-ant-your-key-here` with your actual Anthropic API key

3. Save and close

## 🚀 Launch Commands

### GUI (Recommended)
```bash
./start-gui.sh
```

### CLI (Alternative)
```bash
source .venv/bin/activate
cartographer
```

## 📋 Quick Test Checklist

1. [ ] API key added to `.env`
2. [ ] Run `./start-gui.sh`
3. [ ] Browser opens to `http://localhost:8501`
4. [ ] Enter client name (e.g., "test_client")
5. [ ] Enter subtype (e.g., "demo")
6. [ ] Upload some documents (.txt, .md, .docx, or .pdf)
7. [ ] Click "Extract Rules & Guidelines"
8. [ ] Download the results!

## 💡 Tips

- **GUI**: Best for quick one-off extractions, drag & drop files from anywhere
- **CLI**: Best for batch processing files already in `input/` folders
- **Cost**: Typical extraction costs $0.10-$2.00 depending on document size

## 🆘 Common Issues

**Import errors?**
- Make sure virtual environment is activated: `source .venv/bin/activate`

**API key errors?**
- Check that `.env` file exists and has your key
- No spaces around the `=` sign in `.env`

**Port already in use?**
- Stop other Streamlit instances
- Or manually specify port: `streamlit run src/core_cartographer/gui.py --server.port 8502`

## 📖 Documentation

- `README.md` - Full project documentation
- `GUI_QUICKSTART.md` - GUI usage guide
- `templates/` - Example output formats
- `instructions/` - Extraction guidelines for Claude

---

**Ready to go!** Just add your API key and run `./start-gui.sh` 🚀
