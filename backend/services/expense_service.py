"""Expense aggregations."""
from datetime import datetime
from models.expense import ExpenseModel


class ExpenseService:
    @staticmethod
    def dashboard(year=None):
        year = year or datetime.now().year
        monthly = ExpenseModel.monthly_summary(year)
        by_type = ExpenseModel.by_type_summary(year)
        total = sum(float(row["total"]) for row in monthly) if monthly else 0
        return {
            "year": year,
            "total": round(total, 2),
            "monthly": monthly,
            "by_type": by_type,
        }
