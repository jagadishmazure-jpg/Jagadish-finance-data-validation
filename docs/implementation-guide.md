# Implementation guide (for adopters)

## Adopt the layer in order

1. **Extract first, trust later.** Run `extract_fields` on incoming
   text and keep its reasoning trace next to the fields. If a field is
   absent, treat it as absent — do not backfill it from another source
   without a new validation pass.
2. **Validate before storing anything downstream.** Build a
   `FinancialRecord` (values, line items + stated total, citation,
   record date) and call `validate_record` with your reference date.
   Release only `usable_fields`, and only when `blocked` is false.
3. **Redact before logging, storing notes, or emailing.** Pass every
   free-text string through `pii.redact` first, and use `safe_log` /
   `safe_error` for diagnostics. Check the returned hit counts: any
   hit means the source text was dirty, which belongs in the quality
   report, not silently dropped.
4. **Expose views, not tables.** Seed through `create_store` (or your
   own loader that installs the same authorizer before handing the
   connection out), and serve reads through `fetch_capped` only.
5. **Gate releases.** Wrap any "release to a model / partner / report"
   action in a `ConfirmationGate` with a `make_approval` approval from
   a named person. Re-confirm per release: approvals are single-use.
6. **Report fitness per dataset.** Call `build_report` with the
   validation results and the PII hit totals, and surface its fitness
   verdict to consumers before they consume the dataset.

## Tuning points

- `STALE_AFTER_DAYS` (180) and `MAX_VALUE` in `checks.py`: set them to
  your domain's freshness and scale expectations.
- `MIN_CONFIDENCE` (0.7) in `gates.py`: raise it for higher-stakes
  releases.
- `MAX_ROWS` (100) in `store.py`: the fetch cap for view reads.
- `FIT_PASS_RATE` (0.9) in `report.py`: the fitness threshold.

## What not to do

- Do not call `fetchall` on an uncapped query and then slice in Python;
  the cap exists to bound memory and exposure at fetch time.
- Do not log `record.values` or raw text on a validation failure; use
  `safe_error`.
- Do not reuse an approval across actions or people; scope and
  single-use are the point.
