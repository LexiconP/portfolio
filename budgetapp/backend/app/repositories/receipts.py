from __future__ import annotations

from typing import Any

from ..core.database import Database
from ..core.interfaces import IReceiptRepository


class ReceiptRepository(IReceiptRepository):
    def __init__(self, db: Database) -> None:
        self._db = db

    def insert_receipt(
        self,
        date: str | None,
        vendor: str,
        total: float,
        image_path: str,
        ocr_text: str,
        created_at: str,
    ) -> int:
        with self._db.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO receipts (date, vendor, total, image_path, ocr_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (date, vendor, total, image_path, ocr_text, created_at),
            )
            return int(cursor.lastrowid)

    def list_receipts(self) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT id, date, vendor, total, created_at FROM receipts ORDER BY id DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_receipt(self, receipt_id: int) -> dict[str, Any] | None:
        with self._db.connect() as conn:
            row = conn.execute(
                "SELECT * FROM receipts WHERE id = ?",
                (receipt_id,),
            ).fetchone()
        return dict(row) if row else None

    def export_rows(self) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT date, vendor, total, created_at FROM receipts ORDER BY id DESC"
            ).fetchall()
        return [dict(row) for row in rows]
