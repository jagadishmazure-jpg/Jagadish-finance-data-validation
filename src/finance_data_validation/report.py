"""Per-dataset data-quality report.

One report per dataset, so a consumer can judge fitness for use before
trusting any value: how many records passed, which checks failed and how
often, and how many PII hits were found (PII must be zero before a
dataset is called fit). Numbers come from actual validation runs, never
from estimates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

FIT_PASS_RATE = 0.9


@dataclass
class DataQualityReport:
    dataset: str
    total: int
    passed: int
    failed_by_type: dict = field(default_factory=dict)
    pii_hits: dict = field(default_factory=dict)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.passed / self.total, 4)

    @property
    def pii_total(self) -> int:
        return sum(self.pii_hits.values())

    @property
    def fitness(self) -> str:
        if self.total == 0:
            return "not fit: empty dataset"
        if self.pii_total > 0:
            return "not fit: PII present"
        if self.pass_rate >= FIT_PASS_RATE:
            return "fit for use"
        return "review required"

    def as_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "failed_by_type": dict(self.failed_by_type),
            "pii_hits": dict(self.pii_hits),
            "pii_total": self.pii_total,
            "fitness": self.fitness,
        }


def build_report(dataset: str, validation_results,
                 pii_hits: dict | None = None) -> DataQualityReport:
    """Build a report from real validation results and PII scan counts."""
    failed_by_type: Counter = Counter()
    passed = 0
    for result in validation_results:
        if result.passed:
            passed += 1
        for check in result.failed_checks:
            failed_by_type[check.name] += 1
    return DataQualityReport(
        dataset=dataset,
        total=len(validation_results),
        passed=passed,
        failed_by_type=dict(failed_by_type),
        pii_hits=dict(pii_hits or {}),
    )
