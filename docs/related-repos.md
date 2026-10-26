# Related repos

Cross-links instead of duplication: this repo covers validation of
financial values before use. Neighbouring concerns live elsewhere in
the portfolio family, and are linked here rather than re-implemented.

- **PII guard repo** — general-purpose PII detection/redaction
  patterns (phone, SSN, card, email) and redaction-proof logging. This
  repo applies those patterns specifically to the financial validation
  layer; the general pattern library stays there.
- **Document intelligence repo** — generic extraction and posting from
  documents. This repo's extractor is finance-specific (labelled
  figures, cross-field arithmetic, citation/staleness gates) and does
  not duplicate the generic pipeline.
- **Fraud detection repo** — alert triage and fraud-pattern detection.
  Validation here is about whether a value is trustworthy, not whether
  a transaction is fraudulent; the two checks are complementary and
  deliberately kept separate.
- **Compliance/RAG, KYC/AML, credit-memo, portfolio-risk, and
  invoice-reimbursement repos** (sibling finance builds) — consumers
  of validated data. Each should validate through a layer like this
  one before consuming values, rather than re-implementing checks.
