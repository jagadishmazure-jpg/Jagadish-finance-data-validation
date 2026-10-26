"""Offline demo: extract, validate, redact, and report on synthetic data.

Run: python3 examples/demo.py   (from the repo root; stdlib only)
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from finance_data_validation import checks, extraction, pii, report

TEXTS = [
    "Revenue was $500,000 and expenses were $320,000, net income $180,000. "
    "Source: Q3 ledger note 2026-07.",
    "Revenue was $400,000 and expenses were $250,000, net income $999,000. "
    "Source: Q3 ledger note 2026-07.",
    "Revenue was $300,000 and expenses were $200,000, net income $100,000.",
]

REF = date(2026, 10, 1)


def main():
    results = []
    pii_total = {}
    for text in TEXTS:
        extracted = extraction.extract_fields(text)
        record = checks.FinancialRecord(
            dataset="synthetic-q3", values=extracted.fields,
            source_citation=extracted.source_citation,
            as_of=date(2026, 7, 15))
        result = checks.validate_record(record, REF)
        results.append(result)
        print(f"fields={extracted.fields} passed={result.passed} "
              f"failed={[c.name for c in result.failed_checks]}")
    dirty = "Contact analyst@example.com or 555-010-1234 about the note."
    redacted = pii.redact(dirty)
    print(f"redacted: {redacted.text} hits={redacted.hits}")
    pii_total = redacted.hits
    quality = report.build_report("synthetic-q3", results, pii_hits=pii_total)
    print(quality.as_dict())


if __name__ == "__main__":
    main()
