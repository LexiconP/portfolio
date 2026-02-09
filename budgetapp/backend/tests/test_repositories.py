from __future__ import annotations

from pathlib import Path

from app.core.database import Database
from app.repositories.budgets import BudgetRepository
from app.repositories.receipts import ReceiptRepository


def build_db(tmp_path: Path) -> Database:
    db_path = tmp_path / "app.db"
    db = Database(db_path)
    db.init()
    return db


def test_receipt_repository_crud(tmp_path: Path) -> None:
    db = build_db(tmp_path)
    repository = ReceiptRepository(db)

    first_id = repository.insert_receipt(
        "2024-01-01",
        "Store A",
        12.50,
        "/tmp/receipt_a.png",
        "OCR A",
        "2024-01-02T00:00:00",
    )
    second_id = repository.insert_receipt(
        "2024-01-03",
        "Store B",
        22.00,
        "/tmp/receipt_b.png",
        "OCR B",
        "2024-01-04T00:00:00",
    )

    assert first_id != second_id

    listed = repository.list_receipts()
    assert [row["id"] for row in listed] == [second_id, first_id]

    fetched = repository.get_receipt(first_id)
    assert fetched is not None
    assert fetched["vendor"] == "Store A"
    assert fetched["ocr_text"] == "OCR A"

    export_rows = repository.export_rows()
    assert export_rows[0]["vendor"] == "Store B"


def test_budget_repository_upsert_and_list(tmp_path: Path) -> None:
    db = build_db(tmp_path)
    repository = BudgetRepository(db)

    repository.upsert_budget("Food", 200.0, 75.0, 10.0)
    repository.upsert_budget("Travel", 500.0, 125.0, 5.0)
    repository.upsert_budget("Food", 250.0, 90.0, 15.0)

    rows = repository.list_budgets()

    assert [row["category"] for row in rows] == ["Food", "Travel"]
    assert rows[0]["monthly_limit"] == 250.0
    assert rows[0]["spent"] == 90.0
    assert rows[0]["prior_balance"] == 15.0
