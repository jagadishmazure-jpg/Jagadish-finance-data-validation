"""Reports, budgets, email dry-run policy, and the brand blocklist."""

from datetime import date

import pytest

from finance_data_validation import brand
from finance_data_validation.budget import Budget, validate_cost
from finance_data_validation.checks import FinancialRecord, validate_record
from finance_data_validation.email_channel import (
    EmailRefused, send_report_email,
)
from finance_data_validation.report import build_report

REF = date(2026, 10, 1)


def _record(**over):
    base = dict(dataset="synthetic-q3", values={"revenue": 100.0},
                source_citation="note", as_of=date(2026, 7, 15))
    base.update(over)
    return FinancialRecord(**base)


def test_report_pass_rate_and_failed_by_type():
    results = [validate_record(_record(), REF),
               validate_record(_record(source_citation=None), REF),
               validate_record(_record(as_of=date(2025, 1, 1)), REF)]
    report = build_report("synthetic-q3", results)
    assert report.total == 3 and report.passed == 1
    assert report.pass_rate == round(1 / 3, 4)
    assert report.failed_by_type == {"citation": 1, "stale": 1}


def test_report_fitness_fit():
    report = build_report("synthetic-q3", [validate_record(_record(), REF)])
    assert report.fitness == "fit for use"


def test_report_fitness_not_fit_with_pii():
    report = build_report("synthetic-q3", [validate_record(_record(), REF)],
                          pii_hits={"email": 2})
    assert report.fitness == "not fit: PII present"
    assert report.pii_total == 2


def test_report_fitness_review_required_on_low_pass_rate():
    results = [validate_record(_record(), REF)] + [
        validate_record(_record(source_citation=None), REF) for _ in range(9)]
    assert build_report("synthetic-q3", results).fitness == "review required"


def test_report_empty_dataset_not_fit():
    assert build_report("synthetic-q3", []).fitness == "not fit: empty dataset"


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        validate_cost(-5)


def test_zero_cost_accepted():
    assert validate_cost(0) == 0.0


def test_non_numeric_cost_rejected():
    with pytest.raises(ValueError):
        validate_cost("free")


def test_bool_cost_rejected():
    with pytest.raises(ValueError):
        validate_cost(True)


def test_budget_negative_spend_rejected():
    budget = Budget(100)
    with pytest.raises(ValueError):
        budget.spend(-10)


def test_budget_over_cap_rejected():
    budget = Budget(100)
    budget.spend(90)
    with pytest.raises(ValueError):
        budget.spend(20)


def test_budget_tracks_remaining():
    budget = Budget(100)
    budget.spend(40)
    assert budget.remaining == 60.0


def test_email_dry_run_default_sends_nothing():
    result = send_report_email("a@example.com", "report", "body")
    assert result["dry_run"] is True and result["sent"] is False


def test_email_send_requires_opt_in():
    with pytest.raises(EmailRefused):
        send_report_email("a@example.com", "report", "body",
                          dry_run=False, opt_in=False)


def test_email_send_refused_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    with pytest.raises(EmailRefused):
        send_report_email("a@example.com", "report", "body",
                          dry_run=False, opt_in=True)


def test_email_send_without_transport_refused(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    with pytest.raises(EmailRefused):
        send_report_email("a@example.com", "report", "body",
                          dry_run=False, opt_in=True)


def test_email_send_with_transport_calls_it(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    calls = []
    result = send_report_email(
        "a@example.com", "report", "body", dry_run=False, opt_in=True,
        transport=lambda *a: calls.append(a))
    assert result["sent"] is True and len(calls) == 1


def test_brand_blocklist_is_non_empty():
    assert len(brand.BLOCKLIST_HASHES) >= 5


def test_brand_blocklist_entries_are_hashes_not_names():
    for entry in brand.BLOCKLIST_HASHES:
        assert len(entry) == 64 and all(c in "0123456789abcdef"
                                        for c in entry)


def test_brand_check_flags_blocklisted_name():
    # Name assembled from parts so this test file does not itself carry
    # a blocklisted string in plain form.
    candidate = "johns" + " hopkins university"
    assert brand.check_text(f"prepared at {candidate} in 2026") is True


def test_brand_check_passes_clean_and_fictional_text():
    assert brand.check_text("Quillwick Ledger quarterly validation") is False
    assert brand.check_text("Revenue was $500,000 in Q3.") is False
