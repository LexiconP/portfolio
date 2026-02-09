from __future__ import annotations

from dataclasses import dataclass, field

from app.services.budgets import BudgetService


@dataclass
class RecordingBudgetRepository:
    last_args: tuple[str, float, float, float] | None = None
    upserted: list[tuple[str, float, float, float]] = field(default_factory=list)

    def list_budgets(self) -> list[dict]:
        return [{"category": "Food", "monthly_limit": 200.0, "spent": 50.0, "prior_balance": 25.0}]

    def upsert_budget(
        self,
        category: str,
        monthly_limit: float,
        spent: float,
        prior_balance: float = 0,
    ) -> dict:
        self.last_args = (category, monthly_limit, spent, prior_balance)
        self.upserted.append(self.last_args)
        return {
            "category": category,
            "monthly_limit": monthly_limit,
            "spent": spent,
            "prior_balance": prior_balance,
        }


def test_budget_service_lists_budgets() -> None:
    repository = RecordingBudgetRepository()
    service = BudgetService(repository=repository)

    budgets = service.list_budgets()

    assert budgets == [{"category": "Food", "monthly_limit": 200.0, "spent": 50.0, "prior_balance": 25.0}]


def test_budget_service_upserts_budget() -> None:
    repository = RecordingBudgetRepository()
    service = BudgetService(repository=repository)

    result = service.upsert_budget("Travel", 500.0, 125.0, 75.0)

    assert repository.last_args == ("Travel", 500.0, 125.0, 75.0)
    assert result == {
        "category": "Travel",
        "monthly_limit": 500.0,
        "spent": 125.0,
        "prior_balance": 75.0,
    }


def test_budget_service_imports_csv() -> None:
    repository = RecordingBudgetRepository()
    service = BudgetService(repository=repository)

    csv_bytes = b"category,monthly_limit,spent,prior_balance\nFood,300,120,25\nTravel,800,250,0\n"

    result = service.import_budgets("budgets.csv", csv_bytes)

    assert result == {"imported": 2}
    assert repository.upserted == [
        ("Food", 300.0, 120.0, 25.0),
        ("Travel", 800.0, 250.0, 0.0),
    ]
