"""SQLite database wrapper."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path


class Database:
    """Lightweight DB helper for connecting and initializing schema."""
    _IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
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
        self._assert_identifier(table, "table")
        self._assert_identifier(column, "column")
        columns = {
            row["name"]
            for row in conn.execute(f"PRAGMA table_info({self._quote_identifier(table)})").fetchall()
        }
        if column not in columns:
            conn.execute(
                "ALTER TABLE "
                + self._quote_identifier(table)
                + " ADD COLUMN "
                + self._quote_identifier(column)
                + f" {column_type} DEFAULT {default_value}"
            )

    def _assert_identifier(self, value: str, label: str) -> None:
        if not self._IDENTIFIER_RE.match(value):
            raise ValueError(f"Invalid {label} identifier: {value}")

    def _quote_identifier(self, value: str) -> str:
        return f'"{value}"'
