"""Expense model."""
from extensions import get_cursor


class ExpenseModel:
    @staticmethod
    def create(expense_type, amount, expense_date, note=None):
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO expenses (expense_type, amount, expense_date, note) "
                "VALUES (%s, %s, %s, %s)",
                (expense_type, amount, expense_date, note),
            )
            return cur.lastrowid

    @staticmethod
    def list_all(month=None, year=None):
        sql = ("SELECT id, expense_type, amount, expense_date, note, created_at "
               "FROM expenses WHERE 1=1 ")
        params = []
        if month and year:
            sql += "AND MONTH(expense_date) = %s AND YEAR(expense_date) = %s "
            params.extend([month, year])
        elif year:
            sql += "AND YEAR(expense_date) = %s "
            params.append(year)
        sql += "ORDER BY expense_date DESC"
        with get_cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    @staticmethod
    def delete(expense_id):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
            return cur.rowcount > 0

    @staticmethod
    def monthly_summary(year):
        with get_cursor() as cur:
            cur.execute(
                "SELECT MONTH(expense_date) AS month, "
                "SUM(amount) AS total, COUNT(*) AS count "
                "FROM expenses WHERE YEAR(expense_date) = %s "
                "GROUP BY MONTH(expense_date) ORDER BY month",
                (year,),
            )
            return cur.fetchall()

    @staticmethod
    def by_type_summary(year):
        with get_cursor() as cur:
            cur.execute(
                "SELECT expense_type, SUM(amount) AS total, COUNT(*) AS count "
                "FROM expenses WHERE YEAR(expense_date) = %s "
                "GROUP BY expense_type ORDER BY total DESC",
                (year,),
            )
            return cur.fetchall()
