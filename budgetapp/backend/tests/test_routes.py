from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import build_router
from app.core.config import AppConfig


@dataclass
class DummyReceiptService:
    created_with: bytes | None = None
    list_data: list[dict[str, Any]] | None = None
    receipt_data: dict[str, Any] | None = None
    csv_text: str = "date,vendor,total,created_at\n"

    def create_receipt(self, contents: bytes) -> dict[str, Any]:
        self.created_with = contents
        return {
            "id": 1,
            "date": "2024-01-01",
            "vendor": "Store",
            "total": 10.0,
            "created_at": "2024-01-02T00:00:00",
        }

    def list_receipts(self) -> list[dict[str, Any]]:
        return self.list_data or []

    def get_receipt(self, receipt_id: int) -> dict[str, Any] | None:
        return self.receipt_data

    def export_csv(self) -> StringIO:
        return StringIO(self.csv_text)


@dataclass
class DummyBudgetService:
    list_data: list[dict[str, Any]] | None = None
    last_args: tuple[str, float, float] | None = None

    def list_budgets(self) -> list[dict[str, Any]]:
        return self.list_data or []

    def upsert_budget(self, category: str, monthly_limit: float, spent: float) -> dict[str, Any]:
        self.last_args = (category, monthly_limit, spent)
        return {"category": category, "monthly_limit": monthly_limit, "spent": spent}


def build_app(tmp_path: Path, receipt_service: DummyReceiptService, budget_service: DummyBudgetService) -> TestClient:
    base_dir = tmp_path / "app"
    data_dir = base_dir / "data"
    receipts_dir = data_dir / "receipts"
    static_dir = base_dir / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    (static_dir / "index.html").write_text("<html>OK</html>")

    config = AppConfig(
        base_dir=base_dir,
        data_dir=data_dir,
        receipts_dir=receipts_dir,
        db_path=data_dir / "app.db",
        static_dir=static_dir,
    )

    app = FastAPI()
    app.include_router(build_router(config, receipt_service, budget_service))
    return TestClient(app)


def test_health_check(tmp_path: Path) -> None:
    client = build_app(tmp_path, DummyReceiptService(), DummyBudgetService())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_static_index(tmp_path: Path) -> None:
    client = build_app(tmp_path, DummyReceiptService(), DummyBudgetService())

    response = client.get("/")

    assert response.status_code == 200
    assert "OK" in response.text


def test_create_receipt_rejects_non_image(tmp_path: Path) -> None:
    client = build_app(tmp_path, DummyReceiptService(), DummyBudgetService())

    response = client.post(
        "/receipts",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload an image file"


def test_create_receipt_accepts_image(tmp_path: Path) -> None:
    receipt_service = DummyReceiptService()
    client = build_app(tmp_path, receipt_service, DummyBudgetService())

    response = client.post(
        "/receipts",
        files={"file": ("receipt.png", b"image-bytes", "image/png")},
    )

    assert response.status_code == 200
    assert receipt_service.created_with == b"image-bytes"
    assert response.json()["id"] == 1


def test_list_and_get_receipts(tmp_path: Path) -> None:
    receipt_service = DummyReceiptService(list_data=[{"id": 1}])
    client = build_app(tmp_path, receipt_service, DummyBudgetService())

    list_response = client.get("/receipts")

    assert list_response.status_code == 200
    assert list_response.json() == [{"id": 1}]

    receipt_service.receipt_data = None
    get_response = client.get("/receipts/1")

    assert get_response.status_code == 404

    receipt_service.receipt_data = {"id": 1, "vendor": "Store"}
    get_response = client.get("/receipts/1")

    assert get_response.status_code == 200
    assert get_response.json()["id"] == 1


def test_export_csv(tmp_path: Path) -> None:
    receipt_service = DummyReceiptService(csv_text="date,vendor,total,created_at\n")
    client = build_app(tmp_path, receipt_service, DummyBudgetService())

    response = client.get("/export")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "receipts.csv" in response.headers["content-disposition"]
    assert response.text.startswith("date,vendor,total,created_at")


def test_list_and_upsert_budgets(tmp_path: Path) -> None:
    budget_service = DummyBudgetService(list_data=[{"category": "Food"}])
    client = build_app(tmp_path, DummyReceiptService(), budget_service)

    list_response = client.get("/budgets")

    assert list_response.status_code == 200
    assert list_response.json() == [{"category": "Food"}]

    upsert_response = client.post(
        "/budgets",
        json={"category": "Travel", "monthly_limit": 500.0, "spent": 125.0},
    )

    assert upsert_response.status_code == 200
    assert budget_service.last_args == ("Travel", 500.0, 125.0)
    assert upsert_response.json()["category"] == "Travel"
