"""Expense tracker (admin only)."""
from datetime import datetime
from flask import Blueprint, request, jsonify
from models.expense import ExpenseModel
from services.expense_service import ExpenseService
from utils.validators import ExpenseSchema, validate_payload
from utils.decorators import admin_required

expenses_bp = Blueprint("expenses", __name__, url_prefix="/api/admin/expenses")


@expenses_bp.post("")
@admin_required
def create_expense():
    data, errs = validate_payload(ExpenseSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    expense_id = ExpenseModel.create(
        data["expense_type"], data["amount"],
        data["expense_date"], data.get("note"),
    )
    return jsonify({"message": "Expense recorded", "id": expense_id}), 201


@expenses_bp.get("")
@admin_required
def list_expenses():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    items = ExpenseModel.list_all(month=month, year=year)
    for e in items:
        e["amount"] = float(e["amount"])
        e["expense_date"] = e["expense_date"].isoformat() if e["expense_date"] else None
    return jsonify({"expenses": items})


@expenses_bp.delete("/<int:expense_id>")
@admin_required
def delete_expense(expense_id):
    if not ExpenseModel.delete(expense_id):
        return jsonify({"error": "Not found"}), 404
    return jsonify({"message": "Deleted"})


@expenses_bp.get("/dashboard")
@admin_required
def dashboard():
    year = request.args.get("year", type=int) or datetime.now().year
    data = ExpenseService.dashboard(year)
    for row in data["monthly"]:
        row["total"] = float(row["total"])
    for row in data["by_type"]:
        row["total"] = float(row["total"])
    return jsonify(data)
