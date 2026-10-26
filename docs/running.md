# How to run (offline first)

Prerequisites: Python 3.10+ and pytest. No third-party packages, no
network, no credentials, no cloud account.

```bash
# From the repo root:
python3 -m pytest tests/ -q        # full suite (94 tests)
python3 examples/demo.py           # extract -> validate -> redact -> report
python3 scripts/brand_check.py .   # hash-based brand/name guard over docs
python3 scripts/overlap_check.py /path/to/source-text.txt .
#   (the source text file is held privately and is never committed)
```

Notes:

- `tests/conftest.py` adds `src/` to `sys.path`; no install step and
  no virtualenv inside the repo are needed.
- Do not create a `.venv` inside the scaffold.
- No `.github/workflows` files are shipped in the scaffold; CI is a
  standardisation step owned by the second writer at push time.
- Test counts: run the suite and read its summary line; do not quote
  a count from this document without re-running.
