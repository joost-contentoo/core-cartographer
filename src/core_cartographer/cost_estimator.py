"""Token counting and cost estimation utilities."""

import tiktoken

# Pricing per 1M tokens (as of Dec 2025)
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

    Uses cl100k_base encoding as an approximation for Claude tokenization,
    with a 1.2x correction factor to provide a conservative estimate
    (Claude's tokenizer typically produces ~16-20% more tokens than tiktoken).

    Args:
        text: The text to count tokens for.

    Returns:
        Estimated token count.
    """
    # Using cl100k_base as a reasonable approximation for Claude
    encoding = tiktoken.get_encoding("cl100k_base")
    base_count = len(encoding.encode(text))

    # Apply 1.2x correction factor for conservative estimation
    # (Claude's tokenizer produces ~16-20% more tokens than tiktoken)
    return int(base_count * 1.2)


def estimate_cost(
    input_tokens: int,
    estimated_output_tokens: int,
    model: str = "claude-opus-4-5-20251101",
    round_to_nickel: bool = True,
) -> float:
    """
    Estimate the cost of an API call.

    Args:
        input_tokens: Number of input tokens.
        estimated_output_tokens: Estimated number of output tokens.
        model: Model name for pricing lookup.
        round_to_nickel: If True, round up to nearest $0.05 increment.

    Returns:
        Estimated cost in USD.
    """
    pricing = PRICING.get(model, PRICING["claude-opus-4-5-20251101"])

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (estimated_output_tokens / 1_000_000) * pricing["output"]

    total_cost = input_cost + output_cost

    if round_to_nickel:
        # Round up to nearest $0.05
        import math
        return math.ceil(total_cost / 0.05) * 0.05

    return total_cost


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
