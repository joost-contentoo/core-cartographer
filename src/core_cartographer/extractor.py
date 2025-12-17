"""Core extraction logic using Claude API.

This module handles the extraction of validation rules and localization
guidelines from document collections using Claude's API.
"""

import re
from datetime import datetime
from pathlib import Path

import anthropic

from .config import Settings
from .cost_estimator import count_tokens
from .exceptions import ClientNotFoundError, ExtractionError, ResponseParsingError
from .file_utils import detect_language, extract_language_from_filename
from .logging_config import get_logger
from .models import Document, DocumentPair, DocumentSet, ExtractionResult
from .parser import get_supported_files, parse_document

logger = get_logger(__name__)

# Maximum input tokens before warning/splitting
MAX_INPUT_TOKENS = 150_000


# =============================================================================
# PROMPT BUILDING
# =============================================================================


def _build_mission_section() -> str:
    """Build the mission and context section of the prompt."""
    return """You are extracting localization rules from copy documents.

YOUR OUTPUTS:
1. client_rules.js - Machine-readable validation config (consumed by automated Code Checker)
2. guidelines.md - Human-readable style guide (used by LLMs and humans to write new content in the client's voice)

IMPORTANT CONTEXT:
• The client_rules.js powers automated validation - rules must be precise and evidenced
• The guidelines.md will be used by an LLM to generate new content - it must capture tone, style, and nuance that can't be codified in rules
• Documents may contain metadata, navigation, or internal notes - FOCUS ONLY ON ACTUAL COPY (headlines, paragraphs, FAQs, CTAs, benefit lists)"""


def _build_output_spec_section(settings: Settings) -> str:
    """Build the output specification section with annotated examples."""
    # Load the annotated example templates
    client_rules_example = settings.client_rules_example_path.read_text(encoding="utf-8")
    guidelines_example_path = settings.guidelines_example_path

    # Read guidelines structure (first ~100 lines for structure overview)
    guidelines_content = guidelines_example_path.read_text(encoding="utf-8")
    guidelines_lines = guidelines_content.split("\n")

    # Extract just the section headers for overview
    section_headers = [
        line for line in guidelines_lines
        if line.startswith("## ") and not line.startswith("### ")
    ][:12]  # First 12 top-level sections

    guidelines_structure = "\n".join(section_headers)

    return f"""
═══════════════════════════════════════════════════════════════════════════════
OUTPUT 1: client_rules.js
═══════════════════════════════════════════════════════════════════════════════

Follow this exact structure. Each section has comments explaining what to extract and evidence requirements:

```javascript
{client_rules_example}
```

═══════════════════════════════════════════════════════════════════════════════
OUTPUT 2: guidelines.md
═══════════════════════════════════════════════════════════════════════════════

Create a comprehensive style guide with these REQUIRED sections:

{guidelines_structure}

GUIDELINES PRINCIPLES:
• Show, don't just tell - include BEFORE/AFTER transformation examples
• Be specific - "friendly" is vague, "use du, never Sie" is actionable
• Explain WHY - the reasoning helps LLMs generalize to new situations
• Cross-reference client_rules.js for hard constraints
• Each section: 300-500 words max, prioritize examples over prose
• Total target: 4,000-6,000 words"""


def _build_extraction_rules_section(has_pairs: bool) -> str:
    """Build the extraction rules section with evidence thresholds."""
    terminology_note = """
✓ TERMINOLOGY (source+target pairs available)
  • Terms translated consistently 3+ times
  • Include 'context' when same source word has multiple target translations
  Evidence needed: 3+ consistent translation occurrences"""

    if not has_pairs:
        terminology_note = """
⚠ TERMINOLOGY (no source+target pairs available)
  • Cannot extract terminology mappings without paired documents
  • Leave terminology array empty or minimal
  • Focus on other extraction areas instead"""

    return f"""
WHAT TO EXTRACT:

✓ FORBIDDEN_WORDS
  • Formal address forms when informal is used throughout
  • Competitor names never mentioned
  • Negative/pressure language consistently absent
  Evidence needed: Conspicuous absence across ALL documents
{terminology_note}

✓ PATTERNS
  • Currency formatting (€5 vs 5 € vs 5,00 €)
  • Date formats (DD.MM.YYYY vs other)
  • List closure phrases ("Fertig!", "Das war's!")
  • Number formatting (1.000 vs 1,000)
  Evidence needed: 80%+ consistency across occurrences

✓ LENGTHS
  • Meta titles/descriptions (observe actual limits)
  • Body paragraph lengths (if consistent limits visible)
  Evidence needed: Observable limits in document structure

✓ STRUCTURE
  • Tags/sections present in every document
  Evidence needed: 100% presence across documents

QUALITY THRESHOLD:
• Only include rules with EVIDENCE from documents
• When uncertain, OMIT rather than guess
• Patterns must be CONSISTENT, not one-offs
• For guidelines: capture tone and nuance even when not codifiable as rules"""


def _build_content_focus_section() -> str:
    """Build the content focus instruction section."""
    return """
⚠️ FOCUS ON COPY ONLY

Documents may contain elements to IGNORE:
• Internal notes, metadata, version history
• Navigation elements, breadcrumbs
• Formatting artifacts, template markers
• File paths, URLs (unless part of instructions)

Extract rules ONLY from actual copy:
• Headlines (H1, H2)
• Body paragraphs and intro text
• FAQ questions and answers
• Benefit/feature lists
• CTAs and microcopy
• Instructional steps"""


def _format_document(doc: Document, label: str) -> str:
    """Format a single document for the prompt."""
    return f"""
──── {label}: {doc.filename} ────
{doc.content}"""


def _format_pair(pair: DocumentPair) -> str:
    """Format a document pair for the prompt."""
    return f"""
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
PAIR {pair.pair_id}
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
{_format_document(pair.source, f"SOURCE [{pair.source.language}]")}
{_format_document(pair.target, f"TARGET [{pair.target.language}]")}"""


def _build_documents_section(
    client_name: str,
    document_sets: list[DocumentSet],
) -> str:
    """Build the documents section with proper labeling."""
    subtype_names = [ds.subtype for ds in document_sets]
    total_docs = sum(len(ds.documents) for ds in document_sets)

    header = f"""
══════════════════════════════════════════════════════════════════════════════
EXTRACTION TASK
══════════════════════════════════════════════════════════════════════════════

Client: {client_name}
Subtypes: {', '.join(subtype_names)}
Total Documents: {total_docs}"""

    sections = [header]

    for doc_set in document_sets:
        subtype_header = f"""
┌──────────────────────────────────────────────────────────────────────────────┐
│ SUBTYPE: {doc_set.subtype:<68} │
│ LANGUAGE SITUATION: {doc_set.language_situation:<56} │
│ DOCUMENTS: {len(doc_set.documents):<65} │
└──────────────────────────────────────────────────────────────────────────────┘"""
        sections.append(subtype_header)

        # Add paired documents first
        pairs = doc_set.paired_documents
        if pairs:
            for pair in pairs:
                sections.append(_format_pair(pair))

        # Add unpaired documents
        unpaired = doc_set.unpaired_documents
        if unpaired:
            sections.append("""
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈
UNPAIRED DOCUMENTS
(Extract patterns/forbidden words only - skip terminology without pairs)
┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈""")
            for doc in unpaired:
                label = f"[{doc.language}]" if doc.language else "[UNKNOWN]"
                sections.append(_format_document(doc, label))

    return "\n".join(sections)


def _build_response_format_section(document_sets: list[DocumentSet]) -> str:
    """Build the response format instruction section."""
    subtype_names = [ds.subtype for ds in document_sets]

    if len(document_sets) == 1:
        return f"""
═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════════════════════════════════════════════

Respond with:

## SUBTYPE: {subtype_names[0]}

### CLIENT_RULES

```javascript
[Complete client_rules.js following the annotated template above]
```

### GUIDELINES

[Complete guidelines.md following the structure above - NO code fence]"""

    return f"""
═══════════════════════════════════════════════════════════════════════════════
RESPONSE FORMAT
═══════════════════════════════════════════════════════════════════════════════

Respond with SEPARATE outputs for EACH subtype:

## SUBTYPE: [subtype_name]

### CLIENT_RULES

```javascript
[Complete client_rules.js following the annotated template above]
```

### GUIDELINES

[Complete guidelines.md following the structure above - NO code fence]

---

(Repeat for each subtype: {', '.join(subtype_names)})"""


def build_extraction_prompt(
    client_name: str,
    document_sets: list[DocumentSet],
    settings: Settings,
) -> str:
    """Build the complete extraction prompt.

    Args:
        client_name: Name of the client/brand.
        document_sets: List of document sets to process.
        settings: Application settings.

    Returns:
        Complete prompt string for Claude.
    """
    # Determine if we have any paired documents
    has_pairs = any(
        len(ds.paired_documents) > 0
        for ds in document_sets
    )

    sections = [
        _build_mission_section(),
        _build_output_spec_section(settings),
        _build_extraction_rules_section(has_pairs),
        _build_content_focus_section(),
        _build_documents_section(client_name, document_sets),
        _build_response_format_section(document_sets),
    ]

    return "\n\n".join(sections)


# =============================================================================
# RESPONSE PARSING
# =============================================================================


def _parse_response(response_text: str) -> tuple[str, str]:
    """Parse the response to extract client_rules and guidelines sections."""
    client_rules = ""
    guidelines = ""

    # Extract CLIENT_RULES section (JavaScript code block)
    client_rules_match = re.search(
        r"### CLIENT_RULES\s*```javascript\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not client_rules_match:
        # Try alternate format without ### prefix
        client_rules_match = re.search(
            r"## CLIENT_RULES\s*```javascript\s*(.*?)```",
            response_text,
            re.DOTALL | re.IGNORECASE,
        )
    if client_rules_match:
        client_rules = client_rules_match.group(1).strip()

    # Extract GUIDELINES section (everything after ### GUIDELINES or ## GUIDELINES)
    guidelines_match = re.search(
        r"###? GUIDELINES\s*(.*?)(?=\n##[# ]|$)",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )
    if guidelines_match:
        guidelines = guidelines_match.group(1).strip()
    else:
        # Fallback: take everything after GUIDELINES header
        if "GUIDELINES" in response_text.upper():
            parts = re.split(r"###? GUIDELINES", response_text, flags=re.IGNORECASE)
            if len(parts) > 1:
                guidelines = parts[1].strip()

    return client_rules, guidelines


def _parse_batch_response(
    response_text: str,
    document_sets: list[DocumentSet],
) -> dict[str, ExtractionResult]:
    """Parse batch response to extract results for each subtype."""
    results = {}

    for doc_set in document_sets:
        subtype = doc_set.subtype

        # Extract section for this subtype
        # Pattern: ## SUBTYPE: {name} ... (until next ## SUBTYPE: or end)
        pattern = rf"## SUBTYPE:\s*{re.escape(subtype)}\s*(.*?)(?=\n## SUBTYPE:|$)"
        match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)

        if not match:
            logger.warning(f"No section found for subtype: {subtype}")
            results[subtype] = ExtractionResult(
                client_rules="",
                guidelines="",
                input_tokens=0,
                output_tokens=0,
            )
            continue

        subtype_content = match.group(1)

        # Extract CLIENT_RULES
        client_rules = ""
        rules_match = re.search(
            r"### CLIENT_RULES\s*```javascript\s*(.*?)```",
            subtype_content,
            re.DOTALL | re.IGNORECASE,
        )
        if rules_match:
            client_rules = rules_match.group(1).strip()

        # Extract GUIDELINES
        guidelines = ""
        guidelines_match = re.search(
            r"### GUIDELINES\s*(.*?)(?=\n### [A-Z]|\n## SUBTYPE:|$)",
            subtype_content,
            re.DOTALL | re.IGNORECASE,
        )
        if guidelines_match:
            guidelines = guidelines_match.group(1).strip()
        else:
            # Fallback: take everything after ### GUIDELINES
            if "### GUIDELINES" in subtype_content.upper():
                parts = re.split(r"### GUIDELINES", subtype_content, flags=re.IGNORECASE)
                if len(parts) > 1:
                    guidelines = parts[1].strip()

        results[subtype] = ExtractionResult(
            client_rules=client_rules,
            guidelines=guidelines,
            input_tokens=0,  # Will be set by caller
            output_tokens=0,  # Will be set by caller
        )

        logger.debug(
            f"Parsed subtype {subtype}: {len(client_rules)} chars rules, "
            f"{len(guidelines)} chars guidelines"
        )

    return results


# =============================================================================
# EXTRACTION FUNCTIONS
# =============================================================================


def extract_rules_and_guidelines(
    settings: Settings,
    document_set: DocumentSet,
) -> ExtractionResult:
    """Extract client rules and guidelines from a single document set.

    Args:
        settings: Application settings.
        document_set: The documents to process.

    Returns:
        ExtractionResult containing the client rules (JS) and guidelines (MD).

    Raises:
        ExtractionError: If the Claude API call fails.
        ResponseParsingError: If the response cannot be parsed.
    """
    logger.info(
        f"Starting extraction for {document_set.client_name}/{document_set.subtype}"
    )

    # Build the prompt
    prompt = build_extraction_prompt(
        client_name=document_set.client_name,
        document_sets=[document_set],
        settings=settings,
    )

    # Handle debug mode: save prompt instead of calling API
    if settings.debug_mode:
        logger.info("Debug mode enabled - saving prompt instead of calling API")
        debug_path = _save_debug_prompt(settings, document_set, prompt)
        logger.info(f"Prompt saved to {debug_path}")

        return ExtractionResult(
            client_rules="// Debug mode - no API call made",
            guidelines="# Debug mode - no API call made",
            input_tokens=count_tokens(prompt),
            output_tokens=0,
        )

    # Make API call
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        logger.debug(f"Calling Claude API with model: {settings.model}")
        response = client.messages.create(
            model=settings.model,
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}],
        )
        logger.debug(
            f"API response received: {response.usage.input_tokens} input, "
            f"{response.usage.output_tokens} output tokens"
        )
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        raise ExtractionError(
            f"Claude API error: {e}",
            subtype=document_set.subtype,
            original_error=e,
        )

    # Parse response
    response_text = response.content[0].text

    try:
        client_rules, guidelines = _parse_response(response_text)
    except Exception as e:
        logger.error(f"Failed to parse response: {e}")
        raise ResponseParsingError(
            f"Failed to parse Claude response: {e}",
            subtype=document_set.subtype,
            original_error=e,
        )

    if not client_rules:
        logger.warning("No client rules found in response")
    if not guidelines:
        logger.warning("No guidelines found in response")

    logger.info(
        f"Extraction complete: {len(client_rules)} chars rules, "
        f"{len(guidelines)} chars guidelines"
    )

    return ExtractionResult(
        client_rules=client_rules,
        guidelines=guidelines,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def extract_rules_and_guidelines_batch(
    settings: Settings,
    document_sets: list[DocumentSet],
) -> dict[str, ExtractionResult]:
    """Extract client rules and guidelines from multiple document sets in one API call.

    This processes all subtypes together, allowing Claude to identify common patterns
    and shared rules across subtypes while still producing separate outputs for each.

    Args:
        settings: Application settings.
        document_sets: List of document sets to process together.

    Returns:
        Dictionary mapping subtype name to ExtractionResult.

    Raises:
        ExtractionError: If the Claude API call fails.
        ResponseParsingError: If the response cannot be parsed.
    """
    if not document_sets:
        return {}

    client_name = document_sets[0].client_name
    logger.info(
        f"Starting batch extraction for {client_name} with {len(document_sets)} subtypes"
    )

    # Build the unified prompt
    prompt = build_extraction_prompt(
        client_name=client_name,
        document_sets=document_sets,
        settings=settings,
    )

    # Check token limit
    prompt_tokens = count_tokens(prompt)
    if prompt_tokens > MAX_INPUT_TOKENS:
        logger.warning(
            f"Prompt has {prompt_tokens} tokens, exceeding recommended limit of "
            f"{MAX_INPUT_TOKENS}. Consider splitting into separate calls."
        )

    # Handle debug mode: save prompt instead of calling API
    if settings.debug_mode:
        logger.info("Debug mode enabled - saving batch prompt instead of calling API")
        debug_path = settings.debug_dir / client_name
        debug_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = debug_path / f"prompt_batch_{timestamp}.md"
        file_path.write_text(prompt, encoding="utf-8")
        logger.info(f"Batch prompt saved to {file_path}")

        # Return dummy results for each subtype
        results = {}
        for doc_set in document_sets:
            results[doc_set.subtype] = ExtractionResult(
                client_rules="// Debug mode - no API call made",
                guidelines="# Debug mode - no API call made",
                input_tokens=prompt_tokens // len(document_sets),
                output_tokens=0,
            )
        return results

    # Make API call
    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        logger.debug(f"Calling Claude API with model: {settings.model}")
        response = client.messages.create(
            model=settings.model,
            max_tokens=32000,  # Higher limit for batch
            messages=[{"role": "user", "content": prompt}],
        )
        logger.debug(
            f"API response received: {response.usage.input_tokens} input, "
            f"{response.usage.output_tokens} output tokens"
        )
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        raise ExtractionError(
            f"Claude API error: {e}",
            subtype="batch",
            original_error=e,
        )

    # Parse response for each subtype
    response_text = response.content[0].text

    try:
        results = _parse_batch_response(response_text, document_sets)
    except Exception as e:
        logger.error(f"Failed to parse batch response: {e}")
        raise ResponseParsingError(
            f"Failed to parse Claude batch response: {e}",
            subtype="batch",
            original_error=e,
        )

    # Distribute token usage across subtypes
    input_tokens_per_subtype = response.usage.input_tokens // len(document_sets)
    output_tokens_per_subtype = response.usage.output_tokens // len(document_sets)

    for subtype in results:
        results[subtype] = ExtractionResult(
            client_rules=results[subtype].client_rules,
            guidelines=results[subtype].guidelines,
            input_tokens=input_tokens_per_subtype,
            output_tokens=output_tokens_per_subtype,
        )

    logger.info(f"Batch extraction complete for {len(results)} subtypes")
    return results


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def _save_debug_prompt(
    settings: Settings,
    document_set: DocumentSet,
    prompt: str,
) -> Path:
    """Save prompt to debug folder instead of calling API.

    Args:
        settings: Application settings.
        document_set: The source document set.
        prompt: The prompt to save.

    Returns:
        Path to the saved debug file.
    """
    debug_path = settings.debug_dir / document_set.client_name / document_set.subtype
    debug_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"prompt_{timestamp}.md"
    file_path = debug_path / filename

    file_path.write_text(prompt, encoding="utf-8")

    return file_path


def save_results(
    settings: Settings,
    document_set: DocumentSet,
    result: ExtractionResult,
) -> tuple[Path, Path]:
    """Save extraction results to output files.

    Args:
        settings: Application settings.
        document_set: The source document set.
        result: The extraction result to save.

    Returns:
        Tuple of (client_rules_path, guidelines_path).
    """
    output_path = settings.output_dir / document_set.client_name / document_set.subtype
    output_path.mkdir(parents=True, exist_ok=True)

    client_rules_path = output_path / "client_rules.js"
    guidelines_path = output_path / "guidelines.md"

    client_rules_path.write_text(result.client_rules, encoding="utf-8")
    guidelines_path.write_text(result.guidelines, encoding="utf-8")

    logger.info(f"Saved results to {output_path}")

    return client_rules_path, guidelines_path


def estimate_prompt_tokens(
    client_name: str,
    document_sets: list[DocumentSet],
    settings: Settings,
) -> int:
    """Estimate the token count for a prompt without building it fully.

    This is useful for cost estimation before actual extraction.

    Args:
        client_name: Name of the client/brand.
        document_sets: List of document sets.
        settings: Application settings.

    Returns:
        Estimated token count.
    """
    # Base prompt overhead (mission, output spec, rules, format)
    base_overhead = 4000

    # Document content
    doc_tokens = sum(ds.total_tokens for ds in document_sets)

    # Per-document overhead (labels, separators)
    doc_count = sum(len(ds.documents) for ds in document_sets)
    doc_overhead = doc_count * 50  # ~50 tokens per document for labels

    return base_overhead + doc_tokens + doc_overhead


def scan_client_folder(
    settings: Settings,
    client_name: str,
) -> list[DocumentSet]:
    """Scan a client folder and create DocumentSets for each subtype.

    This function is used by the CLI to discover and organize documents
    from the filesystem. It handles language detection but does NOT
    automatically pair documents (use the GUI for pairing).

    Args:
        settings: Application settings.
        client_name: Name of the client folder to scan.

    Returns:
        List of DocumentSet objects, one per subtype folder.

    Raises:
        ClientNotFoundError: If the client folder doesn't exist.
    """
    client_path = settings.input_dir / client_name

    if not client_path.exists():
        raise ClientNotFoundError(f"Client folder not found: {client_path}")

    document_sets = []

    # Get subtype folders (or use root if no subfolders)
    subtype_folders = [d for d in client_path.iterdir() if d.is_dir()]

    if not subtype_folders:
        # No subfolders - treat root as single subtype
        subtype_folders = [client_path]

    for subtype_folder in subtype_folders:
        subtype = subtype_folder.name if subtype_folder != client_path else "general"

        # Get supported files
        files = get_supported_files(subtype_folder)

        if not files:
            logger.debug(f"No supported files in {subtype_folder}")
            continue

        documents = []
        total_tokens = 0

        for file_path in files:
            try:
                content = parse_document(file_path)
            except Exception as e:
                logger.warning(f"Failed to parse {file_path}: {e}")
                continue

            # Detect language
            lang = extract_language_from_filename(file_path.name)
            if not lang:
                lang = detect_language(content)

            tokens = count_tokens(content)
            total_tokens += tokens

            doc = Document(
                filename=file_path.name,
                content=content,
                language=lang if lang else "UNKNOWN",
                pair_id=None,  # CLI doesn't do automatic pairing (use GUI for that)
                tokens=tokens,
            )
            documents.append(doc)

        if documents:
            doc_set = DocumentSet(
                client_name=client_name,
                subtype=subtype,
                documents=documents,
                total_tokens=total_tokens,
            )
            document_sets.append(doc_set)
            logger.info(
                f"Scanned {subtype}: {len(documents)} documents, "
                f"{total_tokens:,} tokens"
            )

    return document_sets
