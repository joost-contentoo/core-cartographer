"""Data models for Core Cartographer.

This module defines the core data structures used throughout the application
for representing documents, document sets, and extraction results.
"""

from dataclasses import dataclass, field


@dataclass
class Document:
    """A single document with metadata.

    Attributes:
        filename: Original filename of the document.
        content: Parsed text content of the document.
        language: Detected or assigned language code (e.g., "EN", "DE").
        pair_id: Identifier linking paired documents (e.g., "1", "2").
                 None or "-" for unpaired documents.
        tokens: Estimated token count for this document.
    """

    filename: str
    content: str
    language: str
    pair_id: str | None = None
    tokens: int = 0

    @property
    def is_paired(self) -> bool:
        """Check if this document is part of a translation pair."""
        return self.pair_id is not None and self.pair_id != "-"


@dataclass
class DocumentPair:
    """A pair of source and target documents for terminology extraction.

    Attributes:
        pair_id: Unique identifier for this pair.
        source: The source language document.
        target: The target language document.
    """

    pair_id: str
    source: Document
    target: Document


@dataclass
class DocumentSet:
    """A collection of documents for a single subtype.

    This represents all documents within a subtype (e.g., "gift_cards"),
    organized by their pairing status for optimal prompt construction.

    Attributes:
        client_name: Name of the client/brand.
        subtype: Category name (e.g., "gift_cards", "game_cards").
        documents: All documents in this set.
        total_tokens: Sum of tokens across all documents.
    """

    client_name: str
    subtype: str
    documents: list[Document] = field(default_factory=list)
    total_tokens: int = 0

    @property
    def paired_documents(self) -> list[DocumentPair]:
        """Get documents organized as source-target pairs.

        Returns:
            List of DocumentPair objects for documents that have pairs.
        """
        pairs: dict[str, dict[str, Document]] = {}

        for doc in self.documents:
            if not doc.is_paired or doc.pair_id is None:
                continue

            if doc.pair_id not in pairs:
                pairs[doc.pair_id] = {}

            # Determine if source or target based on language
            # Typically EN is source, others are target
            if doc.language.upper() in ("EN", "EN-GB", "EN-US", "EN-WW"):
                pairs[doc.pair_id]["source"] = doc
            else:
                pairs[doc.pair_id]["target"] = doc

        result = []
        for pair_id, docs in sorted(pairs.items()):
            if "source" in docs and "target" in docs:
                result.append(
                    DocumentPair(
                        pair_id=pair_id,
                        source=docs["source"],
                        target=docs["target"],
                    )
                )

        return result

    @property
    def unpaired_documents(self) -> list[Document]:
        """Get documents that are not part of any pair.

        Returns:
            List of Document objects without pair assignments.
        """
        paired_filenames = set()
        for pair in self.paired_documents:
            paired_filenames.add(pair.source.filename)
            paired_filenames.add(pair.target.filename)

        return [doc for doc in self.documents if doc.filename not in paired_filenames]

    @property
    def languages(self) -> set[str]:
        """Get all unique languages in this document set."""
        return {doc.language for doc in self.documents if doc.language}

    @property
    def source_language(self) -> str | None:
        """Detect the source language (typically English)."""
        for lang in self.languages:
            if lang.upper().startswith("EN"):
                return lang
        return None

    @property
    def target_language(self) -> str | None:
        """Detect the target language (non-English)."""
        for lang in self.languages:
            if not lang.upper().startswith("EN") and lang.upper() != "UNKNOWN":
                return lang
        return None

    @property
    def language_situation(self) -> str:
        """Describe the language situation for this document set.

        Returns:
            A string like "en-GB → de-DE (paired)" or "de-DE (target only)"
        """
        source = self.source_language
        target = self.target_language
        has_pairs = len(self.paired_documents) > 0

        if source and target and has_pairs:
            return f"{source} → {target} (paired)"
        elif source and target:
            return f"{source} + {target} (unpaired)"
        elif target:
            return f"{target} (target only)"
        elif source:
            return f"{source} (source only)"
        else:
            return "unknown"


@dataclass
class ExtractionResult:
    """Result of a client rules and guidelines extraction.

    Attributes:
        client_rules: Generated JavaScript validation config.
        guidelines: Generated Markdown style guide.
        input_tokens: Actual input tokens used in API call.
        output_tokens: Actual output tokens in API response.
    """

    client_rules: str
    guidelines: str
    input_tokens: int
    output_tokens: int
