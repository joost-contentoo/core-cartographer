"""Shared dependencies and utilities for API routes."""

from fastapi import HTTPException, status
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIError(HTTPException):
    """Base API error class with consistent error responses."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.extra = kwargs


class ValidationError(APIError):
    """Validation error (400)."""

    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
            **kwargs
        )


class NotFoundError(APIError):
    """Resource not found error (404)."""

    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
            **kwargs
        )


class ProcessingError(APIError):
    """File processing error (422)."""

    def __init__(self, detail: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="PROCESSING_ERROR",
            **kwargs
        )


class RateLimitError(APIError):
    """Rate limit error (429)."""

    def __init__(self, detail: str = "Rate limit exceeded", **kwargs):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT",
            **kwargs
        )


class ServerError(APIError):
    """Internal server error (500)."""

    def __init__(self, detail: str = "Internal server error", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="SERVER_ERROR",
            **kwargs
        )


def handle_anthropic_error(error: Exception) -> APIError:
    """Convert Anthropic API errors to appropriate HTTP errors."""
    error_str = str(error).lower()

    if "rate" in error_str or "limit" in error_str:
        return RateLimitError("Claude API rate limit exceeded. Please wait and try again.")
    elif "auth" in error_str or "api key" in error_str:
        return ValidationError("Invalid API key. Please check your configuration.")
    elif "timeout" in error_str:
        return ServerError("Request timeout. Please try again.")
    else:
        logger.error(f"Anthropic API error: {error}")
        return ServerError(f"Claude API error: {str(error)}")
