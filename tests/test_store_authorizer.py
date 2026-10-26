"""SQLite authorizer: view-only reads, everything else denied.

Note on assertions: denial tests assert the exception TYPE only, never
the error message text -- message wording is engine-dependent, so the
text check is deliberately disabled for these tests.
"""

import sqlite3

import pytest

from finance_data_validation.store import (
    MAX_ROWS, RowCapExceeded, create_store, fetch_capped,
)


def test_view_read_allowed():
    conn = create_store()
    rows = fetch_capped(conn, "v_validated_values")
    assert len(rows) == 3
    assert rows[0][1] == "synthetic-q3"


def test_quality_summary_view_allowed():
    conn = create_store()
    rows = fetch_capped(conn, "v_quality_summary")
    assert rows[0][0] == "synthetic-q3" and rows[0][1] == 3


def test_direct_base_table_read_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT * FROM validated_records").fetchall()


def test_direct_base_table_column_read_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT raw_note FROM validated_records").fetchall()


def test_sqlite_master_read_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT * FROM sqlite_master").fetchall()


def test_insert_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "INSERT INTO validated_records VALUES "
            "(9,'x','revenue',1.0,'USD','2026-07-15',1,'note')")


def test_update_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("UPDATE validated_records SET value=0 WHERE id=1")


def test_delete_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DELETE FROM validated_records WHERE id=1")


def test_drop_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("DROP TABLE validated_records")


def test_pragma_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("PRAGMA table_info(validated_records)").fetchall()


def test_attach_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("ATTACH ':memory:' AS other")


def test_create_table_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("CREATE TABLE rogue (id INTEGER)")


def test_unsafe_function_denied():
    conn = create_store()
    with pytest.raises(sqlite3.DatabaseError):
        conn.execute("SELECT abs(value) FROM v_validated_values").fetchall()


def test_unknown_view_fetch_refused_before_sql():
    conn = create_store()
    with pytest.raises(ValueError):
        fetch_capped(conn, "validated_records")


def test_row_cap_enforced_via_fetchmany():
    rows = [(i, "big", "revenue", 1.0, "USD", "2026-07-15", 1, "note")
            for i in range(1, MAX_ROWS + 5)]
    conn = create_store(rows)
    with pytest.raises(RowCapExceeded):
        fetch_capped(conn, "v_validated_values", max_rows=MAX_ROWS)


def test_row_cap_exactly_at_cap_passes():
    rows = [(i, "big", "revenue", 1.0, "USD", "2026-07-15", 1, "note")
            for i in range(1, MAX_ROWS + 1)]
    conn = create_store(rows)
    assert len(fetch_capped(conn, "v_validated_values",
                            max_rows=MAX_ROWS)) == MAX_ROWS


def test_row_cap_small_cap_on_default_seed():
    conn = create_store()
    assert len(fetch_capped(conn, "v_validated_values", max_rows=10)) == 3
    with pytest.raises(RowCapExceeded):
        fetch_capped(conn, "v_validated_values", max_rows=2)
