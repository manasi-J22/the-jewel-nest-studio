"""Order checkout & history endpoints."""
from flask import Blueprint, request, jsonify, session, current_app
from services.order_service import OrderService
from models.order import OrderModel
from utils.validators import CheckoutSchema, validate_payload
from utils.decorators import login_required

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@orders_bp.post("/checkout")
@login_required
def checkout():
    data, errs = validate_payload(CheckoutSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    cart = session.get("cart", [])
    order_id, err = OrderService.checkout(
        session["user_id"], cart,
        data["address"], data["phone"], data["payment_method"],
    )
    if err:
        return jsonify({"error": err}), 400

    session["cart"] = []
    session.modified = True
    current_app.logger.info(
        f"Order created: id={order_id} user={session['user_id']}"
    )
    return jsonify({"message": "Order placed", "order_id": order_id}), 201


@orders_bp.get("")
@login_required
def history():
    orders = OrderModel.list_for_user(session["user_id"])
    for o in orders:
        o["total"] = float(o["total"])
        for it in o["items"]:
            it["unit_price"] = float(it["unit_price"])
    return jsonify({"orders": orders})
