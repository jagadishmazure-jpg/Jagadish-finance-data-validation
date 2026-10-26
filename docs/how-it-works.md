# How it works, step by step

## 1. Extraction

`build_few_shot_prompt(text)` assembles worked input/output pairs, the
fixed five-step reasoning template, then the target text. The template
order matters: list labelled figures first, match each figure once,
recompute totals, record the citation (or its absence), and never invent
a missing field.

`extract_fields(text)` applies the same rules deterministically with
regular expressions. A dollar-prefixed amount is preferred over a bare
number, so a year or note number sitting between a label and its amount
does not get mistaken for the figure. Negative amounts written with a
leading minus are kept negative.

## 2. Validation

`validate_record(record, reference_date)` runs, in order: range,
cross-field, citation, arithmetic, stale. The result carries every
check, and `blocked` is true when any check failed. `usable_fields`
returns the record's values only when nothing failed — otherwise it is
an empty dict. There is no "release the good fields of a bad record"
path: a record is a unit, and a failed record contributes nothing
downstream.

Staleness: a record older than 180 days before the reference date, a
record dated in the future, and a record with no date at all all fail
the stale check.

## 3. Redaction

`redact(text)` scans cards first (digit runs of 13–19 digits that pass
a Luhn check), then phone, SSN, and email patterns, replacing each hit
with a typed token such as `[REDACTED:CARD]`. It returns the cleaned
text plus per-category hit counts. `safe_log` and `safe_error` apply the
same redaction before a string reaches a log line or an error message.

## 4. Storage and gated release

`create_store(rows)` creates the base table and two views, seeds rows,
then installs the authorizer. After that point the connection refuses
direct base-table reads (SQLite reports no view as their source),
`sqlite_master` reads, all writes, PRAGMA, ATTACH/DETACH, and SQL
functions outside a small safe allowlist (COUNT, SUM, AVG, MIN, MAX,
COALESCE, LOWER, UPPER — needed by the summary view).

`fetch_capped(conn, view, max_rows)` fetches with
`fetchmany(max_rows + 1)` and raises `RowCapExceeded` when the result
would exceed the cap. It never rewrites the query with LIMIT and never
calls `fetchall` on a capped fetch.

`ConfirmationGate.confirm(consent, confidence)` classifies consent as
approved, rejected, absent, low-confidence, or contradicting; `execute`
runs the action only with an approved decision and a valid approval
(named person, unused, matching scope, unexpired).

## 5. Reporting

`build_report(dataset, results, pii_hits)` counts totals, pass rate
(rounded to 4 decimals), failures by check name, and PII hits, and
assigns fitness: `fit for use` (pass rate >= 0.9 and zero PII),
`review required`, `not fit: PII present`, or `not fit: empty dataset`.
