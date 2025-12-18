# Core Cartographer - User Guide

**Version:** 2.0 (Next.js + FastAPI)
**Last Updated:** December 18, 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Workspace Overview](#workspace-overview)
4. [Step-by-Step Workflow](#step-by-step-workflow)
5. [Features & Functions](#features--functions)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Introduction

### What is Core Cartographer?

Core Cartographer is a tool that **extracts localization rules and guidelines** from your documentation. It analyzes your style guides, brand documents, and translation memories to produce:

1. **Client Rules (JavaScript)** - Programmatic rules for translation validation
2. **Guidelines (Markdown)** - Human-readable style guidelines for translators

### Who Should Use This Tool?

- **Localization Managers** - Creating client-specific translation rules
- **Translation Project Managers** - Documenting style guidelines
- **Language Service Providers** - Standardizing client requirements
- **In-house Localization Teams** - Maintaining consistency across projects

### Key Benefits

- ✅ **Automated Extraction** - AI-powered analysis of documentation
- ✅ **Consistent Output** - Standardized rules and guidelines format
- ✅ **Multi-Language Support** - Handles translation pairs automatically
- ✅ **Category-Based** - Organize rules by document type (technical, legal, marketing, etc.)
- ✅ **Real-Time Feedback** - Live cost estimation and progress tracking

---

## Getting Started

### System Requirements

- **Modern web browser** (Chrome, Firefox, Safari)
- **Internet connection** (for API calls)
- **Supported file formats:** PDF, DOCX, TXT, MD

### Accessing the Application

1. Navigate to `http://localhost:3000` (or your deployed URL)
2. The workspace page opens automatically

### First-Time Setup

No configuration required! Just have your:
- **Anthropic API key** configured on the backend
- **Documentation files** ready to upload

---

## Workspace Overview

The workspace is divided into three main sections:

### Left Panel (Main Area)

**1. Project Details Card**
- Enter your **Client Name** (required)
- This name appears in extracted guidelines

**2. File Upload Zone**
- Drag & drop or click to upload files
- Supports PDF, DOCX, TXT, MD formats
- Max 10MB per file

**3. Files List**
- Shows all uploaded files
- Each file displays:
  - Filename
  - Detected language (e.g., EN, DE, FR)
  - Token count
  - Pair ID (if part of translation pair)
  - Category dropdown
- Actions: Select, change category, delete

**4. Categories Manager**
- Add custom categories (e.g., "technical", "legal", "marketing")
- Default category: "general"
- Remove categories (must have at least one)
- Assign files to categories via dropdown

### Right Panel (Actions & Preview)

**1. Actions Card**
- **Settings** - Configure extraction options
- **Auto-Detect Languages** - Identify languages and pairs
- **Start Extraction** - Begin AI analysis

**2. Cost Display**
- Shows total tokens across all files
- Estimated cost in USD
- Updates in real-time as files are added/removed

**3. File Preview**
- Click any file to view its content
- Shows first 500 characters
- Displays metadata (language, category, tokens)

**4. Results Card** (after extraction)
- Appears when extraction completes
- Shows number of categories processed
- Click "View Results" to open full results

---

## Step-by-Step Workflow

### Step 1: Enter Client Name

1. Click in the **Client Name** input field
2. Type your client's name (e.g., "Acme Corporation")
3. This name will appear in the extracted guidelines

**Tip:** Use a descriptive name like "Acme - Technical Documentation" for clarity

---

### Step 2: Upload Documentation Files

#### Method A: Click to Upload
1. Click the **"Click to upload or drag files here"** zone
2. Select one or more files from your computer
3. Wait for upload to complete

#### Method B: Drag & Drop
1. Open your file explorer
2. Drag files directly onto the upload zone
3. Zone highlights when ready to drop
4. Release to upload

**What happens:**
- Files are parsed and analyzed for token count
- Default language: "en"
- Default category: "general"
- Each file gets a unique ID

**Supported formats:**
- ✅ PDF (`.pdf`)
- ✅ Word Documents (`.docx`)
- ✅ Text Files (`.txt`)
- ✅ Markdown (`.md`)

---

### Step 3: Detect Languages & Pairs (Optional)

If your files are in different languages or form translation pairs:

1. Click **"Auto-Detect Languages"** button
2. Wait for analysis (usually 2-5 seconds)
3. Review detected languages (shown in badges)
4. Check for **Pair IDs** (e.g., "Pair #1")

**How pairing works:**
- Files with similar names (e.g., `guide_en.pdf`, `guide_de.pdf`)
- Similar content length (within 20% difference)
- Automatically grouped with matching Pair ID

**Example:**
```
guide_en.pdf  → Language: EN, Pair #1
guide_de.pdf  → Language: DE, Pair #1
```

---

### Step 4: Organize Files by Category (Optional)

Categories help organize extracted rules by document type:

#### Add a Category
1. Scroll to **"Categories"** section
2. Type new category name (e.g., "technical")
3. Click **"Add"** button
4. Category appears as a badge

#### Assign Files to Categories
1. Find file in the **Files** list
2. Click the **category dropdown** (shows "general" by default)
3. Select desired category
4. File is now assigned

**Example categories:**
- `general` - Default for all files
- `technical` - Technical documentation, API guides
- `legal` - Terms of service, contracts
- `marketing` - Brand guidelines, tone of voice
- `ui` - UI strings, microcopy

**Why use categories?**
- Each category produces separate rules and guidelines
- Allows different styles for different content types
- Easier to manage large projects

---

### Step 5: Configure Settings (Optional)

Click the **"Settings"** button to customize extraction:

#### Processing Mode
- **Batch (Recommended)** - Single API call for all categories (faster, cheaper)
- **Individual** - Separate API call per category (more detailed)

#### Model Selection
- **Claude Opus 4.5** (Default, recommended) - Highest quality
- **Claude Sonnet 4** - Faster, good quality
- **Claude 3.5 Sonnet** - Legacy option

#### Debug Mode
- **Off** (Default) - Normal extraction
- **On** - Saves prompts to disk without API calls (testing only)

**When to change settings:**
- Use **Individual** mode for very different document types
- Use **Sonnet** models to reduce costs
- Enable **Debug** to test without consuming API credits

---

### Step 6: Start Extraction

1. Verify:
   - ✅ Client name entered
   - ✅ Files uploaded
   - ✅ Categories assigned (if needed)
2. Click **"Start Extraction"** button (or press **Enter**)
3. Progress modal appears

**Progress Modal shows:**
- Current category being processed
- Completed categories (with checkmarks ✓)
- Total progress
- **Cancel** button (if needed)

**What happens during extraction:**
- AI analyzes your documentation
- Identifies localization rules (terminology, style, formatting)
- Generates JavaScript validation rules
- Creates human-readable guidelines
- Estimates processing: 30-90 seconds per category

---

### Step 7: Review Results

When extraction completes:

1. **Results Dialog opens automatically**
2. Shows summary:
   - Number of categories processed
   - Total tokens used
   - **Download All** button

#### Navigate Categories (if multiple)
- Click category badges at top to switch
- Each category shows its own rules and guidelines

#### View Client Rules (JavaScript)
1. Click **"Client Rules"** tab
2. See syntax-highlighted JavaScript code
3. Rules include:
   - Terminology (do/don't translate specific terms)
   - Formatting rules (dates, numbers, currencies)
   - Style preferences (formality, tone)
4. Click **"Download"** to save as `.js` file

#### View Guidelines (Markdown)
1. Click **"Guidelines"** tab
2. See beautifully rendered markdown
3. Guidelines include:
   - Brand voice and tone
   - Style preferences
   - Target audience information
   - Cultural considerations
   - Examples and edge cases
4. Click **"Download"** to save as `.md` file

#### Download Options
- **Individual:** Download button on each tab
- **Bulk:** "Download All" button (downloads all categories × 2 files)

**Filenames:**
- Client Rules: `{category}_client_rules.js`
- Guidelines: `{category}_guidelines.md`

---

### Step 8: Close or Restart

#### Close Results
- Click **X** or outside dialog to close
- Results remain available via **"View Results"** button

#### Start New Extraction
- Clear files (delete individually)
- Change client name
- Upload new files
- Click "Start Extraction" again

**Note:** Refreshing the page clears all data (no persistence)

---

## Features & Functions

### File Management

#### Selecting Files
- Click any file in the list to **select** it
- Selected file is highlighted (light green background)
- Preview panel shows file content

#### Deleting Files
- **Method 1:** Click trash icon → confirm dialog → delete
- **Method 2:** Select file → press **Delete** key (instant)

#### File Preview
- Click file to see preview
- Shows:
  - Full filename
  - Language badge
  - Category badge
  - Token count
  - Pair ID (if applicable)
  - First 500 characters of content

### Category Management

#### Default Category
- All files start in "general" category
- Cannot delete the last remaining category

#### Multiple Categories
- Add as many as needed
- Files can only belong to one category
- Each category produces separate output

### Cost Estimation

- **Live updates** as files are added/removed
- Calculation: `(input_tokens + output_tokens) × model_price`
- Shown in USD
- Based on current token counts and selected model

### Language Detection

- Uses `langdetect` library
- Returns uppercase codes (EN, DE, FR, etc.)
- Manual override possible (edit file metadata)

### Translation Pairing

- Automatic based on:
  - Filename similarity
  - Content length similarity (±20%)
- Paired files share same Pair ID
- Used to create bilingual guidelines

---

## Keyboard Shortcuts

| Key | Action | Requirements |
|-----|--------|--------------|
| **Delete** | Delete selected file | File must be selected |
| **Enter** | Start extraction | Client name + files uploaded |

**Tips:**
- Delete key instantly removes files (no confirmation)
- Enter key won't trigger while typing in inputs
- Shortcuts disabled during extraction

---

## Tips & Best Practices

### File Preparation

✅ **DO:**
- Use clear, descriptive filenames
- Include language codes in names (e.g., `guide_en.pdf`)
- Upload complete documents (not fragments)
- Ensure files are text-based (not scanned images)

❌ **DON'T:**
- Upload encrypted or password-protected files
- Mix unrelated content types in one category
- Upload files larger than 10MB
- Use special characters excessively in filenames

### Category Organization

**For small projects (1-5 documents):**
- Use default "general" category
- No need to create subcategories

**For large projects (5+ documents):**
- Create categories by content type:
  - `technical` - API docs, developer guides
  - `marketing` - Website copy, ads
  - `legal` - Contracts, policies
  - `ui` - App strings, interface text

### Extraction Settings

**For best quality:**
- Use **Batch** mode with **Opus 4.5**
- This is the default and recommended

**To reduce costs:**
- Use **Sonnet 4** model
- ~60% cheaper with minimal quality loss

**For very different content types:**
- Use **Individual** mode
- Each category gets focused attention

### Results Review

**Client Rules (JavaScript):**
- Review for accuracy
- Integrate into your translation tool (e.g., portal-localiser)
- Update as client requirements change

**Guidelines (Markdown):**
- Share with translators and reviewers
- Include in translation packages
- Store in your TMS or knowledge base

### File Pairing

**To ensure correct pairing:**
- Use consistent naming: `doc_en.pdf`, `doc_de.pdf`
- Keep file sizes similar (source ≈ target)
- Run auto-detect after all files uploaded

---

## Troubleshooting

### Upload Issues

**Problem:** File won't upload
- ✅ Check file format (PDF, DOCX, TXT, MD only)
- ✅ Ensure file size <10MB
- ✅ Verify file isn't corrupted
- ✅ Try renaming file (remove special characters)

**Problem:** Upload succeeds but no content in preview
- ⚠️ File may be scanned image (not searchable text)
- ⚠️ PDF may be corrupt or encrypted
- ➡️ Try re-exporting or using different format

### Language Detection Issues

**Problem:** Wrong language detected
- ➡️ This is expected behavior (detection isn't perfect)
- ➡️ Doesn't affect extraction quality significantly

**Problem:** Files aren't paired
- ✅ Check filenames are similar (e.g., `guide_en`, `guide_de`)
- ✅ Ensure content length is comparable
- ✅ Try renaming files to match better

### Extraction Errors

**Problem:** "Extraction failed" error
- ✅ Check backend is running (`http://localhost:8000`)
- ✅ Verify API key is configured
- ✅ Check internet connection
- ✅ Click "Retry" button
- ➡️ Check backend logs for details

**Problem:** Extraction takes too long
- ⏱️ Normal time: 30-90 seconds per category
- ⏱️ Large files (10K+ tokens) take longer
- ⏱️ Multiple categories process sequentially
- ➡️ If >5 minutes, click "Cancel" and retry

**Problem:** Results seem incomplete or incorrect
- ✅ Ensure uploaded files contain relevant content
- ✅ Try using **Individual** mode instead of Batch
- ✅ Switch to **Opus 4.5** model for best quality
- ➡️ Review source documents for clarity

### Display Issues

**Problem:** UI looks broken or unstyled
- ✅ Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- ✅ Clear browser cache
- ✅ Try different browser (Chrome, Firefox, Safari)

**Problem:** Animations are janky
- ➡️ This is cosmetic only, doesn't affect functionality
- ➡️ May occur on slower machines

### Results Issues

**Problem:** Can't download files
- ✅ Check browser allows downloads
- ✅ Check download folder permissions
- ➡️ Try different browser

**Problem:** Downloaded files are empty
- ⚠️ This shouldn't happen - please report as bug
- ➡️ Try "Download All" instead of individual downloads

---

## FAQ

### General Questions

**Q: Do I need to create an account?**
A: No, Core Cartographer is stateless. No accounts or logins required.

**Q: Is my data saved if I refresh the page?**
A: No, refreshing clears all data. Download results before closing.

**Q: Can I save my workspace and come back later?**
A: Not yet. This feature may be added in future versions.

**Q: How much does extraction cost?**
A: Depends on file size and model:
- Small project (5K tokens): ~$0.15
- Medium project (20K tokens): ~$0.60
- Large project (100K tokens): ~$3.00

### File Questions

**Q: What's the maximum file size?**
A: 10MB per file. For larger files, split into sections.

**Q: Can I upload scanned PDFs?**
A: Scanned images won't work. Use OCR to convert to searchable text first.

**Q: How many files can I upload?**
A: No hard limit, but 20+ files may slow down the UI.

**Q: Can I upload files in any language?**
A: Yes, but AI analysis works best with English, German, French, Spanish, Italian, Portuguese.

### Extraction Questions

**Q: How long does extraction take?**
A: 30-90 seconds per category. Multiple categories process sequentially.

**Q: Can I cancel extraction midway?**
A: Yes, click the "Cancel" button in the progress modal.

**Q: What happens if extraction fails?**
A: Error message appears with "Retry" button. No charges for failed extractions.

**Q: Why use categories?**
A: Different document types need different rules. Categories keep them organized.

### Results Questions

**Q: What format are the rules in?**
A: JavaScript objects, compatible with portal-localiser and other tools.

**Q: What format are the guidelines in?**
A: Markdown, readable in any text editor or rendered online.

**Q: Can I edit the results?**
A: Yes, download and edit in your preferred editor.

**Q: Can I re-run extraction on the same files?**
A: Yes, just click "Start Extraction" again. Previous results are overwritten.

### Technical Questions

**Q: What AI model does it use?**
A: Default is Claude Opus 4.5. You can change in Settings.

**Q: Can I run this locally without internet?**
A: No, requires API connection to Anthropic servers.

**Q: Is this open source?**
A: Check the repository for license information.

**Q: Can I integrate this into my TMS?**
A: The backend API can be integrated. See API documentation.

---

## Getting Help

### Support Channels

- **GitHub Issues:** Report bugs and request features
- **Documentation:** Check README and technical docs
- **Logs:** Backend logs provide detailed error information

### Reporting Bugs

When reporting bugs, include:
1. Steps to reproduce
2. Expected vs actual behavior
3. Browser and OS version
4. Screenshots (if applicable)
5. Backend logs (if applicable)

### Feature Requests

We welcome feature requests! Please check existing issues first to avoid duplicates.

---

## Appendix: Output Examples

### Client Rules (JavaScript)

```javascript
const clientRules = {
  terminology: {
    translate: ["user", "settings", "dashboard"],
    doNotTranslate: ["API", "Acme", "OAuth"],
  },
  formatting: {
    dates: "DD/MM/YYYY",
    numbers: "1.234,56",
    currency: "€",
  },
  style: {
    formality: "formal",
    tone: "professional",
  },
};
```

### Guidelines (Markdown)

```markdown
# Acme Corporation - Translation Guidelines

## Overview
This document provides guidelines for translating Acme's technical documentation.

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

## Formatting
- Dates: DD/MM/YYYY format
- Numbers: Use comma for decimals (1,5 not 1.5)
```

---

**Need more help?** Contact support or check the technical documentation.

---

*Core Cartographer v2.0 - Modern, Fast, Reliable* ✨
