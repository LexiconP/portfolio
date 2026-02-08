"""SQLite database wrapper."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    """Lightweight DB helper for connecting and initializing schema."""
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def connect(self) -> sqlite3.Connection:
        # Row factory allows dict-like access to columns.
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self) -> None:
        # Create tables if they do not already exist.
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    vendor TEXT,
                    total REAL,
                    image_path TEXT,
                    ocr_text TEXT,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT UNIQUE,
                    monthly_limit REAL DEFAULT 0,
                    spent REAL DEFAULT 0,
                    prior_balance REAL DEFAULT 0
                );
                """
            )
            self._ensure_column(conn, "budgets", "prior_balance", "REAL", "0")

    def _ensure_column(
        self,
        conn: sqlite3.Connection,
        table: str,
        column: str,
        column_type: str,
        default_value: str,
    ) -> None:
        columns = {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        if column not in columns:
            conn.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {column_type} DEFAULT {default_value}"
            )
