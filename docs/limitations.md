# Limitations and known failures

These are kept visible rather than smoothed over. Each is a known miss
with a test or a documented boundary, not a silent gap.

- **Regex extraction, not a model.** The extractor only reads figures
  that follow a recognised label within a short window. Figures carried
  in footnotes, tables, or ambiguous phrasing ("the larger figure") are
  missed, and a missed field is emitted as absent — never guessed.
  (See `test_extract_emits_only_found_fields`.)
- **No measured model behaviour.** Few-shot and chain-of-thought
  patterns are implemented as templates and deterministic parsing. No
  claim is made about how any live model would perform on this task.
- **Plausibility band is coarse.** The range check uses a single wide
  band (up to 1 trillion in the record's currency). It catches absurd
  values, not subtly wrong ones; cross-field and arithmetic checks carry
  the precision.
- **Staleness threshold is a policy choice.** 180 days is the repo's
  default, not a regulatory rule. Callers with a different freshness
  requirement must pass their own reference date and threshold.
- **Card detection needs a Luhn pass.** A mistyped or partial card
  number that fails Luhn is not counted as a card hit. That trades a
  small false-negative risk for far fewer false positives on long
  reference numbers.
- **SQLite authorizer scope.** The authorizer protects this connection
  only. Anyone with the underlying file or a fresh connection bypasses
  it — it is a defence-in-depth control for the application layer, not
  a substitute for file permissions.
- **No real mail transport.** Opted-in sends raise until a transport is
  supplied; the dry-run path is the only working path today.
- **Small fixtures.** Demo and test datasets are hand-written
  regression fixtures (the demo uses 3 records). Pass rates on them
  describe the fixtures, not real-world data quality.
