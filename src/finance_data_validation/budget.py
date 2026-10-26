"""Cost/budget inputs: negatives are rejected, never silently accepted.

A negative cost would let a caller understate spend or slip past a cap
by cancelling real spend with a fake credit, so every entry point that
accepts a cost validates it first.
"""

from __future__ import annotations


def validate_cost(value) -> float:
    """Return ``value`` as a float, rejecting negatives and non-numbers."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("cost must be a number")
    if value < 0:
        raise ValueError(f"negative cost rejected: {value}")
    return float(value)


class Budget:
    """A capped spend ledger: negative or over-cap spend is refused."""

    def __init__(self, cap: float):
        self.cap = validate_cost(cap)
        self.spent = 0.0

    def spend(self, amount) -> float:
        amount = validate_cost(amount)
        if self.spent + amount > self.cap:
            raise ValueError("spend would exceed budget cap")
        self.spent += amount
        return self.spent

    @property
    def remaining(self) -> float:
        return self.cap - self.spent
