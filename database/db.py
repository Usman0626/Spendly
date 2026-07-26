import os
import sqlite3
from datetime import date, timedelta

from werkzeug.security import generate_password_hash

# Anchor the db file to the project root regardless of cwd: __file__ is
# .../expense-tracker/database/db.py, so two dirname() calls up reaches the
# same directory app.py lives in.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if row["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    first_of_month = date.today().replace(day=1)
    day_offsets = [1, 4, 7, 10, 13, 16, 19, 22]  # capped at 22 so it's valid even in Feb
    sample_expenses = [
        (45.50, "Food", "Grocery shopping at the farmers market"),
        (28.75, "Transport", "Uber ride to the airport"),
        (120.00, "Bills", "Monthly electricity bill"),
        (65.00, "Health", "Pharmacy prescription refill"),
        (15.99, "Entertainment", "Movie tickets"),
        (89.99, "Shopping", "New running shoes"),
        (20.00, "Other", "Donation to local charity"),
        (12.50, "Food", "Coffee and a pastry"),
    ]

    for offset, (amount, category, description) in zip(day_offsets, sample_expenses):
        expense_date = (first_of_month + timedelta(days=offset)).strftime("%Y-%m-%d")
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date, description)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, amount, category, expense_date, description),
        )

    conn.commit()
    conn.close()
