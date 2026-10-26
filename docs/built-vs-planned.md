# Built vs planned

| Area | Status | Evidence |
|---|---|---|
| Few-shot prompt building + CoT template | Built | `test_prompt_contains_examples_then_target`, `test_prompt_includes_cot_steps` |
| Deterministic field extraction | Built | `tests/test_extraction.py` (12 tests) |
| Five-check fabricated-value gate, blocking | Built | `tests/test_checks.py` (14 tests) |
| PII detect/redact (phone, SSN, card, email) + log/error proof | Built | `tests/test_pii.py` (15 tests) |
| View-aware SQLite authorizer + capped fetch | Built | `tests/test_store_authorizer.py` (17 tests) |
| Confirmation gates + named approvals | Built | `tests/test_gates.py` (15 tests) |
| Per-dataset quality report | Built | `tests/test_report_budget_email_brand.py` (report tests) |
| Negative-cost rejection, email dry-run policy, brand guard | Built | `tests/test_report_budget_email_brand.py` |
| Demo script with real output | Built | `examples/demo.py` |
| Brand check + 8-word overlap check scripts | Built | `scripts/brand_check.py`, `scripts/overlap_check.py` |
| Live-model extraction (provider calls, retries, evals) | Planned | Not built; no provider is named or claimed |
| Real mail transport | Planned | `email_channel.py` raises until one is supplied |
| Deployment, packaging, CI badges | Planned | Not claimed anywhere in this repo |
