# Architecture

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

Module map (all under `src/finance_data_validation/`):

| Module | Responsibility |
|---|---|
| `extraction.py` | Few-shot prompt building, CoT template, deterministic field parsing |
| `checks.py` | Five-check fabricated-value gate; blocking semantics |
| `pii.py` | Detection + redaction; log/error safety |
| `store.py` | View-aware authorizer; capped fetch |
| `gates.py` | Confirmation gates; named-person approvals |
| `report.py` | Per-dataset quality report + fitness verdict |
| `budget.py` | Negative-cost rejection; capped spend ledger |
| `email_channel.py` | Dry-run-by-default reporting channel |
| `brand.py` | Hash-based blocklist guard |

Design rule: each stage can only narrow what flows downstream. Validation
can block, PII can redact, the authorizer can deny, a gate can refuse —
no stage can widen access granted by an earlier one.
