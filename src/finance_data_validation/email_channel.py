"""Email channel: dry-run by default, explicit opt-in to send.

* ``dry_run=True`` (the default) returns a preview and sends nothing.
* Sending requires ``opt_in=True``; without it, sending is refused.
* Sending is refused outright when the ``CI`` environment variable is
  set, so no automated run can ever mail anything.
* No credentials live in this repo and no mail transport is configured:
  even an opted-in, non-CI send raises until a transport is supplied.
  That gap is listed as Planned, not claimed as built.
"""

from __future__ import annotations

import os


class EmailRefused(Exception):
    """Raised when a send is refused by policy, not by a network error."""


def send_report_email(recipient: str, subject: str, body: str,
                      dry_run: bool = True, opt_in: bool = False,
                      transport=None) -> dict:
    preview = {"to": recipient, "subject": subject,
               "body_preview": body[:200], "dry_run": dry_run}
    if dry_run:
        preview["sent"] = False
        return preview
    if os.environ.get("CI"):
        raise EmailRefused("sending refused in CI")
    if not opt_in:
        raise EmailRefused("sending requires explicit opt_in=True")
    if transport is None:
        raise EmailRefused("no mail transport configured")
    transport(recipient, subject, body)
    preview["sent"] = True
    return preview
