"""
Token Management
===============

Token counting and cost estimation utilities.
"""

import time
from typing import Any, Dict

import tiktoken


class TiktokenCounter:
    """Token counter using tiktoken"""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))

    def count_message_tokens(self, messages: list) -> int:
        """Count tokens in message list"""
        total = 0
        for message in messages:
            if isinstance(message, dict):
                content = message.get("content", "")
                role = message.get("role", "")
                total += self.count_tokens(content)
                total += self.count_tokens(role)
                total += 3  # Message overhead
            else:
                total += self.count_tokens(str(message))
        return total


class CostEstimator:
    """Cost estimation for API calls"""

    # Pricing per 1K tokens (approximate)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    }

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.counter = TiktokenCounter(model)

    def estimate_cost(self, input_text: str, output_text: str = "") -> Dict[str, float]:
        """Estimate cost for input and output text"""
        input_tokens = self.counter.count_tokens(input_text)
        output_tokens = self.counter.count_tokens(output_text) if output_text else 0

        pricing = self.PRICING.get(self.model, self.PRICING["gpt-4"])

        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": input_cost + output_cost,
        }


class TokenBudgetManager:
    """Manages token budgets and usage tracking"""

    def __init__(self, daily_budget: float = 100.0):
        self.daily_budget = daily_budget
        self.current_usage = 0.0
        self.usage_history = []

    def check_budget(self, estimated_cost: float) -> bool:
        """Check if operation is within budget"""
        return (self.current_usage + estimated_cost) <= self.daily_budget

    def record_usage(self, cost: float) -> None:
        """Record token usage"""
        self.current_usage += cost
        self.usage_history.append(
            {"cost": cost, "timestamp": time.time(), "total_usage": self.current_usage}
        )

    def get_remaining_budget(self) -> float:
        """Get remaining budget"""
        return max(0.0, self.daily_budget - self.current_usage)

    def reset_daily_usage(self) -> None:
        """Reset daily usage counter"""
        self.current_usage = 0.0


class TokenUsageTracker:
    """Tracks token usage across operations"""

    def __init__(self):
        self.usage_log = []
        self.total_tokens = 0
        self.total_cost = 0.0

    def log_usage(self, operation: str, tokens: int, cost: float) -> None:
        """Log token usage for an operation"""
        entry = {
            "operation": operation,
            "tokens": tokens,
            "cost": cost,
            "timestamp": time.time(),
        }
        self.usage_log.append(entry)
        self.total_tokens += tokens
        self.total_cost += cost

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        return {
            "total_operations": len(self.usage_log),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_tokens_per_operation": self.total_tokens
            / max(1, len(self.usage_log)),
            "average_cost_per_operation": self.total_cost / max(1, len(self.usage_log)),
        }
