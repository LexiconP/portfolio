from __future__ import annotations

from typing import Any

from ..core.interfaces import IBudgetRepository


class BudgetService:
    def __init__(self, repository: IBudgetRepository) -> None:
        self._repository = repository

    def list_budgets(self) -> list[dict[str, Any]]:
        return self._repository.list_budgets()

    def upsert_budget(self, category: str, monthly_limit: float, spent: float) -> dict[str, Any]:
        return self._repository.upsert_budget(category, monthly_limit, spent)
