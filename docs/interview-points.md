# Interview points

- **Why block instead of warn?** A downstream model cannot tell a
  "warning" from a value. Once a fabricated figure enters a prompt, it
  is quoted with the same confidence as a real one. Blocking at the
  validation layer is the only point where the distinction still
  exists, so `usable_fields` is empty for any failed record.
- **Why view-aware, not just "don't query the table"?** Convention
  breaks under pressure; the authorizer makes the wrong query fail
  instead of relying on every future caller remembering the rule.
  SQLite reports the view name as the source of base-table columns
  read through a view, which is exactly the signal the authorizer
  keys on — verified by experiment, not assumed.
- **Why does the authorizer allow COUNT/SUM but deny other functions?**
  The summary view needs aggregates to work. Denying all functions
  broke it (found by a failing test during the build); the fix is an
  explicit safe allowlist, with everything else denied.
- **Why assert exception type, not message, for denials?** Engine
  message wording varies across SQLite builds. Asserting on text would
  make the test suite brittle without making the control stronger.
- **Why Luhn-check card candidates?** Long digit runs are common in
  finance (references, totals). Without Luhn, the redactor would mangle
  legitimate figures; with it, only plausible card numbers are hit.
- **Why is "yes, wait, no" a rejection, not a yes?** Consent that
  contradicts itself in one utterance is not consent — it is evidence
  the speaker changed their mind mid-sentence. Treating the first word
  as decisive would execute an action the user just retracted.
- **Why dry-run email by default?** A validation library must never
  become a mail sender by accident. Sending needs an explicit opt-in,
  is refused in CI, and still raises without a configured transport.
- **Honest numbers.** The demo's 33% pass rate is a fixture property
  (two of three records were built to fail), not a quality claim. The
  honest claim is the test count: 94 tests green, offline, stdlib only.
