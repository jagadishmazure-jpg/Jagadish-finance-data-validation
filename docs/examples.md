# Real code excerpts and real output

Excerpts below are copied from the repo's own modules; outputs are from
real runs on 2026-10-26 (offline, system Python 3.12).

## Extraction

```python
from finance_data_validation import extraction
result = extraction.extract_fields(
    "Revenue was $500,000 and expenses were $320,000, "
    "net income $180,000. Source: Q3 ledger note 2026-07.")
result.fields
# {'net_income': 180000.0, 'revenue': 500000.0, 'expenses': 320000.0}
```

## Validation blocks a fabricated record

```python
from datetime import date
from finance_data_validation.checks import FinancialRecord, validate_record
bad = FinancialRecord(
    dataset="synthetic-q3",
    values={"revenue": 500000.0, "expenses": 320000.0,
            "net_income": 999999.0},
    source_citation="Q3 ledger note", as_of=date(2026, 7, 15))
result = validate_record(bad, date(2026, 10, 1))
result.blocked, result.usable_fields
# (True, {})
```

## Demo run (`python3 examples/demo.py`)

```
fields={'net_income': 180000.0, 'revenue': 500000.0, 'expenses': 320000.0} passed=True failed=[]
fields={'net_income': 999000.0, 'revenue': 400000.0, 'expenses': 250000.0} passed=False failed=['cross_field']
fields={'net_income': 100000.0, 'revenue': 300000.0, 'expenses': 200000.0} passed=False failed=['citation']
redacted: Contact [REDACTED:EMAIL] or [REDACTED:PHONE] about the note. hits={'phone': 1, 'email': 1}
{'dataset': 'synthetic-q3', 'total': 3, 'passed': 1, 'failed': 2, 'pass_rate': 0.3333,
 'failed_by_type': {'cross_field': 1, 'citation': 1}, 'pii_hits': {'phone': 1, 'email': 1},
 'pii_total': 2, 'fitness': 'not fit: PII present'}
```

The demo set has 3 records; 1 passed because the other two were
deliberately built to fail. That pass rate describes the fixture, not
real-world data quality.
