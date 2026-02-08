from __future__ import annotations

from app.services.ocr import ReceiptParser, parse_receipt_text


def test_receipt_parser_extracts_vendor_date_total() -> None:
    parser = ReceiptParser()
    text = """Coffee Hut\nDate: 2024-05-01\nLatte 4.50\nTotal 12.75\n"""

    result = parser.parse(text)

    assert result.vendor == "Coffee Hut"
    assert result.date == "2024-05-01"
    assert result.total == 12.75


def test_receipt_parser_handles_empty_text() -> None:
    parser = ReceiptParser()

    result = parser.parse("")

    assert result.vendor == "Unknown Vendor"
    assert result.date is None
    assert result.total == 0.0


def test_parse_receipt_text_returns_dict() -> None:
    text = """Market\n01/02/2024\nSubtotal 8.25\nTotal 9.99\n"""

    parsed = parse_receipt_text(text)

    assert parsed == {"vendor": "Market", "date": "01/02/2024", "total": 9.99}
