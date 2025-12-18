"""Tests for cost estimation utilities."""

import pytest

from core_cartographer.cost_estimator import (
    PRICING,
    count_tokens,
    estimate_cost,
    format_cost,
    format_tokens,
)


class TestCountTokens:
    """Tests for count_tokens function."""

    def test_count_empty_string(self) -> None:
        """Test counting tokens in an empty string."""
        result = count_tokens("")
        assert result == 0

    def test_count_simple_text(self) -> None:
        """Test counting tokens in simple text."""
        result = count_tokens("Hello, world!")
        assert result > 0
        assert result < 10  # Should be around 4 tokens

    def test_count_longer_text(self) -> None:
        """Test that longer text has more tokens."""
        short = count_tokens("Hello")
        long = count_tokens("Hello, this is a much longer text with many words.")
        assert long > short

    def test_count_unicode_text(self) -> None:
        """Test counting tokens with unicode characters."""
        result = count_tokens("こんにちは世界")  # Japanese: Hello World
        assert result > 0

    def test_count_whitespace_only(self) -> None:
        """Test counting tokens in whitespace-only text."""
        result = count_tokens("   \n\t   ")
        assert result >= 0


class TestEstimateCost:
    """Tests for estimate_cost function."""

    def test_zero_tokens(self) -> None:
        """Test cost with zero tokens."""
        result = estimate_cost(0, 0)
        assert result == 0.0

    def test_input_only(self) -> None:
        """Test cost with only input tokens."""
        # 1M input tokens at $5/1M for opus
        result = estimate_cost(1_000_000, 0, "claude-opus-4-5-20251101")
        assert result == pytest.approx(5.0)

    def test_output_only(self) -> None:
        """Test cost with only output tokens."""
        # 1M output tokens at $25/1M for opus
        result = estimate_cost(0, 1_000_000, "claude-opus-4-5-20251101")
        assert result == pytest.approx(25.0)

    def test_combined_cost(self) -> None:
        """Test cost with both input and output tokens."""
        # 1M input + 1M output for opus = $5 + $25 = $30
        result = estimate_cost(1_000_000, 1_000_000, "claude-opus-4-5-20251101")
        assert result == pytest.approx(30.0)

    def test_sonnet_pricing(self) -> None:
        """Test cost with sonnet model pricing."""
        # 1M input + 1M output for sonnet = $3 + $15 = $18
        result = estimate_cost(1_000_000, 1_000_000, "claude-sonnet-4-20250514")
        assert result == pytest.approx(18.0)

    def test_unknown_model_uses_default(self) -> None:
        """Test that unknown models fall back to opus pricing."""
        result = estimate_cost(1_000_000, 1_000_000, "unknown-model")
        expected = estimate_cost(1_000_000, 1_000_000, "claude-opus-4-5-20251101")
        assert result == expected

    def test_small_token_count(self) -> None:
        """Test cost with small token counts."""
        # 1000 input + 500 output (without rounding to nickel)
        result = estimate_cost(1000, 500, "claude-opus-4-5-20251101", round_to_nickel=False)
        expected = (1000 / 1_000_000 * 5.0) + (500 / 1_000_000 * 25.0)
        assert result == pytest.approx(expected)


class TestFormatCost:
    """Tests for format_cost function."""

    def test_format_zero(self) -> None:
        """Test formatting zero cost."""
        result = format_cost(0.0)
        assert result == "$0.0000"

    def test_format_small_cost(self) -> None:
        """Test formatting small cost."""
        result = format_cost(0.0123)
        assert result == "$0.0123"

    def test_format_larger_cost(self) -> None:
        """Test formatting larger cost."""
        result = format_cost(5.5)
        assert result == "$5.5000"

    def test_format_rounds_correctly(self) -> None:
        """Test that formatting rounds to 4 decimal places."""
        result = format_cost(1.23456789)
        assert result == "$1.2346"


class TestFormatTokens:
    """Tests for format_tokens function."""

    def test_format_small_number(self) -> None:
        """Test formatting small token counts."""
        assert format_tokens(500) == "500"
        assert format_tokens(999) == "999"

    def test_format_thousands(self) -> None:
        """Test formatting thousands of tokens."""
        assert format_tokens(1000) == "1.0k"
        assert format_tokens(1500) == "1.5k"
        assert format_tokens(10000) == "10.0k"
        assert format_tokens(999999) == "1000.0k"

    def test_format_millions(self) -> None:
        """Test formatting millions of tokens."""
        assert format_tokens(1_000_000) == "1.0M"
        assert format_tokens(2_500_000) == "2.5M"
        assert format_tokens(10_000_000) == "10.0M"

    def test_format_zero(self) -> None:
        """Test formatting zero tokens."""
        assert format_tokens(0) == "0"


class TestPricing:
    """Tests for pricing constants."""

    def test_opus_pricing_exists(self) -> None:
        """Test that opus pricing is defined."""
        assert "claude-opus-4-5-20251101" in PRICING
        pricing = PRICING["claude-opus-4-5-20251101"]
        assert "input" in pricing
        assert "output" in pricing

    def test_sonnet_pricing_exists(self) -> None:
        """Test that sonnet pricing is defined."""
        assert "claude-sonnet-4-20250514" in PRICING
        pricing = PRICING["claude-sonnet-4-20250514"]
        assert "input" in pricing
        assert "output" in pricing

    def test_output_more_expensive_than_input(self) -> None:
        """Test that output tokens cost more than input tokens."""
        for model, pricing in PRICING.items():
            msg = f"Model {model} should have higher output cost"
            assert pricing["output"] > pricing["input"], msg
