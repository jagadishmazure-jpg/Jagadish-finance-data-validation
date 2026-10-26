# Threat model

## STRIDE

| Threat | Where | Mitigation in this repo |
|---|---|---|
| Spoofing — a caller poses as an approver | `gates.py` | Approvals require a named person; bare "system"/"admin" rejected. (Identity proofing itself is the caller's job — see limitations.) |
| Tampering — a bad value is edited into a good record | `store.py` | Writes denied after seeding via the authorizer. |
| Repudiation — a release happens with no record | `gates.py` | Gate decisions and approval consumption are explicit objects; callers should log them (see implementation guide). |
| Information disclosure — PII leaves the layer | `pii.py` | Redaction before storage notes, logs, errors, and downstream release; card + email included, not just phone/SSN. |
| Denial of service — unbounded fetch | `store.py` | `fetchmany(MAX+1)` cap; over-cap raises instead of loading. |
| Elevation of privilege — direct table read bypasses views | `store.py` | Authorizer denies base-table reads without a view source; `sqlite_master` denied. |

## OWASP LLM Top 10 (relevant items)

- **LLM01 Prompt injection:** extraction inputs are data, never
  instructions to this package — the package makes no model calls, so
  injected text cannot steer a model through it. Adopters wiring a
  model behind `build_few_shot_prompt` must treat extracted text as
  untrusted input to that model.
- **LLM02 Sensitive information disclosure:** PII redaction layer
  (above); logs and errors are redacted by construction.
- **LLM06 Excessive agency:** gated releases — no downstream action
  runs without an approved gate decision plus a valid approval.
- **LLM09 Misinformation:** the fabricated-value checklist is the
  direct countermeasure: range, cross-field, citation, arithmetic, and
  staleness checks, all blocking.

## Out of scope

- Authentication/identity proofing of approvers (caller-provided).
- File-system protection of any on-disk database (the shipped store
  is in-memory).
- Model-side safety for adopters who attach a live model (see LLM01).
