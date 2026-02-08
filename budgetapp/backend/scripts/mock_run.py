from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.core.config import AppConfig
from app.core.database import Database
from app.repositories.budgets import BudgetRepository
from app.repositories.receipts import ReceiptRepository
from app.services.budgets import BudgetService
from app.services.receipts import ReceiptService


@dataclass
class DummyOcrService:
    text: str

    def extract_text(self, image_path: Path) -> str:
        return self.text


@dataclass
class DummyParserResult:
    vendor: str
    date: str | None
    total: float


@dataclass
class DummyReceiptParser:
    result: DummyParserResult

    def parse(self, text: str) -> DummyParserResult:
        return self.result


def build_config(base_dir: Path) -> AppConfig:
    data_dir = base_dir / "data"
    receipts_dir = data_dir / "receipts"
    static_dir = base_dir / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    return AppConfig(
        base_dir=base_dir,
        data_dir=data_dir,
        receipts_dir=receipts_dir,
        db_path=data_dir / "app.db",
        static_dir=static_dir,
    )


def run_mock() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        config = build_config(base_dir)
        config.ensure_directories()

        db = Database(config.db_path)
        db.init()

        receipt_repository = ReceiptRepository(db)
        budget_repository = BudgetRepository(db)

        receipt_service = ReceiptService(
            repository=receipt_repository,
            config=config,
            ocr_service=DummyOcrService(text="TOTAL 12.34\n2024-01-02"),
            parser=DummyReceiptParser(
                result=DummyParserResult(
                    vendor="Synthetic Store",
                    date="2024-01-02",
                    total=12.34,
                )
            ),
        )
        budget_service = BudgetService(repository=budget_repository)

        receipt_service.create_receipt(b"synthetic-image-bytes")
        receipt_service.create_receipt(b"more-synthetic-bytes")

        budget_service.upsert_budget("Food", 300.0, 120.0)
        budget_service.upsert_budget("Travel", 800.0, 250.0)

        receipts = receipt_service.list_receipts()
        budgets = budget_service.list_budgets()
        csv_output = receipt_service.export_csv().getvalue()

        print("Receipts:")
        for receipt in receipts:
            print(receipt)

        print("\nBudgets:")
        for budget in budgets:
            print(budget)

        print("\nCSV Export:\n" + csv_output)


if __name__ == "__main__":
    run_mock()
