# Core Cartographer - Manual Test Matrix

**Version:** 1.0
**Date:** December 18, 2024
**Testing Target:** Next.js + FastAPI Migration

---

## Test Environment Setup

### Prerequisites
- [ ] Backend running on `http://localhost:8000`
- [ ] Frontend running on `http://localhost:3000`
- [ ] Anthropic API key configured in `.env`
- [ ] Sample test files available (PDF, DOCX, TXT)

### Test Data Files
Prepare the following test files:
1. **Single English PDF** (e.g., `test_en.pdf`)
2. **Single German PDF** (e.g., `test_de.pdf`)
3. **Translation pair** (e.g., `guide_en.pdf`, `guide_de.pdf`)
4. **Large file** (>5MB to test limits)
5. **Unsupported format** (e.g., `.xlsx`)
6. **Corrupt file** (malformed PDF)

---

## 1. File Upload & Management

### TC-001: Basic File Upload
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open app at `/workspace` | Page loads, FileUploadZone visible | ⏳ | |
| 2 | Click "Click to upload" | File picker opens | ⏳ | |
| 3 | Select `test_en.pdf` | File uploads, appears in FileList | ⏳ | |
| 4 | Verify file metadata | Shows filename, language, tokens, "general" subtype | ⏳ | |

### TC-002: Drag & Drop Upload
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Drag `test_de.pdf` over upload zone | Zone highlights with primary color | ⏳ | |
| 2 | Drop file | File uploads successfully | ⏳ | |
| 3 | Verify in FileList | File appears with correct metadata | ⏳ | |

### TC-003: Multiple File Upload
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Select 3 files simultaneously | All 3 files upload | ⏳ | |
| 2 | Check FileList | All 3 files visible with correct data | ⏳ | |

### TC-004: File Deletion
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload 2 files | Both appear in list | ⏳ | |
| 2 | Click trash icon on first file | Confirmation dialog appears | ⏳ | |
| 3 | Click "Delete" | File removed from list | ⏳ | |
| 4 | Click trash icon on second file | Confirmation dialog appears | ⏳ | |
| 5 | Click "Cancel" | File remains in list | ⏳ | |

### TC-005: File Deletion via Keyboard
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file and select it | File highlighted | ⏳ | |
| 2 | Press **Delete** key | File immediately removed | ⏳ | |
| 3 | Verify FileList | File no longer present | ⏳ | |

### TC-006: Unsupported File Type
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Try to upload `.xlsx` file | Error banner appears | ⏳ | |
| 2 | Check error message | Shows "Unsupported file type" | ⏳ | |
| 3 | Click retry button | File picker opens again | ⏳ | |

---

## 2. Language Detection & Pairing

### TC-007: Auto-Detect Single File
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload English PDF | Default language is "en" | ⏳ | |
| 2 | Click "Auto-Detect Languages" | Button becomes disabled during process | ⏳ | |
| 3 | Wait for completion | Language detected as "EN" | ⏳ | |

### TC-008: Auto-Detect Translation Pair
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload `guide_en.pdf` and `guide_de.pdf` | Both appear in list | ⏳ | |
| 2 | Click "Auto-Detect Languages" | Process runs | ⏳ | |
| 3 | Check languages | EN and DE detected | ⏳ | |
| 4 | Check pair IDs | Both files show same "Pair #1" badge | ⏳ | |

### TC-009: Manual Language Override
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file with wrong language | Shows incorrect language | ⏳ | |
| 2 | Change language in FileItem (if editable) | Language updates | ⏳ | |
| 3 | Verify in preview | Updated language displayed | ⏳ | |

---

## 3. Subtype Management

### TC-010: Add Custom Subtype
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Scroll to "Categories" section | SubtypeManager visible with "general" | ⏳ | |
| 2 | Type "technical" in input | Input accepts text | ⏳ | |
| 3 | Click "Add" button | "technical" badge appears | ⏳ | |
| 4 | Check FileList dropdowns | "technical" available in all dropdowns | ⏳ | |

### TC-011: Remove Subtype
**Priority:** P1 (High)

| Step | Action | expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Add "marketing" subtype | Appears in list | ⏳ | |
| 2 | Click "✕" on "marketing" badge | Badge removed | ⏳ | |
| 3 | Check FileList dropdowns | "marketing" no longer in dropdowns | ⏳ | |

### TC-012: Cannot Remove Last Subtype
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Try to remove "general" (only subtype) | Remove button disabled or warning shown | ⏳ | |

### TC-013: Assign Subtype to File
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file (defaults to "general") | File shows "general" | ⏳ | |
| 2 | Add "legal" subtype | "legal" available | ⏳ | |
| 3 | Change file's subtype to "legal" | Dropdown updates | ⏳ | |
| 4 | Verify change persisted | File still shows "legal" | ⏳ | |

---

## 4. Settings Panel

### TC-014: Open Settings Panel
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Click "Settings" button | Modal dialog opens | ⏳ | |
| 2 | Verify default settings | Batch mode, Opus 4.5, Debug off | ⏳ | |

### TC-015: Change Processing Mode
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open Settings | Dialog opens | ⏳ | |
| 2 | Select "Individual" radio button | Selection changes | ⏳ | |
| 3 | Click "Save" | Dialog closes | ⏳ | |
| 4 | Reopen Settings | "Individual" still selected | ⏳ | |

### TC-016: Change Model
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open Settings | Dialog opens | ⏳ | |
| 2 | Open model dropdown | Shows all 3 models | ⏳ | |
| 3 | Select "Claude Sonnet 4" | Selection updates | ⏳ | |
| 4 | Save and verify | Model persisted | ⏳ | |

### TC-017: Enable Debug Mode
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open Settings | Dialog opens | ⏳ | |
| 2 | Check "Debug Mode" checkbox | Checkbox toggles | ⏳ | |
| 3 | Save settings | Dialog closes | ⏳ | |
| 4 | Run extraction | Prompts saved to disk (backend verification) | ⏳ | |

### TC-018: Cancel Settings Changes
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open Settings | Dialog opens with defaults | ⏳ | |
| 2 | Change to "Individual" mode | Selection changes | ⏳ | |
| 3 | Click "Cancel" | Dialog closes | ⏳ | |
| 4 | Reopen Settings | Still shows original "Batch" mode | ⏳ | |

---

## 5. Extraction Flow

### TC-019: Basic Extraction - Single Category
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Enter client name "Test Client" | Input accepts text | ⏳ | |
| 2 | Upload 1 file | File appears | ⏳ | |
| 3 | Keep default "general" category | No changes needed | ⏳ | |
| 4 | Click "Start Extraction" | Progress modal opens | ⏳ | |
| 5 | Wait for completion | Shows "Processing general..." | ⏳ | |
| 6 | Verify progress indicators | Checkmark appears on "general" | ⏳ | |
| 7 | Wait for results | ResultsDialog opens automatically | ⏳ | |
| 8 | Verify results shown | Shows 1 category with rules & guidelines | ⏳ | |

### TC-020: Extraction - Multiple Categories
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload 3 files | All appear in list | ⏳ | |
| 2 | Add "technical" and "legal" subtypes | Both added | ⏳ | |
| 3 | Assign 1 file to each subtype | File subtypes updated | ⏳ | |
| 4 | Start extraction | Progress modal shows 3 categories | ⏳ | |
| 5 | Watch progress | Each category processed sequentially | ⏳ | |
| 6 | Verify completion | All 3 categories show checkmarks | ⏳ | |
| 7 | Check ResultsDialog | Shows all 3 categories | ⏳ | |

### TC-021: Extraction via Keyboard Shortcut
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Enter client name and upload files | Ready to extract | ⏳ | |
| 2 | Press **Enter** key | Extraction starts immediately | ⏳ | |
| 3 | Verify progress modal opens | Modal visible | ⏳ | |

### TC-022: Cannot Extract Without Client Name
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload files | Files present | ⏳ | |
| 2 | Leave client name empty | Input empty | ⏳ | |
| 3 | Try to click "Start Extraction" | Button disabled | ⏳ | |

### TC-023: Cannot Extract Without Files
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Enter client name | Input filled | ⏳ | |
| 2 | Don't upload any files | FileList empty | ⏳ | |
| 3 | Try to click "Start Extraction" | Button disabled | ⏳ | |

### TC-024: Cancel Extraction
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Start extraction with 2+ categories | Progress modal opens | ⏳ | |
| 2 | Click "Cancel" button | Extraction stops | ⏳ | |
| 3 | Verify modal closes | Modal disappears | ⏳ | |
| 4 | Check no results appear | No ResultsDialog | ⏳ | |

### TC-025: Extraction Error Handling
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Stop backend or remove API key | Backend unavailable | ⏳ | |
| 2 | Try extraction | Error banner appears | ⏳ | |
| 3 | Check error message | Shows meaningful error | ⏳ | |
| 4 | Click "Retry" button | Retry attempt made | ⏳ | |

---

## 6. Results Display

### TC-026: Results Dialog - Single Category
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Complete extraction with 1 category | ResultsDialog opens | ⏳ | |
| 2 | Verify summary stats | Shows 1 category, token count | ⏳ | |
| 3 | Check tabs | "Client Rules" and "Guidelines" tabs present | ⏳ | |
| 4 | Click "Client Rules" tab | Shows JavaScript with syntax highlighting | ⏳ | |
| 5 | Click "Guidelines" tab | Shows rendered markdown | ⏳ | |

### TC-027: Results Dialog - Multiple Categories
**Priority:** P0 (Critical)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Complete extraction with 3 categories | ResultsDialog opens | ⏳ | |
| 2 | Verify category badges shown | 3 badges: "general", "technical", "legal" | ⏳ | |
| 3 | Click "technical" badge | Content switches to technical results | ⏳ | |
| 4 | Verify tabs update | Shows technical rules & guidelines | ⏳ | |
| 5 | Switch to "legal" | Content updates again | ⏳ | |

### TC-028: Download Single File
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open ResultsDialog | Dialog visible | ⏳ | |
| 2 | Click "Download" on Client Rules tab | File downloads as `general_client_rules.js` | ⏳ | |
| 3 | Open downloaded file | Valid JavaScript content | ⏳ | |
| 4 | Click "Download" on Guidelines tab | File downloads as `general_guidelines.md` | ⏳ | |
| 5 | Open downloaded file | Valid Markdown content | ⏳ | |

### TC-029: Download All Files
**Priority:** P1 (High)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open ResultsDialog with 3 categories | Dialog visible | ⏳ | |
| 2 | Click "Download All" button | 6 files download (3 × 2) | ⏳ | |
| 3 | Verify filenames | All 6 files have correct names | ⏳ | |
| 4 | Check file contents | All contain valid content | ⏳ | |

### TC-030: Close and Reopen Results
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open ResultsDialog | Dialog visible | ⏳ | |
| 2 | Close dialog | Dialog disappears | ⏳ | |
| 3 | Click "View Results" button | Dialog reopens with same data | ⏳ | |
| 4 | Verify content preserved | All results still visible | ⏳ | |

---

## 7. Cost Estimation

### TC-031: Cost Display Updates
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Start with empty workspace | Cost shows "$0.00" | ⏳ | |
| 2 | Upload 1 small file (1K tokens) | Cost updates | ⏳ | |
| 3 | Upload 1 large file (10K tokens) | Cost increases | ⏳ | |
| 4 | Remove large file | Cost decreases | ⏳ | |

---

## 8. File Preview

### TC-032: Preview Selected File
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file | File appears in list | ⏳ | |
| 2 | Click file in list | File highlighted, preview appears | ⏳ | |
| 3 | Verify preview content | Shows first 500 chars | ⏳ | |
| 4 | Check metadata | Shows language, subtype, tokens, pair ID | ⏳ | |

### TC-033: Empty Preview State
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file but don't select | Preview shows empty state | ⏳ | |
| 2 | Verify empty state text | Shows helpful message | ⏳ | |

---

## 9. Empty States

### TC-034: FileList Empty State
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Open app with no files | FileList shows empty state | ⏳ | |
| 2 | Verify icon and text | Guidance about uploading files | ⏳ | |
| 3 | Watch animation | Fade-in animation plays | ⏳ | |

---

## 10. Animations & Polish

### TC-035: Error Banner Animation
**Priority:** P3 (Low)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Trigger error (e.g., unsupported file) | Error banner slides in from top | ⏳ | |
| 2 | Verify animation smoothness | No jank, 300ms duration | ⏳ | |

### TC-036: Results Card Animation
**Priority:** P3 (Low)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Complete extraction | Success card slides up from bottom | ⏳ | |
| 2 | Watch sparkle emoji | Zooms in with delay | ⏳ | |

### TC-037: File Selection Animation
**Priority:** P3 (Low)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Click file in list | File scales slightly and shows shadow | ⏳ | |
| 2 | Click another file | Previous deselects, new one animates | ⏳ | |

---

## 11. Edge Cases & Stress Tests

### TC-038: Very Large File
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file >10MB | Either uploads or shows size limit error | ⏳ | |

### TC-039: Many Files
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload 20+ files | All upload successfully | ⏳ | |
| 2 | Verify UI performance | No lag in scrolling/interaction | ⏳ | |

### TC-040: Special Characters in Filenames
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Upload file with special chars (e.g., `test#file@2024.pdf`) | Uploads successfully | ⏳ | |
| 2 | Verify display | Filename shows correctly | ⏳ | |
| 3 | Download results | Filename handled correctly | ⏳ | |

### TC-041: Long Client Name
**Priority:** P3 (Low)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Enter very long client name (100+ chars) | Input accepts text | ⏳ | |
| 2 | Verify UI doesn't break | Text truncates or wraps gracefully | ⏳ | |

### TC-042: Network Interruption
**Priority:** P2 (Medium)

| Step | Action | Expected Result | Status | Notes |
|------|--------|----------------|--------|-------|
| 1 | Start extraction | Progress begins | ⏳ | |
| 2 | Stop backend mid-extraction | Error shown, retry available | ⏳ | |
| 3 | Restart backend and retry | Extraction resumes | ⏳ | |

---

## 12. Browser Compatibility

### TC-043: Chrome
**Priority:** P0 (Critical)

| Test | Status | Notes |
|------|--------|-------|
| All core functionality works | ⏳ | |

### TC-044: Firefox
**Priority:** P1 (High)

| Test | Status | Notes |
|------|--------|-------|
| All core functionality works | ⏳ | |

### TC-045: Safari
**Priority:** P1 (High)

| Test | Status | Notes |
|------|--------|-------|
| All core functionality works | ⏳ | |

---

## Test Summary Template

```
Total Tests: 45
Passed: 0
Failed: 0
Blocked: 0
Not Tested: 45

Critical Issues: 0
High Priority Issues: 0
Medium Priority Issues: 0
Low Priority Issues: 0
```

---

## Bug Report Template

```markdown
### Bug ID: BUG-XXX
**Severity:** Critical/High/Medium/Low
**Priority:** P0/P1/P2/P3
**Test Case:** TC-XXX

**Description:**
[What happened]

**Steps to Reproduce:**
1.
2.
3.

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Environment:**
- Browser: Chrome 120
- OS: macOS 14.2
- Backend: commit abc123

**Screenshots:**
[If applicable]
```

---

**Status:** Ready for manual testing
**Next Step:** Execute test cases and document results
