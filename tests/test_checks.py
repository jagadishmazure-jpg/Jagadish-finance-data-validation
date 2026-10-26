"""Fabricated-value checklist: every failed check blocks downstream use."""

from datetime import date

from finance_data_validation.checks import (
    FinancialRecord, validate_record,
)

REF = date(2026, 10, 1)
GOOD = FinancialRecord(
    dataset="synthetic-q3",
    values={"revenue": 500000.0, "expenses": 320000.0, "net_income": 180000.0},
    line_items={"a": 100000.0, "b": 80000.0},
    stated_total=180000.0,
    source_citation="Q3 ledger note 2026-07",
    as_of=date(2026, 7, 15),
)


def _names(result):
    return {c.name for c in result.failed_checks}


def test_clean_record_passes_all_checks_and_is_usable():
    result = validate_record(GOOD, REF)
    assert result.passed and not result.blocked
    assert result.usable_fields == GOOD.values


def test_cross_field_mismatch_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3",
        values={"revenue": 500000.0, "expenses": 320000.0,
                "net_income": 999999.0},
        source_citation="Q3 ledger note", as_of=date(2026, 7, 15))
    result = validate_record(bad, REF)
    assert "cross_field" in _names(result)
    assert result.blocked and result.usable_fields == {}


def test_missing_citation_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3",
        values={"revenue": 100.0}, source_citation=None,
        as_of=date(2026, 7, 15))
    result = validate_record(bad, REF)
    assert "citation" in _names(result) and result.blocked


def test_blank_citation_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="   ", as_of=date(2026, 7, 15))
    result = validate_record(bad, REF)
    assert "citation" in _names(result)


def test_arithmetic_mismatch_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        line_items={"a": 60.0, "b": 50.0}, stated_total=100.0,
        source_citation="note", as_of=date(2026, 7, 15))
    result = validate_record(bad, REF)
    assert "arithmetic" in _names(result) and result.blocked


def test_arithmetic_match_passes():
    good = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        line_items={"a": 60.0, "b": 40.0}, stated_total=100.0,
        source_citation="note", as_of=date(2026, 7, 15))
    assert validate_record(good, REF).passed


def test_stale_record_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="note", as_of=date(2025, 1, 1))
    result = validate_record(bad, REF)
    assert "stale" in _names(result) and result.blocked


def test_stale_boundary_exactly_180_days_passes():
    good = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="note", as_of=date(2026, 4, 4))
    assert "stale" not in _names(validate_record(good, REF))


def test_future_dated_record_flagged_stale():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="note", as_of=date(2027, 1, 1))
    assert "stale" in _names(validate_record(bad, REF))


def test_missing_date_flagged_stale():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="note", as_of=None)
    assert "stale" in _names(validate_record(bad, REF))


def test_out_of_range_value_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 10 ** 15},
        source_citation="note", as_of=date(2026, 7, 15))
    assert "range" in _names(validate_record(bad, REF))


def test_non_numeric_value_blocks():
    bad = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": "lots"},
        source_citation="note", as_of=date(2026, 7, 15))
    assert "range" in _names(validate_record(bad, REF))


def test_fabricated_record_fails_multiple_checks_and_is_blocked():
    # Inconsistent arithmetic AND no citation: the fabricated-value case.
    bad = FinancialRecord(
        dataset="synthetic-q3",
        values={"revenue": 500000.0, "expenses": 320000.0,
                "net_income": 500000.0},
        source_citation=None, as_of=date(2026, 7, 15))
    result = validate_record(bad, REF)
    assert len(result.failed_checks) >= 2
    assert result.blocked and result.usable_fields == {}


def test_partial_fields_skip_cross_field_gracefully():
    partial = FinancialRecord(
        dataset="synthetic-q3", values={"revenue": 100.0},
        source_citation="note", as_of=date(2026, 7, 15))
    assert validate_record(partial, REF).passed
