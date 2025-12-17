"""Token counting and cost estimation utilities."""

import tiktoken

# Pricing per 1M tokens (as of Dec 2024)
# Using Claude Opus 4.5 pricing
PRICING = {
    "claude-opus-4-5-20251101": {
        "input": 5.00,  # $5 per 1M input tokens
        "output": 25.00,  # $25 per 1M output tokens
    },
    "claude-sonnet-4-5": {
        "input": 3.00,  # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
    },
    "claude-sonnet-4-20250514": {
        "input": 3.00,  # $3 per 1M input tokens
        "output": 15.00,  # $15 per 1M output tokens
    },
}


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string.

    Uses cl100k_base encoding as an approximation for Claude tokenization.

    Args:
        text: The text to count tokens for.

    Returns:
        Estimated token count.
    """
    # Using cl100k_base as a reasonable approximation for Claude
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def estimate_cost(
    input_tokens: int,
    estimated_output_tokens: int,
    model: str = "claude-opus-4-5-20251101",
) -> float:
    """
    Estimate the cost of an API call.

    Args:
        input_tokens: Number of input tokens.
        estimated_output_tokens: Estimated number of output tokens.
        model: Model name for pricing lookup.

    Returns:
        Estimated cost in USD.
    """
    pricing = PRICING.get(model, PRICING["claude-opus-4-5-20251101"])

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]

    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """Format a cost value for display."""
    return f"${cost:.4f}"


def format_tokens(tokens: int) -> str:
    """Format a token count for display."""
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}k"
    return str(tokens)
