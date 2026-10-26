# Guardrails and security controls

Every control below has a named proof test. If the README says something
is enforced, a test proves it.

| Control | Proof tests |
|---|---|
| View-aware SQLite authorizer: base reads only via allowed views | `test_direct_base_table_read_denied`, `test_direct_base_table_column_read_denied` |
| `sqlite_master` denied | `test_sqlite_master_read_denied` |
| Writes denied (insert/update/delete/drop/create) | `test_insert_denied`, `test_update_denied`, `test_delete_denied`, `test_drop_denied`, `test_create_table_denied` |
| PRAGMA / ATTACH denied | `test_pragma_denied`, `test_attach_denied` |
| Unsafe SQL functions denied; safe aggregates allowed | `test_unsafe_function_denied`, `test_quality_summary_view_allowed` |
| Gate bypass blocked | `test_gate_bypass_blocked_without_decision`, `test_gate_bypass_blocked_after_rejection` |
| Gate reject path | `test_gate_reject_path` |
| Gate absent path | `test_gate_absent_path_none`, `test_gate_absent_path_blank` |
| Gate low-confidence rejection | `test_gate_low_confidence_yes_rejected` |
| Gate self-contradicting consent ("yes, wait, no") | `test_gate_contradicting_consent_rejected`, `test_gate_contradicting_consent_blocks_execution` |
| Approvals named-person / single-use / scoped / expiring | `test_approval_requires_named_person`, `test_approval_single_use`, `test_approval_scoped`, `test_approval_expired` |
| PII redaction: phone, SSN, card, email | `test_redact_phone`, `test_redact_ssn`, `test_redact_card_number`, `test_redact_email`, `test_redact_all_four_leaves_no_raw_value` |
| Redaction in logs and errors | `test_safe_log_redacts_before_logging`, `test_safe_error_never_echoes_raw_pii` |
| Row cap via `fetchmany(MAX+1)` | `test_row_cap_enforced_via_fetchmany`, `test_row_cap_exactly_at_cap_passes`, `test_row_cap_small_cap_on_default_seed` |
| Negative-cost rejection | `test_negative_cost_rejected`, `test_budget_negative_spend_rejected`, `test_bool_cost_rejected`, `test_non_numeric_cost_rejected` |
| Non-empty brand blocklist (hashes) | `test_brand_blocklist_is_non_empty`, `test_brand_check_flags_blocklisted_name` |
| Fabricated-value blocking | `test_cross_field_mismatch_blocks`, `test_fabricated_record_fails_multiple_checks_and_is_blocked`, `test_arithmetic_mismatch_blocks`, `test_missing_citation_blocks` |
| Stale-data flagging | `test_stale_record_blocks`, `test_future_dated_record_flagged_stale`, `test_missing_date_flagged_stale` |
| Email dry-run default, opt-in, CI refusal | `test_email_dry_run_default_sends_nothing`, `test_email_send_requires_opt_in`, `test_email_send_refused_in_ci` |

Notes:

- Authorizer denial tests assert the exception *type* only, never the
  message text (engine wording varies; the text check is deliberately
  disabled for those tests).
- The brand blocklist is stored as SHA-256 hashes only, so the guard
  cannot itself leak the names it guards against.
- No credentials, tokens, or real personal data appear anywhere in the
  repo; PII fixtures in tests are synthetic (555 numbers, a test card
  number, example.com addresses).
