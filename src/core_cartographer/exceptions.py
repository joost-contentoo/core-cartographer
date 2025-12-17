"""Custom exceptions for Core Cartographer.

This module defines domain-specific exceptions for better error handling
and debugging throughout the application.
"""


class CartographerError(Exception):
    """Base exception for all Core Cartographer errors."""

    pass


class ConfigurationError(CartographerError):
    """Raised when there's a configuration or settings error.

    Examples:
        - Missing API key
        - Invalid directory paths
        - Malformed configuration values
    """

    pass


class DocumentParsingError(CartographerError):
    """Raised when a document cannot be parsed.

    Attributes:
        file_path: Path to the file that failed to parse.
        original_error: The underlying exception that caused the failure.
    """

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.original_error = original_error

    def __str__(self) -> str:
        msg = super().__str__()
        if self.file_path:
            msg = f"{msg} (file: {self.file_path})"
        return msg


class UnsupportedFormatError(DocumentParsingError):
    """Raised when attempting to parse an unsupported file format."""

    pass


class ExtractionError(CartographerError):
    """Raised when Claude API extraction fails.

    Attributes:
        subtype: The document subtype being processed.
        original_error: The underlying exception from the API.
    """

    def __init__(
        self,
        message: str,
        subtype: str | None = None,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.subtype = subtype
        self.original_error = original_error

    def __str__(self) -> str:
        msg = super().__str__()
        if self.subtype:
            msg = f"{msg} (subtype: {self.subtype})"
        return msg


class ResponseParsingError(ExtractionError):
    """Raised when the Claude response cannot be parsed into expected format."""

    pass


class ClientNotFoundError(CartographerError):
    """Raised when a client folder doesn't exist."""

    def __init__(self, client_name: str, input_dir: str | None = None):
        self.client_name = client_name
        self.input_dir = input_dir
        message = f"Client folder not found: {client_name}"
        if input_dir:
            message = f"{message} (in {input_dir})"
        super().__init__(message)


class NoDocumentsFoundError(CartographerError):
    """Raised when no processable documents are found in a folder."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"No supported documents found in: {path}")
