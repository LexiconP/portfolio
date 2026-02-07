from __future__ import annotations

import csv
import io
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import pytesseract

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECEIPTS_DIR = DATA_DIR / "receipts"
DB_PATH = DATA_DIR / "app.db"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Receipt OCR Budget Reconciliation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_storage() -> None:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                vendor TEXT,
                total REAL,
                image_path TEXT,
                ocr_text TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT UNIQUE,
                monthly_limit REAL DEFAULT 0,
                spent REAL DEFAULT 0
            );
            """
        )


def parse_receipt_text(text: str) -> dict[str, Any]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    vendor = lines[0] if lines else "Unknown Vendor"

    date_match = re.search(
        r"(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{2,4})",
        text,
    )
    date_value = None
    if date_match:
        date_value = date_match.group(0)

    amounts = [float(m) for m in re.findall(r"(\d+\.\d{2})", text)]
    total = max(amounts) if amounts else 0.0

    return {
        "vendor": vendor,
        "date": date_value,
        "total": total,
    }


@app.on_event("startup")
def on_startup() -> None:
    init_storage()
    init_db()


@app.get("/", response_class=HTMLResponse)
def root() -> FileResponse:
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="Static UI not found")
    return FileResponse(index_path)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/receipts")
async def create_receipt(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Upload an image file")

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    image_path = RECEIPTS_DIR / f"receipt_{timestamp}.png"

    contents = await file.read()
    image_path.write_bytes(contents)

    image = Image.open(image_path)
    ocr_text = pytesseract.image_to_string(image)
    parsed = parse_receipt_text(ocr_text)

    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO receipts (date, vendor, total, image_path, ocr_text, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                parsed.get("date"),
                parsed.get("vendor"),
                parsed.get("total"),
                str(image_path),
                ocr_text,
                created_at,
            ),
        )
        receipt_id = cursor.lastrowid

    return {
        "id": receipt_id,
        "date": parsed.get("date"),
        "vendor": parsed.get("vendor"),
        "total": parsed.get("total"),
        "created_at": created_at,
    }


@app.get("/receipts")
def list_receipts() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, date, vendor, total, created_at FROM receipts ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: int) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM receipts WHERE id = ?",
            (receipt_id,),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return dict(row)


@app.get("/export")
def export_csv() -> StreamingResponse:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT date, vendor, total, created_at FROM receipts ORDER BY id DESC"
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "vendor", "total", "created_at"])
    for row in rows:
        writer.writerow([row["date"], row["vendor"], row["total"], row["created_at"]])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=receipts.csv"},
    )


@app.get("/budgets")
def list_budgets() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, category, monthly_limit, spent FROM budgets ORDER BY category"
        ).fetchall()
    return [dict(row) for row in rows]


@app.post("/budgets")
def upsert_budget(payload: dict[str, Any]) -> dict[str, Any]:
    category = payload.get("category")
    monthly_limit = payload.get("monthly_limit", 0)
    spent = payload.get("spent", 0)
    if not category:
        raise HTTPException(status_code=400, detail="Category is required")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO budgets (category, monthly_limit, spent)
            VALUES (?, ?, ?)
            ON CONFLICT(category) DO UPDATE SET monthly_limit=excluded.monthly_limit, spent=excluded.spent
            """,
            (category, monthly_limit, spent),
        )
    return {"category": category, "monthly_limit": monthly_limit, "spent": spent}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
