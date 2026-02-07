"""OCR and receipt parsing utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image
import pytesseract


class OcrService:
    """Wrapper around Tesseract OCR."""
    def extract_text(self, image_path: Path) -> str:
        with Image.open(image_path) as image:
            return pytesseract.image_to_string(image)


@dataclass
class ReceiptParseResult:
    vendor: str
    date: str | None
    total: float


class ReceiptParser:
    """Extracts key fields from OCR text using simple heuristics."""
    def parse(self, text: str) -> ReceiptParseResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        vendor = lines[0] if lines else "Unknown Vendor"

        date_match = re.search(
            r"(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{2,4})",
            text,
        )
        date_value = date_match.group(0) if date_match else None

        amounts = [float(m) for m in re.findall(r"(\d+\.\d{2})", text)]
        total = max(amounts) if amounts else 0.0

        return ReceiptParseResult(vendor=vendor, date=date_value, total=total)


_DEFAULT_RECEIPT_PARSER = ReceiptParser()


def parse_receipt_text(text: str) -> dict[str, Any]:
    parsed = _DEFAULT_RECEIPT_PARSER.parse(text)
    return {"vendor": parsed.vendor, "date": parsed.date, "total": parsed.total}
