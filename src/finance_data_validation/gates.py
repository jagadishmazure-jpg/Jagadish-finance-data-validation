"""Confirmation gates and named-person approvals.

Rules enforced here, each with a test proving it:

* A gated action cannot run without a gate decision (bypass blocked).
* An explicit refusal is a rejection (reject path).
* No consent text at all is a rejection (absent path).
* Consent given with low confidence (below ``MIN_CONFIDENCE``) is a
  rejection, even when the words say yes (low-confidence path).
* Self-contradicting consent -- affirmation and refusal/retreat in the
  same utterance, e.g. "yes, wait, no" -- is a rejection.
* Approvals are named-person (a bare "system"/"admin" is not a person),
  single-use (consumed on first use), scoped (must match the action),
  and expiring (checked against the current time).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

MIN_CONFIDENCE = 0.7
_NON_PERSON = {"system", "auto", "admin", "bot", "service"}

_AFFIRM = re.compile(r"\b(yes|confirm|confirmed|approve|approved|proceed)\b")
_RETREAT = re.compile(r"\b(no|not|wait|stop|cancel|hold on|don't|do not)\b")


class GateError(Exception):
    """Raised when a gated action is refused or attempted improperly."""


@dataclass
class Approval:
    approver: str
    scope: str
    expires_at: datetime
    _used: bool = field(default=False, repr=False)

    def __post_init__(self):
        name = (self.approver or "").strip()
        if not name or name.lower() in _NON_PERSON or len(name) < 3:
            raise ValueError("approval requires a named person as approver")
        if not (self.scope or "").strip():
            raise ValueError("approval requires a non-empty scope")

    def is_valid(self, scope: str, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        return (not self._used and self.scope == scope
                and now < self.expires_at)

    def consume(self, scope: str, now: datetime | None = None) -> None:
        if not self.is_valid(scope, now):
            raise GateError("approval is expired, used, or out of scope")
        self._used = True


def make_approval(approver: str, scope: str,
                  ttl_minutes: int = 30) -> Approval:
    """Create a named-person, single-use, scoped, expiring approval."""
    return Approval(
        approver=approver, scope=scope,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes))


@dataclass
class GateDecision:
    approved: bool
    reason: str


class ConfirmationGate:
    """One gate per risky action. A decision is recorded, then checked."""

    def __init__(self, action: str):
        self.action = action
        self.decision: GateDecision | None = None

    def confirm(self, consent: str | None,
                confidence: float) -> GateDecision:
        if consent is None or not consent.strip():
            self.decision = GateDecision(False, "absent: no consent given")
        elif _AFFIRM.search(consent.lower()) and _RETREAT.search(consent.lower()):
            self.decision = GateDecision(
                False, "contradicting: affirmation and refusal both present")
        elif _RETREAT.search(consent.lower()) and not _AFFIRM.search(consent.lower()):
            self.decision = GateDecision(False, "rejected: consent refused")
        elif not _AFFIRM.search(consent.lower()):
            self.decision = GateDecision(
                False, "rejected: no explicit affirmation")
        elif confidence < MIN_CONFIDENCE:
            self.decision = GateDecision(
                False, f"low-confidence: {confidence} < {MIN_CONFIDENCE}")
        else:
            self.decision = GateDecision(True, "approved")
        return self.decision

    def execute(self, approval: Approval, fn, *args, **kwargs):
        """Run ``fn`` only with an approved decision and valid approval."""
        if self.decision is None or not self.decision.approved:
            raise GateError("bypass blocked: no approved gate decision")
        approval.consume(self.action)
        return fn(*args, **kwargs)
