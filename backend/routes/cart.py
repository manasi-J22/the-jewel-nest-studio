"""Server-side session cart."""
from flask import Blueprint, request, jsonify, session
from models.product import ProductModel
from utils.validators import CartItemSchema, validate_payload
from utils.decorators import login_required

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


def _get_cart():
    return session.setdefault("cart", [])


def _save_cart(cart):
    session["cart"] = cart
    session.modified = True


@cart_bp.get("")
@login_required
def view_cart():
    cart = _get_cart()
    detailed, total = [], 0.0
    for entry in cart:
        product = ProductModel.get(entry["product_id"])
        if not product:
            continue
        price = float(product["price"])
        line_total = price * entry["quantity"]
        total += line_total
        detailed.append({
            "product_id": product["id"],
            "name": product["name"],
            "image_url": product["image_url"],
            "price": price,
            "quantity": entry["quantity"],
            "stock": product["stock"],
            "line_total": round(line_total, 2),
        })
    return jsonify({"items": detailed, "total": round(total, 2)})


@cart_bp.post("/add")
@login_required
def add_to_cart():
    data, errs = validate_payload(CartItemSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    product = ProductModel.get(data["product_id"])
    if not product:
        return jsonify({"error": "Product not found"}), 404
    if product["stock"] < data["quantity"]:
        return jsonify({"error": "Insufficient stock"}), 400

    cart = _get_cart()
    for entry in cart:
        if entry["product_id"] == data["product_id"]:
            entry["quantity"] = min(entry["quantity"] + data["quantity"],
                                    product["stock"])
            break
    else:
        cart.append({"product_id": data["product_id"], "quantity": data["quantity"]})
    _save_cart(cart)
    return jsonify({"message": "Added to cart", "cart_size": len(cart)})


@cart_bp.post("/update")
@login_required
def update_cart():
    data, errs = validate_payload(CartItemSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    cart = _get_cart()
    for entry in cart:
        if entry["product_id"] == data["product_id"]:
            entry["quantity"] = data["quantity"]
            break
    else:
        return jsonify({"error": "Item not in cart"}), 404
    _save_cart(cart)
    return jsonify({"message": "Cart updated"})


@cart_bp.post("/remove/<int:product_id>")
@login_required
def remove_from_cart(product_id):
    cart = [e for e in _get_cart() if e["product_id"] != product_id]
    _save_cart(cart)
    return jsonify({"message": "Removed", "cart_size": len(cart)})


@cart_bp.post("/clear")
@login_required
def clear_cart():
    _save_cart([])
    return jsonify({"message": "Cart cleared"})
