from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image
import pytesseract


class OcrService:
    def extract_text(self, image_path: Path) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)


@dataclass
class ReceiptParseResult:
    vendor: str
    date: str | None
    total: float


class ReceiptParser:
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


def parse_receipt_text(text: str) -> dict[str, Any]:
    parsed = ReceiptParser().parse(text)
    return {"vendor": parsed.vendor, "date": parsed.date, "total": parsed.total}
