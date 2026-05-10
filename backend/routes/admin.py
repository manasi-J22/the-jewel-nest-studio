"""Admin endpoints — products and orders management."""
from flask import Blueprint, request, jsonify, current_app
from models.product import ProductModel
from models.order import OrderModel
from models.user import UserModel
from services.product_service import ProductService
from utils.validators import ProductSchema, validate_payload
from utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/stats")
@admin_required
def stats():
    """Quick dashboard stats."""
    from extensions import get_cursor
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM users WHERE role = 'user'")
        users = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c FROM products")
        products = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) AS c, COALESCE(SUM(total),0) AS rev FROM orders")
        order_row = cur.fetchone()
        cur.execute("SELECT COUNT(*) AS c FROM orders WHERE status = 'pending'")
        pending = cur.fetchone()["c"]
    return jsonify({
        "users": users,
        "products": products,
        "orders": order_row["c"],
        "revenue": float(order_row["rev"]),
        "pending_orders": pending,
    })


@admin_bp.post("/products")
@admin_required
def create_product():
    if request.content_type and request.content_type.startswith("multipart/"):
        form = request.form.to_dict()
        if "stock" in form:
            form["stock"] = int(form["stock"])
        if "image" in request.files:
            try:
                form["image_url"] = ProductService.save_image(request.files["image"])
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        payload = form
    else:
        payload = request.get_json(silent=True) or {}

    data, errs = validate_payload(ProductSchema, payload)
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    product_id = ProductModel.create(data)
    current_app.logger.info(f"Product created: id={product_id} name={data['name']}")
    return jsonify({"message": "Product created", "id": product_id}), 201


@admin_bp.put("/products/<int:product_id>")
@admin_bp.post("/products/<int:product_id>")
@admin_required
def update_product(product_id):
    if request.content_type and request.content_type.startswith("multipart/"):
        form = request.form.to_dict()
        if "stock" in form:
            form["stock"] = int(form["stock"])
        if "image" in request.files and request.files["image"].filename:
            try:
                form["image_url"] = ProductService.save_image(request.files["image"])
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        payload = form
    else:
        payload = request.get_json(silent=True) or {}

    if not ProductModel.get(product_id):
        return jsonify({"error": "Product not found"}), 404

    ok = ProductModel.update(product_id, payload)
    if not ok:
        return jsonify({"error": "No fields updated"}), 400
    current_app.logger.info(f"Product updated: id={product_id}")
    return jsonify({"message": "Product updated"})


@admin_bp.delete("/products/<int:product_id>")
@admin_required
def delete_product(product_id):
    if not ProductModel.delete(product_id):
        return jsonify({"error": "Product not found"}), 404
    current_app.logger.info(f"Product deleted: id={product_id}")
    return jsonify({"message": "Deleted"})


@admin_bp.get("/orders")
@admin_required
def list_orders():
    orders = OrderModel.list_all()
    for o in orders:
        o["total"] = float(o["total"])
        for it in o["items"]:
            it["unit_price"] = float(it["unit_price"])
    return jsonify({"orders": orders})


@admin_bp.put("/orders/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ("pending", "processing", "shipped", "delivered", "cancelled"):
        return jsonify({"error": "Invalid status"}), 400
    if not OrderModel.update_status(order_id, status):
        return jsonify({"error": "Order not found"}), 404
    return jsonify({"message": "Status updated"})


@admin_bp.get("/users")
@admin_required
def list_users():
    return jsonify({"users": UserModel.list_all()})
