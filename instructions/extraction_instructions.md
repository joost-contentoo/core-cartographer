# Extraction Instructions

> **Note**: As of v2.0, extraction instructions are built dynamically by the prompt builder in `src/core_cartographer/extractor.py`.
>
> For the archived v1 instructions, see `archive/extraction_instructions_v1.md`.

## How Extraction Works

The extractor builds a comprehensive prompt that includes:

1. **Mission & Context**: Clear goal statement and output descriptions
2. **Output Specifications**: Annotated examples from `templates/`
3. **Extraction Rules**: What to look for with evidence thresholds
4. **Content Focus**: Instruction to focus on copy, ignore metadata
5. **Document Structure**: Labeled by language, pair, and subtype
6. **Response Format**: Clear structure for Claude's response

## Template Files

The prompt references these templates:

- `templates/client_rules_example.js` - Annotated validation config structure
- `templates/guidelines_example.md` - Human-readable style guide structure

## Customization

To customize extraction behavior:

1. Edit the template files to change output structure/examples
2. Modify `extractor.py` → `_build_*_section()` functions for prompt changes
3. Adjust evidence thresholds in `_build_extraction_rules_section()`
