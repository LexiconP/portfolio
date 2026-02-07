from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Any, Protocol


class IOcrService(Protocol):
    def extract_text(self, image_path: Path) -> str:
        ...


class ReceiptParseResult(Protocol):
    date: str | None
    vendor: str
    total: float


class IReceiptParser(Protocol):
    def parse(self, text: str) -> ReceiptParseResult:
        ...


class IReceiptRepository(Protocol):
    def insert_receipt(
        self,
        date: str | None,
        vendor: str,
        total: float,
        image_path: str,
        ocr_text: str,
        created_at: str,
    ) -> int:
        ...

    def list_receipts(self) -> list[dict[str, Any]]:
        ...

    def get_receipt(self, receipt_id: int) -> dict[str, Any] | None:
        ...

    def export_rows(self) -> list[dict[str, Any]]:
        ...


class IBudgetRepository(Protocol):
    def list_budgets(self) -> list[dict[str, Any]]:
        ...

    def upsert_budget(self, category: str, monthly_limit: float, spent: float) -> dict[str, Any]:
        ...


class IReceiptService(Protocol):
    def create_receipt(self, contents: bytes) -> dict[str, Any]:
        ...

    def list_receipts(self) -> list[dict[str, Any]]:
        ...

    def get_receipt(self, receipt_id: int) -> dict[str, Any] | None:
        ...

    def export_csv(self) -> StringIO:
        ...


class IBudgetService(Protocol):
    def list_budgets(self) -> list[dict[str, Any]]:
        ...

    def upsert_budget(self, category: str, monthly_limit: float, spent: float) -> dict[str, Any]:
        ...
