from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.core.config import AppConfig
from app.services.receipts import ReceiptService


@dataclass
class ParseResult:
    vendor: str
    date: str | None
    total: float


class RecordingOcrService:
    def __init__(self, text: str) -> None:
        self.text = text
        self.last_path: Path | None = None

    def extract_text(self, image_path: Path) -> str:
        self.last_path = image_path
        return self.text


class RecordingParser:
    def __init__(self, result: ParseResult) -> None:
        self.result = result
        self.last_text: str | None = None

    def parse(self, text: str) -> ParseResult:
        self.last_text = text
        return self.result


class RecordingReceiptRepository:
    def __init__(self) -> None:
        self.insert_args: tuple | None = None

    def insert_receipt(
        self,
        date: str | None,
        vendor: str,
        total: float,
        image_path: str,
        ocr_text: str,
        created_at: str,
    ) -> int:
        self.insert_args = (date, vendor, total, image_path, ocr_text, created_at)
        return 1

    def list_receipts(self) -> list[dict]:
        return []

    def get_receipt(self, receipt_id: int) -> dict | None:
        return None

    def export_rows(self) -> list[dict]:
        return []


def build_config(tmp_path: Path) -> AppConfig:
    base_dir = tmp_path / "app"
    data_dir = base_dir / "data"
    receipts_dir = data_dir / "receipts"
    static_dir = base_dir / "static"
    return AppConfig(
        base_dir=base_dir,
        data_dir=data_dir,
        receipts_dir=receipts_dir,
        db_path=data_dir / "app.db",
        static_dir=static_dir,
    )


def test_create_receipt_stores_bytes_and_calls_ocr(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    config.ensure_directories()
    repository = RecordingReceiptRepository()
    ocr_service = RecordingOcrService(text="TOTAL 12.34")
    parser = RecordingParser(result=ParseResult(vendor="Store", date="2024-01-01", total=12.34))

    service = ReceiptService(
        repository=repository,
        config=config,
        ocr_service=ocr_service,
        parser=parser,
    )

    contents = b"fake-image-bytes"
    service.create_receipt(contents)

    files = list(config.receipts_dir.glob("*.png"))
    assert len(files) == 1
    assert files[0].read_bytes() == contents
    assert ocr_service.last_path == files[0]


def test_create_receipt_maps_parser_output_to_repository(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    config.ensure_directories()
    repository = RecordingReceiptRepository()
    ocr_service = RecordingOcrService(text="parsed text")
    parser = RecordingParser(result=ParseResult(vendor="Coffee", date="01/02/2024", total=9.99))

    service = ReceiptService(
        repository=repository,
        config=config,
        ocr_service=ocr_service,
        parser=parser,
    )

    service.create_receipt(b"bytes")

    assert repository.insert_args is not None
    date, vendor, total, image_path, ocr_text, created_at = repository.insert_args
    assert date == "01/02/2024"
    assert vendor == "Coffee"
    assert total == 9.99
    assert ocr_text == "parsed text"
    assert image_path.endswith(".png")
    assert created_at


def test_create_receipt_handles_empty_parser_output(tmp_path: Path) -> None:
    config = build_config(tmp_path)
    config.ensure_directories()
    repository = RecordingReceiptRepository()
    ocr_service = RecordingOcrService(text="")
    parser = RecordingParser(result=ParseResult(vendor="", date=None, total=0.0))

    service = ReceiptService(
        repository=repository,
        config=config,
        ocr_service=ocr_service,
        parser=parser,
    )

    service.create_receipt(b"bytes")

    assert repository.insert_args is not None
    date, vendor, total, _, ocr_text, _ = repository.insert_args
    assert date is None
    assert vendor == ""
    assert total == 0.0
    assert ocr_text == ""
