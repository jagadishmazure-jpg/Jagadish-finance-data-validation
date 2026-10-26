# Finance Data Validation

> **Synthetic data only.** Every figure in this repo is invented for
> demonstration. Nothing here is real financial data, real personal data,
> or a claim about any real company. The fictional firm in examples is
> **Quillwick Ledger**, an invented name. This repo has no affiliation
> with any university, training provider, or financial institution.

## Recruiter summary

Finance teams cannot trust AI outputs built on unchecked numbers, so this
repo turns messy financial text into validated, redaction-clean inputs
before any downstream system sees them. It extracts labelled figures with
few-shot and chain-of-thought patterns (deterministic, no live model),
runs a five-check fabricated-value gate where any failure blocks the
record, redacts phone/SSN/card/email values before they can leave the
validation layer, and reports per-dataset fitness. Proof: **94 tests
green** (`python3 -m pytest tests/ -q`), including named adversarial
proofs for the SQLite authorizer, confirmation gates, PII redaction,
row caps, and negative-cost rejection — all offline, standard library
only.

## Purpose and who it is for

For engineers building AI features on top of financial documents: the
layer between "text arrived" and "value is trusted". It answers three
questions per record — is the figure internally consistent, is it
sourced and fresh, and is it clean of personal data — and refuses to
release the value when any answer is no.

## Architecture

```mermaid
flowchart LR
    A[Synthetic financial text] --> B[Extraction\nfew-shot + CoT templates]
    B --> C[Validation checklist\nrange, cross-field, citation,\narithmetic, stale]
    C -->|any check fails| D[BLOCKED\nusable_fields = {}]
    C -->|all pass| E[PII scan + redact\nphone, SSN, card, email]
    E --> F[View-only SQLite store\nstrict authorizer]
    F --> G[Data-quality report\npass rate, failures, PII hits]
    H[Confirmation gate +\nnamed-person approval] --> F
```

See [docs/architecture.md](docs/architecture.md) and
[knowledge/architecture.md](knowledge/architecture.md).

## How it works, step by step

1. **Extract.** `extraction.extract_fields` finds labelled figures
   (revenue, expenses, net income, assets, liabilities), the period,
   and the source citation, and records a reasoning trace. A few-shot
   prompt is built by `build_few_shot_prompt` for the same shape.
2. **Validate.** `checks.validate_record` runs five checks. Any failure
   sets `blocked=True` and empties `usable_fields` — there is no
   partial-release path.
3. **Redact.** `pii.redact` replaces phone, SSN, card (Luhn-verified),
   and email values; `safe_log`/`safe_error` redact before logging or
   raising, so raw values never leak through diagnostics.
4. **Store (view-only).** `store.create_store` seeds a SQLite database,
   then installs a strict authorizer: base-table reads are allowed only
   when SQLite reports an allowed view as the read's source; direct
   base reads, `sqlite_master`, writes, PRAGMA, ATTACH, and unsafe
   functions are denied.
5. **Gate releases.** `gates.ConfirmationGate` requires an explicit,
   high-confidence, non-contradicting consent plus a named-person,
   single-use, scoped, expiring approval before a gated action runs.
6. **Report.** `report.build_report` gives pass rate, failures by
   check type, PII hits, and a fitness verdict per dataset.

Full detail: [docs/how-it-works.md](docs/how-it-works.md).

## Real code excerpts and real output

Extraction (from `examples/demo.py`, run 2026-10-26, offline):

```
fields={'net_income': 180000.0, 'revenue': 500000.0, 'expenses': 320000.0} passed=True failed=[]
fields={'net_income': 999000.0, 'revenue': 400000.0, 'expenses': 250000.0} passed=False failed=['cross_field']
fields={'net_income': 100000.0, 'revenue': 300000.0, 'expenses': 200000.0} passed=False failed=['citation']
redacted: Contact [REDACTED:EMAIL] or [REDACTED:PHONE] about the note. hits={'phone': 1, 'email': 1}
{'dataset': 'synthetic-q3', 'total': 3, 'passed': 1, 'failed': 2, 'pass_rate': 0.3333,
 'failed_by_type': {'cross_field': 1, 'citation': 1}, 'pii_hits': {'phone': 1, 'email': 1},
 'pii_total': 2, 'fitness': 'not fit: PII present'}
```

The demo's 3-record set is a regression fixture, not a quality claim:
1 of 3 passed because the other two were deliberately built to fail
(one inconsistent net income, one missing citation).

Test proof (run 2026-10-26, system Python 3.12, `python3 -m pytest tests/ -q`):

```
94 passed in 0.16s
```

## How to run (offline first)

```bash
python3 -m pytest tests/ -q        # full suite, stdlib only, no network
python3 examples/demo.py           # extract -> validate -> redact -> report
python3 scripts/brand_check.py .   # hash-based brand/name guard over docs
```

No virtualenv is created inside the repo, no dependencies are installed,
and no cloud, deployment, or package release is involved. See
[docs/running.md](docs/running.md).

## Guardrails and security controls

- Strict view-aware SQLite authorizer (see above); denial tests assert
  exception type only, never message text.
- Confirmation gates: bypass / reject / absent / low-confidence /
  self-contradicting-consent paths all tested.
- Approvals: named person, single use, scoped, expiring.
- PII redaction checklist covers phone, SSN, **card numbers**, and
  **email addresses**; redaction proven in logs and errors.
- Row cap at fetch time via `fetchmany(MAX + 1)`; no LIMIT rewriting,
  no `fetchall` on capped fetches.
- Cost/budget inputs reject negatives (and booleans/non-numbers).
- Email channel: `dry_run=True` by default, explicit opt-in to send,
  refused in CI, no credentials in the repo, no transport configured.
- Brand/name guard: blocklist stored as SHA-256 hashes, asserted
  non-empty by a test.

Detail: [docs/guardrails.md](docs/guardrails.md),
[docs/threat-model.md](docs/threat-model.md).

## Limitations and known failures (kept visible as tests)

- The extractor is regex-based and deterministic: it only reads figures
  that follow a recognised label, and it cannot resolve ambiguous or
  footnote-carried figures. See [docs/limitations.md](docs/limitations.md).
- No live model is called: few-shot/CoT behaviour is a pattern, not a
  measured model capability.
- No real mail transport: opted-in sends raise until one is supplied.

## Built vs planned

| Area | Status |
|---|---|
| Few-shot + CoT extraction (deterministic) | Built |
| Five-check fabricated-value gate, blocking | Built |
| PII detect/redact incl. cards + emails, log/error proof | Built |
| View-aware SQLite authorizer + capped fetch | Built |
| Confirmation gates + named approvals | Built |
| Data-quality report per dataset | Built |
| Budget negative rejection, email dry-run policy | Built |
| Brand guard (hash blocklist), overlap check script | Built |
| Live-model extraction, real mail transport, cloud deploy | Planned (not claimed) |

See [docs/built-vs-planned.md](docs/built-vs-planned.md).

## Docs

- [docs/architecture.md](docs/architecture.md) · [docs/how-it-works.md](docs/how-it-works.md) · [docs/guardrails.md](docs/guardrails.md) · [docs/limitations.md](docs/limitations.md) · [docs/built-vs-planned.md](docs/built-vs-planned.md) · [docs/implementation-guide.md](docs/implementation-guide.md) · [docs/interview-points.md](docs/interview-points.md) · [docs/threat-model.md](docs/threat-model.md) · [docs/adr.md](docs/adr.md) · [docs/related-repos.md](docs/related-repos.md) · [docs/examples.md](docs/examples.md) · [docs/running.md](docs/running.md)
- [knowledge/notes.md](knowledge/notes.md) — distilled source patterns, in the author's own words; the source document itself is not committed.

## Related repos

Cross-links instead of duplication — see
[docs/related-repos.md](docs/related-repos.md). Neighbours in this
portfolio family include the PII-guard repo (detection/redaction
patterns), the document-intelligence repo (generic extraction/posting),
and the fraud-detection repo (alert triage, kept separate from
validation here).

## License

MIT — see [LICENSE](LICENSE). Security contact process: [SECURITY.md](SECURITY.md).
