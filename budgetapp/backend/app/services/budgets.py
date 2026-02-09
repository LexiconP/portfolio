"""Budget domain logic."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pandas as pd

from ..core.interfaces import IBudgetRepository


class BudgetService:
    """Coordinates budget retrieval and updates."""
    def __init__(self, repository: IBudgetRepository) -> None:
        self._repository = repository

    def list_budgets(self) -> list[dict[str, Any]]:
        return self._repository.list_budgets()

    def upsert_budget(
        self,
        category: str,
        monthly_limit: float,
        spent: float,
        prior_balance: float = 0,
    ) -> dict[str, Any]:
        return self._repository.upsert_budget(category, monthly_limit, spent, prior_balance)

    def import_budgets(self, filename: str, contents: bytes) -> dict[str, Any]:
        suffix = Path(filename).suffix.lower()
        data = io.BytesIO(contents)

        if suffix == ".csv":
            frame = pd.read_csv(data)
        elif suffix == ".xlsx":
            frame = pd.read_excel(data)
        else:
            raise ValueError("Unsupported file type")

        frame.columns = [str(col).strip().lower() for col in frame.columns]

        if "category" not in frame.columns:
            raise ValueError("Missing required 'category' column")

        for column in ("monthly_limit", "spent", "prior_balance"):
            if column not in frame.columns:
                frame[column] = 0

        frame["category"] = frame["category"].astype(str).str.strip()
        frame = frame[frame["category"] != ""]

        for column in ("monthly_limit", "spent", "prior_balance"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0)

        imported = 0
        for row in frame.itertuples(index=False):
            self._repository.upsert_budget(
                getattr(row, "category"),
                float(getattr(row, "monthly_limit")),
                float(getattr(row, "spent")),
                float(getattr(row, "prior_balance")),
            )
            imported += 1

        return {"imported": imported}
