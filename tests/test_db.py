import sqlite3

import pytest
from werkzeug.security import check_password_hash


def test_init_db_creates_tables(isolated_db):
    conn = isolated_db.get_db()
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert {"users", "expenses"} <= tables


def test_init_db_is_idempotent(isolated_db):
    isolated_db.init_db()
    isolated_db.init_db()


def test_seed_db_inserts_demo_user_and_expenses(isolated_db):
    isolated_db.seed_db()
    conn = isolated_db.get_db()

    users = conn.execute("SELECT * FROM users").fetchall()
    assert len(users) == 1
    assert users[0]["email"] == "demo@spendly.com"

    expenses = conn.execute("SELECT * FROM expenses").fetchall()
    conn.close()
    assert len(expenses) == 8

    categories = {row["category"] for row in expenses}
    assert categories == set(isolated_db.CATEGORIES)

    for row in expenses:
        assert len(row["date"]) == 10 and row["date"][4] == "-" and row["date"][7] == "-"


def test_seed_db_password_is_hashed(isolated_db):
    isolated_db.seed_db()
    conn = isolated_db.get_db()
    user = conn.execute("SELECT password_hash FROM users").fetchone()
    conn.close()

    assert user["password_hash"] != "demo123"
    assert check_password_hash(user["password_hash"], "demo123")


def test_seed_db_is_idempotent(isolated_db):
    isolated_db.seed_db()
    isolated_db.seed_db()

    conn = isolated_db.get_db()
    user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    expense_count = conn.execute("SELECT COUNT(*) AS c FROM expenses").fetchone()["c"]
    conn.close()

    assert user_count == 1
    assert expense_count == 8


def test_unique_email_constraint(isolated_db):
    isolated_db.seed_db()
    conn = isolated_db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Someone Else", "demo@spendly.com", "x"),
        )
    conn.close()


def test_foreign_key_enforcement(isolated_db):
    conn = isolated_db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (99999, 10.0, "Food", "2026-01-01", "bad fk"),
        )
    conn.close()
