# Security policy

## Reporting a vulnerability

This is a demonstration repo containing synthetic data only. If you
find a security issue in the code, please report it through the
repository's private vulnerability reporting channel (or, for a
scaffold without a live repo yet, to the repo owner directly). Do not
open a public issue with exploit details.

## What is protected here

- View-only SQLite access via a strict authorizer (see
  `docs/guardrails.md`).
- PII redaction before logs, errors, storage notes, and downstream
  release (phone, SSN, card numbers, email addresses).
- Confirmation gates with named-person, single-use, scoped, expiring
  approvals for gated releases.
- No credentials, tokens, or real personal data are stored in this
  repo; test PII fixtures are synthetic.

## Known limits

- The SQLite authorizer protects the application connection only; it
  is not a substitute for file permissions on any on-disk database.
- Approver identity proofing is the caller's responsibility.
- No mail transport is configured; opted-in sends raise until one is
  supplied.
