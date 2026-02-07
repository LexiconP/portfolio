"""Receipt domain logic."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.config import AppConfig
from ..core.interfaces import IReceiptParser, IReceiptRepository, IOcrService


class ReceiptService:
    """Coordinates receipt storage, OCR, parsing, and persistence."""
    def __init__(
        self,
        repository: IReceiptRepository,
        config: AppConfig,
        ocr_service: IOcrService,
        parser: IReceiptParser,
    ) -> None:
        self._repository = repository
        self._config = config
        self._ocr = ocr_service
        self._parser = parser

    def create_receipt(self, contents: bytes) -> dict[str, Any]:
        # Save image, run OCR, parse fields, then persist.
        image_path = self._store_receipt_image(contents)
        ocr_text = self._ocr.extract_text(image_path)
        parsed = self._parser.parse(ocr_text)
        created_at = datetime.utcnow().isoformat()

        receipt_id = self._repository.insert_receipt(
            parsed.date,
            parsed.vendor,
            parsed.total,
            str(image_path),
            ocr_text,
            created_at,
        )

        return {
            "id": receipt_id,
            "date": parsed.date,
            "vendor": parsed.vendor,
            "total": parsed.total,
            "created_at": created_at,
        }

    def list_receipts(self) -> list[dict[str, Any]]:
        return self._repository.list_receipts()

    def get_receipt(self, receipt_id: int) -> dict[str, Any] | None:
        return self._repository.get_receipt(receipt_id)

    def export_csv(self) -> io.StringIO:
        # Build CSV from repository rows.
        rows = self._repository.export_rows()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "vendor", "total", "created_at"])
        for row in rows:
            writer.writerow([row["date"], row["vendor"], row["total"], row["created_at"]])

        output.seek(0)
        return output

    def _store_receipt_image(self, contents: bytes) -> Path:
        # Generate a unique filename based on timestamp.
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        image_path = self._config.receipts_dir / f"receipt_{timestamp}.png"
        image_path.write_bytes(contents)
        return image_path
