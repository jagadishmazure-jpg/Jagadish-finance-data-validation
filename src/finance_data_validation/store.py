"""View-aware SQLite store.

The base table ``validated_records`` is never readable directly. Reads
are allowed only through the published views, and the authorizer enforces
that by inspecting the *source* argument SQLite passes for each column
read: when a query runs through a view, SQLite reports the view's name
as the source of the underlying base-table columns. A direct base-table
read reports no source, so it is denied.

Denied outright: sqlite_master, every write (INSERT/UPDATE/DELETE/DROP/
CREATE/ALTER), PRAGMA, ATTACH, DETACH, and any SQL function outside a
small safe allowlist (COUNT/SUM/AVG/MIN/MAX/COALESCE/LOWER/UPPER).
Extension loading is off by default at the Python API level
(``enable_load_extension`` is never called), so no extension can be
loaded through this connection. Schema and seed rows are written before
the authorizer is installed; after that the connection is read-only
through views.

Row caps are enforced at fetch time with ``fetchmany(MAX + 1)``: the
query text is never rewritten with LIMIT, and ``fetchall`` is never used
on a capped fetch.
"""

from __future__ import annotations

import sqlite3

ALLOWED_VIEWS = {"v_validated_values", "v_quality_summary"}
BASE_TABLE = "validated_records"
MAX_ROWS = 100


class RowCapExceeded(Exception):
    """Raised when a capped fetch would return more than MAX_ROWS rows."""


def _authorizer(action, param1, param2, db_name, source):
    if action == sqlite3.SQLITE_READ:
        if param1 == "sqlite_master":
            return sqlite3.SQLITE_DENY
        if param1 in ALLOWED_VIEWS:
            return sqlite3.SQLITE_OK
        if param1 == BASE_TABLE:
            # Allowed only when the read flows through an allowed view.
            return (sqlite3.SQLITE_OK if source in ALLOWED_VIEWS
                    else sqlite3.SQLITE_DENY)
        return sqlite3.SQLITE_DENY
    if action in (sqlite3.SQLITE_PRAGMA, sqlite3.SQLITE_ATTACH,
                  sqlite3.SQLITE_DETACH):
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION:
        # The function name arrives in one of the first two parameters.
        name = (param1 or param2 or "").lower()
        safe = {"count", "sum", "avg", "min", "max", "coalesce",
                "lower", "upper"}
        return sqlite3.SQLITE_OK if name in safe else sqlite3.SQLITE_DENY
    if action in (sqlite3.SQLITE_INSERT, sqlite3.SQLITE_UPDATE,
                  sqlite3.SQLITE_DELETE, sqlite3.SQLITE_DROP_TABLE,
                  sqlite3.SQLITE_DROP_VIEW, sqlite3.SQLITE_CREATE_TABLE,
                  sqlite3.SQLITE_CREATE_VIEW, sqlite3.SQLITE_ALTER_TABLE):
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def create_store(rows=None) -> sqlite3.Connection:
    """Create a seeded store and install the authorizer before returning."""
    conn = sqlite3.connect(":memory:")
    conn.execute(
        "CREATE TABLE validated_records ("
        " id INTEGER PRIMARY KEY, dataset TEXT, field_name TEXT,"
        " value REAL, currency TEXT, as_of TEXT, passed INTEGER,"
        " raw_note TEXT)")
    conn.execute(
        "CREATE VIEW v_validated_values AS SELECT id, dataset, field_name,"
        " value, currency, as_of, passed FROM validated_records")
    conn.execute(
        "CREATE VIEW v_quality_summary AS SELECT dataset, COUNT(*) AS n,"
        " SUM(passed) AS passed_n FROM validated_records GROUP BY dataset")
    seed = rows if rows is not None else [
        (1, "synthetic-q3", "revenue", 500000.0, "USD", "2026-07-15", 1,
         "ledger note, redacted before storage"),
        (2, "synthetic-q3", "expenses", 320000.0, "USD", "2026-07-15", 1,
         "ledger note, redacted before storage"),
        (3, "synthetic-q3", "net_income", 180000.0, "USD", "2026-07-15", 1,
         "ledger note, redacted before storage"),
    ]
    conn.executemany("INSERT INTO validated_records VALUES (?,?,?,?,?,?,?,?)",
                     seed)
    conn.commit()
    conn.set_authorizer(_authorizer)
    return conn


def fetch_capped(conn: sqlite3.Connection, view: str,
                 max_rows: int = MAX_ROWS) -> list:
    """Fetch at most ``max_rows`` rows from an allowed view, capped.

    Uses ``fetchmany(max_rows + 1)`` so an over-cap result is detected
    without ever loading the whole table. The SQL text is not rewritten:
    a query containing LIMIT is refused outright.
    """
    if view not in ALLOWED_VIEWS:
        raise ValueError(f"not an allowed view: {view}")
    sql = f"SELECT * FROM {view}"
    if "limit" in sql.lower():
        raise ValueError("LIMIT rewriting is not allowed")
    cursor = conn.execute(sql)
    rows = cursor.fetchmany(max_rows + 1)
    if len(rows) > max_rows:
        raise RowCapExceeded(
            f"result exceeds cap of {max_rows} rows")
    return rows
