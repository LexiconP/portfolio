from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

from ..core.config import AppConfig
from ..core.interfaces import IBudgetService, IReceiptService


def build_router(
    config: AppConfig,
    receipt_service: IReceiptService,
    budget_service: IBudgetService,
) -> APIRouter:
    router = APIRouter()

    @router.get("/", response_class=HTMLResponse)
    def root() -> FileResponse:
        index_path = config.static_dir / "index.html"
        if not index_path.exists():
            raise HTTPException(status_code=500, detail="Static UI not found")
        return FileResponse(index_path)

    @router.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @router.post("/receipts")
    async def create_receipt(file: UploadFile = File(...)) -> dict[str, Any]:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Upload an image file")

        contents = await file.read()
        return receipt_service.create_receipt(contents)

    @router.get("/receipts")
    def list_receipts() -> list[dict[str, Any]]:
        return receipt_service.list_receipts()

    @router.get("/receipts/{receipt_id}")
    def get_receipt(receipt_id: int) -> dict[str, Any]:
        receipt = receipt_service.get_receipt(receipt_id)
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        return receipt

    @router.get("/export")
    def export_csv() -> StreamingResponse:
        output = receipt_service.export_csv()
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=receipts.csv"},
        )

    @router.get("/budgets")
    def list_budgets() -> list[dict[str, Any]]:
        return budget_service.list_budgets()

    @router.post("/budgets")
    def upsert_budget(payload: dict[str, Any]) -> dict[str, Any]:
        category = payload.get("category")
        monthly_limit = float(payload.get("monthly_limit", 0))
        spent = float(payload.get("spent", 0))
        if not category:
            raise HTTPException(status_code=400, detail="Category is required")

        return budget_service.upsert_budget(category, monthly_limit, spent)

    return router
