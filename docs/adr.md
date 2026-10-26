# Architecture decision records

## ADR-1: Blocking, not warning, on failed checks

- **Context:** A failed check could warn and still release the value.
- **Decision:** Any failed check blocks the whole record
  (`usable_fields` is empty).
- **Consequence:** Consumers lose partially-good records; they gain a
  guarantee that released values passed every check. The trade-off is
  deliberate: a model cannot distinguish a warned value from a clean
  one once it is in the prompt.

## ADR-2: View-aware SQLite authorizer

- **Context:** Views alone are a convention; any caller can query the
  base table.
- **Decision:** Install an authorizer that allows base-table column
  reads only when SQLite reports an allowed view as the read's source.
- **Consequence:** Verified by experiment: view reads report the view
  as source, direct reads report none. Denial tests assert exception
  type only, since message text is engine-dependent.

## ADR-3: Fetch cap via fetchmany(MAX+1), never LIMIT rewriting

- **Context:** Capping could be done by rewriting SQL or slicing after
  `fetchall`.
- **Decision:** Fetch `MAX+1` rows and raise when the extra row exists.
- **Consequence:** Over-cap results are detected without loading the
  table, and the caller's SQL is never silently rewritten.

## ADR-4: Deterministic extraction, no live model

- **Context:** Few-shot/CoT patterns are usually demonstrated with a
  model call.
- **Decision:** Implement the patterns as prompt templates plus a
  deterministic regex extractor, stdlib only, offline.
- **Consequence:** The suite is reproducible and needs no credentials,
  but no model-capability claim is made. A live-model adapter is a
  planned, separate piece of work.

## ADR-5: Hash-stored brand blocklist

- **Context:** A plain-name blocklist would itself contain the names
  that must not appear.
- **Decision:** Store SHA-256 hashes; check text by hashing its
  1- to 4-word runs.
- **Consequence:** The guard works without leaking names, at the cost
  of an extra hashing step per check (negligible for doc-sized text).
