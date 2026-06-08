"""Token usage tracking and cost estimation."""
from dataclasses import dataclass, field

# Approximate pricing per 1K tokens (USD)
MODEL_PRICING = {
    # OpenAI
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    # Anthropic
    "claude-sonnet-4": {"input": 0.003, "output": 0.015},
    "claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-opus-4": {"input": 0.015, "output": 0.075},
    # DeepSeek
    "deepseek-chat": {"input": 0.0005, "output": 0.002},
    "deepseek-reasoner": {"input": 0.001, "output": 0.004},
    "deepseek-v3": {"input": 0.0005, "output": 0.002},
    "deepseek-r1": {"input": 0.001, "output": 0.004},
    # Default fallback
    "__default__": {"input": 0.001, "output": 0.003},
}


@dataclass
class UsageRecord:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0


class UsageTracker:
    def __init__(self):
        self.session: UsageRecord = UsageRecord()
        self.turn: UsageRecord = UsageRecord()

    def add(self, input_tokens: int = 0, output_tokens: int = 0,
            cache_read: int = 0, cache_write: int = 0):
        for rec in (self.turn, self.session):
            rec.input_tokens += input_tokens
            rec.output_tokens += output_tokens
            rec.cache_read_tokens += cache_read
            rec.cache_write_tokens += cache_write

    def reset_turn(self):
        self.turn = UsageRecord()

    def estimate_cost(self, record: UsageRecord, model_key: str = "__default__") -> float:
        pricing = MODEL_PRICING.get(model_key, MODEL_PRICING["__default__"])
        cost = (record.input_tokens / 1000) * pricing["input"]
        cost += (record.output_tokens / 1000) * pricing["output"]
        return round(cost, 6)

    def format_usage(self, record: UsageRecord) -> str:
        parts = []
        if record.input_tokens:
            parts.append(f"in {record.input_tokens}")
        if record.output_tokens:
            parts.append(f"out {record.output_tokens}")
        if record.cache_read_tokens:
            parts.append(f"cache {record.cache_read_tokens}")
        return " / ".join(parts) if parts else "—"

    def format_cost(self, record: UsageRecord, model_key: str = "__default__") -> str:
        cost = self.estimate_cost(record, model_key)
        if cost == 0:
            return "$0"
        if cost < 0.01:
            return f"${cost:.6f}"
        if cost < 1:
            return f"${cost:.4f}"
        return f"${cost:.2f}"

    def summary(self, model_key: str = "__default__") -> dict:
        return {
            "turn": {
                "input": self.turn.input_tokens,
                "output": self.turn.output_tokens,
                "cost": self.estimate_cost(self.turn, model_key),
            },
            "session": {
                "input": self.session.input_tokens,
                "output": self.session.output_tokens,
                "cost": self.estimate_cost(self.session, model_key),
            },
        }


# Global tracker
_tracker = UsageTracker()


def get_tracker() -> UsageTracker:
    return _tracker


def reset_turn():
    _tracker.reset_turn()
