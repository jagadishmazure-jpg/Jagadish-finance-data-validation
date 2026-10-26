"""Confirmation gates and approvals: bypass, reject, absent, low
confidence, contradicting consent, and named/expiring/scoped approvals."""

from datetime import datetime, timedelta, timezone

import pytest

from finance_data_validation.gates import (
    Approval, ConfirmationGate, GateError, make_approval,
)


def _gate_with_consent(consent, confidence=0.95):
    gate = ConfirmationGate("release_values")
    gate.confirm(consent, confidence)
    return gate


def test_gate_bypass_blocked_without_decision():
    gate = ConfirmationGate("release_values")
    approval = make_approval("Priya Raman", "release_values")
    with pytest.raises(GateError):
        gate.execute(approval, lambda: "ran")


def test_gate_bypass_blocked_after_rejection():
    gate = _gate_with_consent("no")
    approval = make_approval("Priya Raman", "release_values")
    with pytest.raises(GateError):
        gate.execute(approval, lambda: "ran")


def test_gate_reject_path():
    gate = _gate_with_consent("no, do not release")
    assert gate.decision.approved is False
    assert "rejected" in gate.decision.reason


def test_gate_absent_path_none():
    gate = _gate_with_consent(None)
    assert gate.decision.approved is False
    assert "absent" in gate.decision.reason


def test_gate_absent_path_blank():
    gate = _gate_with_consent("   ")
    assert gate.decision.approved is False


def test_gate_low_confidence_yes_rejected():
    gate = _gate_with_consent("yes, release it", confidence=0.3)
    assert gate.decision.approved is False
    assert "low-confidence" in gate.decision.reason


def test_gate_confidence_at_threshold_passes():
    gate = _gate_with_consent("yes, release it", confidence=0.7)
    assert gate.decision.approved is True


def test_gate_contradicting_consent_rejected():
    gate = _gate_with_consent("yes, wait, no")
    assert gate.decision.approved is False
    assert "contradicting" in gate.decision.reason


def test_gate_contradicting_consent_blocks_execution():
    gate = _gate_with_consent("yes, wait, no")
    approval = make_approval("Priya Raman", "release_values")
    with pytest.raises(GateError):
        gate.execute(approval, lambda: "ran")


def test_gate_clean_yes_executes():
    gate = _gate_with_consent("yes, release it", confidence=0.95)
    approval = make_approval("Priya Raman", "release_values")
    assert gate.execute(approval, lambda: "ran") == "ran"


def test_approval_requires_named_person():
    for bad in ("", "system", "admin", "bot"):
        with pytest.raises(ValueError):
            make_approval(bad, "release_values")


def test_approval_single_use():
    gate = _gate_with_consent("yes")
    approval = make_approval("Priya Raman", "release_values")
    gate.execute(approval, lambda: "first")
    gate2 = _gate_with_consent("yes")
    with pytest.raises(GateError):
        gate2.execute(approval, lambda: "second")


def test_approval_scoped():
    gate = ConfirmationGate("release_values")
    gate.confirm("yes", 0.95)
    approval = make_approval("Priya Raman", "other_scope")
    with pytest.raises(GateError):
        gate.execute(approval, lambda: "ran")


def test_approval_expired():
    gate = ConfirmationGate("release_values")
    gate.confirm("yes", 0.95)
    approval = Approval(
        approver="Priya Raman", scope="release_values",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1))
    with pytest.raises(GateError):
        gate.execute(approval, lambda: "ran")


def test_approval_not_yet_expired_is_valid():
    approval = make_approval("Priya Raman", "release_values")
    assert approval.is_valid("release_values") is True
