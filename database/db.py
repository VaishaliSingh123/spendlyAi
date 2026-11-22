import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# Project root is one level above this file's directory.
# expense_tracker.db is already listed in .gitignore.
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "expense_tracker.db",
)

CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Return a SQLite connection with dict-like rows and foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create the users and expenses tables. Safe to call repeatedly."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                amount      REAL    NOT NULL,
                category    TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                description TEXT,
                created_at  TEXT    DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and 8 sample expenses, only if no users exist."""
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (
                "Demo User",
                "demo@spendly.com",
                generate_password_hash("demo123"),
            ),
        )
        user_id = cursor.lastrowid

        # Fixed days <= 28 are valid in every month and fall in the current month.
        today = date.today()
        samples = [
            ("Food", 450.00, 2, "Groceries"),
            ("Transport", 120.50, 5, "Metro card recharge"),
            ("Bills", 1500.00, 9, "Electricity bill"),
            ("Health", 300.00, 12, "Pharmacy"),
            ("Entertainment", 250.00, 15, "Movie tickets"),
            ("Shopping", 1200.00, 18, "Clothing"),
            ("Other", 80.00, 21, "Miscellaneous"),
            ("Food", 320.75, 25, "Restaurant dinner"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [
                (
                    user_id,
                    amount,
                    category,
                    today.replace(day=day).strftime("%Y-%m-%d"),
                    description,
                )
                for category, amount, day, description in samples
            ],
        )
        conn.commit()
    finally:
        conn.close()
