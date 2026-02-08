"""Budget repository for SQLite operations."""

from __future__ import annotations

from typing import Any

from ..core.database import Database
from ..core.interfaces import IBudgetRepository


class BudgetRepository(IBudgetRepository):
    """SQL access for budget data."""
    def __init__(self, db: Database) -> None:
        self._db = db

    def list_budgets(self) -> list[dict[str, Any]]:
        with self._db.connect() as conn:
            rows = conn.execute(
                "SELECT id, category, monthly_limit, spent, prior_balance FROM budgets ORDER BY category"
            ).fetchall()
        return [dict(row) for row in rows]

    def upsert_budget(
        self,
        category: str,
        monthly_limit: float,
        spent: float,
        prior_balance: float = 0,
    ) -> dict[str, Any]:
        with self._db.connect() as conn:
            conn.execute(
                """
                INSERT INTO budgets (category, monthly_limit, spent, prior_balance)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(category) DO UPDATE SET
                    monthly_limit=excluded.monthly_limit,
                    spent=excluded.spent,
                    prior_balance=excluded.prior_balance
                """,
                (category, monthly_limit, spent, prior_balance),
            )
        return {
            "category": category,
            "monthly_limit": monthly_limit,
            "spent": spent,
            "prior_balance": prior_balance,
        }
