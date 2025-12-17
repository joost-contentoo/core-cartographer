# Core Cartographer

Extract **validation rules** and **localization guidelines** from copy documents using Claude Opus 4.5.

## What It Does

Core Cartographer analyzes collections of localized copy (e.g., product pages, marketing content) and reverse-engineers the implicit rules and style patterns into two outputs:

1. **`client_rules.js`** - Machine-readable validation config for automated content checking
2. **`guidelines.md`** - Human-readable localization guidance for writers and translators

This enables you to:
- Codify tribal knowledge from existing high-quality content
- Ensure consistency across new content with automated validation
- Onboard new translators with comprehensive style guides
- Maintain separate rules/guidelines per client and content type

## Example Output

### Client Rules (JavaScript)
```javascript
const client_rules = {
  client: "acme",
  locale: "de",

  forbidden_words: ["Sie", "Ihnen", "Ihr"],  // Using informal "du"

  terminology: [
    { en: "gift card", de: "Gutschein", context: "product term" },
    { en: "redeem", de: "einlösen", context: "action verb" }
  ],

  patterns: {
    currency: {
      invalid_patterns: ["\\d+€", "€\\d+"],
      valid_format: "X €",
      fix_message: "Use: number + space + euro sign"
    }
  }
};
```

### Guidelines (Markdown)
```markdown
# ACME German Localization Guidelines

## Brand Voice
ACME speaks to German customers as a knowledgeable friend...

## Writing Style
Use informal "du" throughout. Never mix with "Sie"...
```

## Project Structure

```
core-cartographer/
├── input/                          # Client documents to analyze
│   └── [client_name]/
│       └── [subtype]/              # e.g., gift_cards, payment_cards
│           ├── document1.pdf
│           └── document2.docx
├── output/                         # Generated rules and guidelines
│   └── [client_name]/
│       └── [subtype]/
│           ├── client_rules.js     # Machine-readable validation config
│           └── guidelines.md       # Human-readable guidance
├── templates/                      # Example outputs for Claude to follow
│   ├── client_rules_example.js
│   └── guidelines_example.md
├── instructions/                   # Extraction instructions for Claude
│   └── extraction_instructions.md
└── src/core_cartographer/          # Python source code
```

## Installation

### Prerequisites
- Python 3.11+
- Anthropic API key

### Setup

```bash
# Clone and enter directory
git clone https://github.com/yourusername/core-cartographer.git
cd core-cartographer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install
pip install -e .

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Usage

```bash
cartographer
```

The interactive CLI guides you through:

1. **Select client** - Choose from available client folders
2. **Select subtypes** - Process all or specific document types
3. **Review costs** - See estimated token usage and API costs
4. **Extract** - Claude analyzes documents and generates outputs
5. **Preview & confirm** - Review before saving

### Example Session

```
╭──────────────────────────────────────────────────────────────╮
│ Core Cartographer v0.1.0                                     │
│ Extract validation rules and localization guidelines         │
╰──────────────────────────────────────────────────────────────╯

? What would you like to do? Extract rules & guidelines
? Select a client: dundle

         Documents Found
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┓
┃ Subtype      ┃ Documents ┃ Tokens ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━┩
│ gift_cards   │        12 │  8.2k  │
│ game_cards   │         8 │  5.1k  │
│ payment_cards│        15 │  9.7k  │
└──────────────┴───────────┴────────┘

? Which subtypes to process? [All subtypes]

Estimated Cost:
  Input tokens:  38.0k
  Output tokens: ~19.0k
  Estimated cost: $2.0250

? Proceed with extraction? Yes

Processing gift_cards...
✓ Saved: output/dundle/gift_cards/client_rules.js
✓ Saved: output/dundle/gift_cards/guidelines.md
```

## Input Document Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain text | `.txt` | Direct processing |
| Markdown | `.md` | Preserves structure |
| Word | `.docx` | Text extraction |
| PDF | `.pdf` | Text extraction (no OCR) |

## Customizing Extraction

### Examples (templates/)

The `templates/` folder contains example outputs that Claude uses as reference:
- `client_rules_example.js` - Shows the expected JavaScript structure
- `guidelines_example.md` - Shows the expected Markdown structure

Edit these to match your preferred output format.

### Instructions (instructions/)

`extraction_instructions.md` tells Claude how to analyze documents and what to extract. Customize this to:
- Add domain-specific extraction rules
- Adjust the level of detail
- Add new rule categories

## How It Works

1. **Document Collection**: All documents in a subtype folder are collected
2. **Holistic Analysis**: Documents are sent to Claude Opus 4.5 together for comprehensive pattern recognition
3. **Dual Extraction**: Claude generates both machine-readable rules and human-readable guidelines
4. **Review Flow**: Preview outputs before committing to files

### Why Holistic Analysis?

Claude Opus 4.5's large context window (200k+ tokens) allows analyzing all documents at once. This produces:
- More consistent terminology extraction
- Better pattern recognition across documents
- Identification of inconsistencies in source content

## Configuration

### Environment Variables (.env)

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required
INPUT_DIR=./input               # Optional (default: ./input)
OUTPUT_DIR=./output             # Optional (default: ./output)
MODEL=claude-opus-4-5-20251101  # Optional (default: opus 4.5)
```

## Integration with Code Checker

The `client_rules.js` output is designed to feed into a separate Code Checker tool that validates new content against the extracted rules. The rules config includes:

- `forbidden_words` - Terms that trigger validation errors
- `terminology` - Required translations with context
- `patterns` - Regex-based formatting rules
- `lengths` - Character/word limits per content type
- `keywords` - SEO placement requirements
- `structure` - Required document elements

## License

ISC
