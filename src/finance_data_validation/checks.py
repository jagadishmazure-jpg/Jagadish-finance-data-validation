"""Fabricated-value detection checklist.

Every check below is a gate, not a warning: any failed check blocks the
record's values from downstream use (see ``ValidationResult.blocked``
and ``usable_fields``). The five checks are:

1. range -- every numeric value lies inside a plausible band;
2. cross-field consistency -- net income equals revenue minus expenses
   (when all three are present);
3. source-citation presence -- a citation must be present;
4. arithmetic verification -- stated totals equal the sum of their parts;
5. stale-data flag -- the record's date must be present, not in the
   future, and no older than ``STALE_AFTER_DAYS`` before the reference
   date.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

STALE_AFTER_DAYS = 180
MAX_VALUE = 1_000_000_000_000.0  # 1 trillion, in the record's currency
TOLERANCE = 0.01


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class FinancialRecord:
    dataset: str
    values: dict
    line_items: dict | None = None
    stated_total: float | None = None
    source_citation: str | None = None
    as_of: date | None = None


@dataclass
class ValidationResult:
    record: FinancialRecord
    checks: list = field(default_factory=list)

    @property
    def failed_checks(self) -> list:
        return [c for c in self.checks if not c.passed]

    @property
    def passed(self) -> bool:
        return not self.failed_checks

    @property
    def blocked(self) -> bool:
        """Any failed check blocks downstream use. No exceptions."""
        return not self.passed

    @property
    def usable_fields(self) -> dict:
        """Values released downstream: empty when blocked."""
        return {} if self.blocked else dict(self.record.values)


def _range_check(record: FinancialRecord) -> CheckResult:
    for name, value in record.values.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return CheckResult("range", False, f"{name} is not numeric")
        if value < -MAX_VALUE or value > MAX_VALUE:
            return CheckResult("range", False,
                               f"{name}={value:g} outside plausible band")
    return CheckResult("range", True, "all values inside plausible band")


def _cross_field_check(record: FinancialRecord) -> CheckResult:
    v = record.values
    if {"revenue", "expenses", "net_income"} <= set(v):
        expected = v["revenue"] - v["expenses"]
        if abs(v["net_income"] - expected) > TOLERANCE:
            return CheckResult(
                "cross_field", False,
                f"net_income {v['net_income']:g} != revenue - expenses "
                f"{expected:g}")
    return CheckResult("cross_field", True,
                       "cross-field relation holds or is not applicable")


def _citation_check(record: FinancialRecord) -> CheckResult:
    if record.source_citation and record.source_citation.strip():
        return CheckResult("citation", True, "source citation present")
    return CheckResult("citation", False, "no source citation present")


def _arithmetic_check(record: FinancialRecord) -> CheckResult:
    if record.line_items is not None and record.stated_total is not None:
        total = sum(record.line_items.values())
        if abs(total - record.stated_total) > TOLERANCE:
            return CheckResult(
                "arithmetic", False,
                f"line items sum to {total:g}, stated total "
                f"{record.stated_total:g}")
        return CheckResult("arithmetic", True, "parts sum to stated total")
    return CheckResult("arithmetic", True,
                       "no line-item total to verify")


def _stale_check(record: FinancialRecord, reference: date) -> CheckResult:
    if record.as_of is None:
        return CheckResult("stale", False, "no record date present")
    age = (reference - record.as_of).days
    if age < 0:
        return CheckResult("stale", False, "record date is in the future")
    if age > STALE_AFTER_DAYS:
        return CheckResult("stale", False,
                           f"record is {age} days old "
                           f"(limit {STALE_AFTER_DAYS})")
    return CheckResult("stale", True, f"record is {age} days old")


def validate_record(record: FinancialRecord,
                    reference: date | None = None) -> ValidationResult:
    """Run all five checks; any failure blocks the record."""
    reference = reference or date.today()
    checks = [
        _range_check(record),
        _cross_field_check(record),
        _citation_check(record),
        _arithmetic_check(record),
        _stale_check(record, reference),
    ]
    return ValidationResult(record=record, checks=checks)
