from __future__ import annotations

from dataclasses import dataclass

from app.services.budgets import BudgetService


@dataclass
class RecordingBudgetRepository:
    last_args: tuple[str, float, float] | None = None

    def list_budgets(self) -> list[dict]:
        return [{"category": "Food", "monthly_limit": 200.0, "spent": 50.0}]

    def upsert_budget(self, category: str, monthly_limit: float, spent: float) -> dict:
        self.last_args = (category, monthly_limit, spent)
        return {"category": category, "monthly_limit": monthly_limit, "spent": spent}


def test_budget_service_lists_budgets() -> None:
    repository = RecordingBudgetRepository()
    service = BudgetService(repository=repository)

    budgets = service.list_budgets()

    assert budgets == [{"category": "Food", "monthly_limit": 200.0, "spent": 50.0}]


def test_budget_service_upserts_budget() -> None:
    repository = RecordingBudgetRepository()
    service = BudgetService(repository=repository)

    result = service.upsert_budget("Travel", 500.0, 125.0)

    assert repository.last_args == ("Travel", 500.0, 125.0)
    assert result == {"category": "Travel", "monthly_limit": 500.0, "spent": 125.0}
