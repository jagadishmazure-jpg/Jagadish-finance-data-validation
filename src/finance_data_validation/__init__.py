"""Finance data validation: turn structured and unstructured financial
information into trustworthy inputs for AI systems.

All data handled by this package is SYNTHETIC unless a caller explicitly
supplies its own records. No live model, network call, or cloud service is
required. The package is standard-library only and runs fully offline.

Fictional firm used in examples and docs: Quillwick Ledger (invented for
this repo; it is not a real business).
"""

__all__ = [
    "extraction",
    "checks",
    "pii",
    "gates",
    "store",
    "report",
    "budget",
    "email_channel",
    "brand",
]
