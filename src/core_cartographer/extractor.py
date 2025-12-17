"""Core extraction logic using Claude API."""

import re
from dataclasses import dataclass
from pathlib import Path

import anthropic

from .config import Settings
from .parser import get_supported_files, parse_document
from .cost_estimator import count_tokens


@dataclass
class ExtractionResult:
    """Result of a client rules and guidelines extraction."""

    client_rules: str  # JavaScript code
    guidelines: str  # Markdown content
    input_tokens: int
    output_tokens: int


@dataclass
class DocumentSet:
    """A collection of documents from a subtype folder."""

    client_name: str
    subtype: str
    documents: list[tuple[Path, str]]  # (path, content) pairs
    total_tokens: int


def scan_client_folder(settings: Settings, client_name: str) -> list[DocumentSet]:
    """
    Scan a client folder and return document sets for each subtype.

    Args:
        settings: Application settings.
        client_name: Name of the client folder.

    Returns:
        List of DocumentSet objects, one per subtype subfolder.
    """
    client_path = settings.input_dir / client_name

    if not client_path.exists():
        raise FileNotFoundError(f"Client folder not found: {client_path}")

    document_sets = []

    # Check for subtypes (subfolders)
    subtypes = [d for d in client_path.iterdir() if d.is_dir()]

    if not subtypes:
        # No subfolders, treat client folder as single subtype
        subtypes = [client_path]

    for subtype_path in subtypes:
        files = get_supported_files(subtype_path)

        if not files:
            continue

        documents = []
        total_tokens = 0

        for file_path in files:
            content = parse_document(file_path)
            documents.append((file_path, content))
            total_tokens += count_tokens(content)

        subtype_name = subtype_path.name if subtype_path != client_path else "default"

        document_sets.append(
            DocumentSet(
                client_name=client_name,
                subtype=subtype_name,
                documents=documents,
                total_tokens=total_tokens,
            )
        )

    return document_sets


def extract_rules_and_guidelines(
    settings: Settings,
    document_set: DocumentSet,
) -> ExtractionResult:
    """
    Extract client rules and guidelines from a document set using Claude.

    Args:
        settings: Application settings.
        document_set: The documents to process.

    Returns:
        ExtractionResult containing the client rules (JS) and guidelines (MD).
    """
    # Load example files and instructions
    client_rules_example = settings.client_rules_example_path.read_text(encoding="utf-8")
    guidelines_example = settings.guidelines_example_path.read_text(encoding="utf-8")
    instructions = settings.extraction_instructions_path.read_text(encoding="utf-8")

    # Prepare document content for the prompt
    documents_text = ""
    for path, content in document_set.documents:
        documents_text += f"\n\n--- Document: {path.name} ---\n\n{content}"

    # Build the prompt
    prompt = f"""You are analyzing copy documents to extract validation rules and localization guidelines.

## Instructions
{instructions}

## Example Client Rules Config (follow this JavaScript structure)
```javascript
{client_rules_example}
```

## Example Guidelines Document (follow this Markdown structure)
```markdown
{guidelines_example}
```

## Documents to Analyze

Client: {document_set.client_name}
Document Type: {document_set.subtype}
Document Count: {len(document_set.documents)}

{documents_text}

---

Please analyze all the documents above and create:
1. A `client_rules.js` file with machine-readable validation rules
2. A `guidelines.md` file with human-readable localization guidance

Use the client name "{document_set.client_name}" and determine the appropriate locale from the document content.

Respond with two clearly labeled sections:

## CLIENT_RULES

```javascript
[Your complete client_rules.js content here]
```

## GUIDELINES

[Your complete guidelines.md content here - do NOT wrap in code fences]
"""

    # Make API call
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=settings.model,
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse response
    response_text = response.content[0].text

    # Split response into client_rules and guidelines
    client_rules, guidelines = _parse_response(response_text)

    return ExtractionResult(
        client_rules=client_rules,
        guidelines=guidelines,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


def _parse_response(response_text: str) -> tuple[str, str]:
    """Parse the response to extract client_rules and guidelines sections."""
    client_rules = ""
    guidelines = ""

    # Extract CLIENT_RULES section (JavaScript code block)
    client_rules_match = re.search(
        r"## CLIENT_RULES\s*```javascript\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )
    if client_rules_match:
        client_rules = client_rules_match.group(1).strip()

    # Extract GUIDELINES section (everything after ## GUIDELINES)
    guidelines_match = re.search(
        r"## GUIDELINES\s*(.*?)(?=\n## [A-Z]|$)",
        response_text,
        re.DOTALL | re.IGNORECASE,
    )
    if guidelines_match:
        guidelines = guidelines_match.group(1).strip()
    else:
        # Fallback: take everything after ## GUIDELINES
        if "## GUIDELINES" in response_text.upper():
            parts = re.split(r"## GUIDELINES", response_text, flags=re.IGNORECASE)
            if len(parts) > 1:
                guidelines = parts[1].strip()

    return client_rules, guidelines


def save_results(
    settings: Settings,
    document_set: DocumentSet,
    result: ExtractionResult,
) -> tuple[Path, Path]:
    """
    Save extraction results to output files.

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

    return client_rules_path, guidelines_path
