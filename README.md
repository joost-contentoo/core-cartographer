# Core Cartographer

An intelligent document analysis tool that extracts **glossaries** and **guidelines** from copy documents using Claude Opus 4.5. Designed for translation and localization workflows.

## Overview

Core Cartographer processes collections of copy documents (e.g., gift cards, game cards, payment cards) and uses LLM analysis to extract:

- **Glossary**: Key terminology, definitions, and translation pairs
- **Guidelines**: Style rules, tone of voice, formatting conventions, and content patterns

The tool organizes outputs by client and document subtype, making it ideal for managing multiple projects with varying document types.

## Features

- **Multi-format support**: Process `.txt`, `.md`, `.docx`, and `.pdf` files
- **Language auto-detection**: Automatically identifies document languages and language pairs
- **Holistic analysis**: Sends all documents in a subfolder to Claude at once for comprehensive pattern extraction
- **Cost estimation**: Shows estimated API costs before processing
- **Interactive review**: Preview extracted content before saving
- **Client organization**: Outputs organized by client and document subtype

## Project Structure

```
core-cartographer/
├── input/                      # Place client documents here
│   └── [client_name]/
│       └── [subtype]/          # e.g., gift_cards, game_cards
│           ├── document1.pdf
│           ├── document2.docx
│           └── ...
├── output/                     # Generated glossaries and guidelines
│   └── [client_name]/
│       └── [subtype]/
│           ├── glossary.md
│           └── guidelines.md
├── templates/                  # Templates for output documents
│   ├── glossary_template.md
│   └── guidelines_template.md
├── instructions/               # Instructions for Claude
│   └── extraction_instructions.md
├── src/                        # Source code
│   └── core_cartographer/
│       ├── __init__.py
│       ├── cli.py              # Interactive CLI
│       ├── extractor.py        # Document extraction logic
│       ├── parser.py           # Document parsing (PDF, DOCX, etc.)
│       ├── cost_estimator.py   # Token counting and cost estimation
│       └── config.py           # Configuration management
├── .env.example                # Example environment variables
├── pyproject.toml              # Python project configuration
└── README.md
```

## Installation

### Prerequisites

- Python 3.11+
- Anthropic API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/core-cartographer.git
   cd core-cartographer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Configure your API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

## Usage

Run the interactive CLI:

```bash
cartographer
```

The menu will guide you through:

1. **Select client** - Choose or create a client folder
2. **Scan documents** - View detected subtypes and document counts
3. **Estimate costs** - See token counts and estimated API costs
4. **Process** - Extract glossaries and guidelines
5. **Review** - Preview results before saving

### Example Workflow

```
$ cartographer

╭──────────────────────────────────────╮
│     Core Cartographer v0.1.0         │
╰──────────────────────────────────────╯

? Select a client: acme_corp

Found 3 document subtypes:
  • gift_cards (12 documents)
  • game_cards (8 documents)
  • payment_cards (15 documents)

? Select subtypes to process: [All]

Estimated costs:
  • Total tokens: ~45,000
  • Estimated cost: $0.68

? Proceed with extraction? Yes

Processing gift_cards...
✓ Glossary extracted (127 terms)
✓ Guidelines extracted

[Preview of glossary.md shown here]

? Save results? Yes
✓ Saved to output/acme_corp/gift_cards/
```

## Configuration

### Environment Variables (.env)

```bash
ANTHROPIC_API_KEY=sk-ant-...    # Required: Your Anthropic API key
INPUT_DIR=./input               # Optional: Custom input directory
OUTPUT_DIR=./output             # Optional: Custom output directory
MODEL=claude-opus-4-5-20251101  # Optional: Model to use
```

## Templates

The `templates/` folder contains the structure templates for generated documents:

- **glossary_template.md**: Structure for the glossary output
- **guidelines_template.md**: Structure for the guidelines output

Edit these templates to customize the output format for your needs.

## Instructions

The `instructions/extraction_instructions.md` file contains detailed instructions for Claude on how to extract and format the glossary and guidelines. This ensures consistent extraction across runs.

## Supported Document Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain text | `.txt` | Direct text processing |
| Markdown | `.md` | Preserves formatting |
| Word | `.docx` | Text extraction, basic formatting |
| PDF | `.pdf` | Text extraction (OCR not included) |

## Best Practices

1. **Organize by subtype**: Group similar documents in subfolders for more coherent glossaries
2. **Use clean documents**: Ensure PDFs are text-based (not scanned images) for best results
3. **Review before saving**: Always review the preview to catch any extraction issues
4. **Keep templates updated**: Refine templates based on output quality

## Limitations

- PDF OCR is not included; scanned documents need pre-processing
- Very large document sets may need to be split to stay within context limits
- Language detection works best with substantial text content

## License

ISC

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
