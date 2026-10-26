# Knowledge: architecture (Mermaid)

```mermaid
flowchart TD
    subgraph Ingest
        T[Synthetic financial text]
    end
    subgraph Extract
        P[Few-shot prompt\nworked examples + target]
        C[Chain-of-thought template\n5 ordered steps]
        X[Deterministic parser\nlabelled figures only]
        P --> X
        C --> X
    end
    subgraph Validate
        V1[Range check]
        V2[Cross-field check]
        V3[Citation check]
        V4[Arithmetic check]
        V5[Stale check]
    end
    subgraph Protect
        R[PII redact\nphone, SSN, card, email]
        L[Safe log / safe error\nredacted diagnostics]
    end
    subgraph StoreGate
        S[SQLite views only\nstrict authorizer]
        G[Confirmation gate\n+ named approval]
    end
    Q[Data-quality report\npass rate, failures, PII, fitness]

    T --> P
    X --> V1 --> V2 --> V3 --> V4 --> V5
    V5 -->|pass| R --> S
    V5 -->|fail| B[Blocked: no downstream use]
    L --> S
    G --> S
    S --> Q
```

The same diagram in short form lives in `docs/architecture.md` and in
the README. The rule the diagram encodes: every stage can only narrow
what flows downstream.
