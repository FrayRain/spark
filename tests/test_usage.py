"""Tests for usage tracking module."""
import json
from fluxlite.usage import UsageTracker, MODEL_PRICING


class TestUsageTracker:
    def test_empty_tracker(self):
        t = UsageTracker()
        assert t.turn.input_tokens == 0
        assert t.turn.output_tokens == 0
        assert t.session.input_tokens == 0

    def test_add_tokens(self):
        t = UsageTracker()
        t.add(input_tokens=100, output_tokens=50)
        assert t.turn.input_tokens == 100
        assert t.turn.output_tokens == 50
        assert t.session.input_tokens == 100
        assert t.session.output_tokens == 50

    def test_reset_turn(self):
        t = UsageTracker()
        t.add(input_tokens=100, output_tokens=50)
        t.reset_turn()
        assert t.turn.input_tokens == 0
        assert t.turn.output_tokens == 0
        assert t.session.input_tokens == 100  # session preserved

    def test_multiple_adds(self):
        t = UsageTracker()
        t.add(input_tokens=100, output_tokens=50)
        t.add(input_tokens=200, output_tokens=30)
        assert t.session.input_tokens == 300
        assert t.session.output_tokens == 80

    def test_cost_estimation(self):
        t = UsageTracker()
        t.add(input_tokens=1000, output_tokens=500)
        # deepseek-chat: $0.0005/1K in, $0.002/1K out
        cost = t.estimate_cost(t.session, "deepseek-chat")
        expected = (1000 / 1000) * 0.0005 + (500 / 1000) * 0.002
        assert cost == expected

    def test_cost_zero_for_no_tokens(self):
        t = UsageTracker()
        assert t.estimate_cost(t.session) == 0.0

    def test_format_usage(self):
        t = UsageTracker()
        t.add(input_tokens=150, output_tokens=75)
        formatted = t.format_usage(t.turn)
        assert "in 150" in formatted
        assert "out 75" in formatted

    def test_format_cost_small(self):
        t = UsageTracker()
        t.add(input_tokens=100, output_tokens=50)
        cost_str = t.format_cost(t.session, "deepseek-chat")
        assert cost_str.startswith("$")

    def test_summary(self):
        t = UsageTracker()
        t.add(input_tokens=500, output_tokens=200)
        s = t.summary("gpt-4o")
        assert "turn" in s
        assert "session" in s
        assert s["turn"]["input"] == 500
        assert s["session"]["output"] == 200

    def test_cache_read_tokens(self):
        t = UsageTracker()
        t.add(input_tokens=100, cache_read=50)
        assert t.turn.cache_read_tokens == 50

    def test_model_pricing_default(self):
        assert "__default__" in MODEL_PRICING
        assert MODEL_PRICING["__default__"]["input"] > 0
