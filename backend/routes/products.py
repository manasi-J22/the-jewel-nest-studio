"""Public product endpoints."""
from flask import Blueprint, request, jsonify
from models.product import ProductModel
from models.review import ReviewModel

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.get("")
def list_products():
    args = request.args
    items = ProductModel.list_filtered(
        category=args.get("category"),
        min_price=args.get("min_price", type=float),
        max_price=args.get("max_price", type=float),
        search=args.get("search"),
        sort=args.get("sort", "newest"),
        limit=args.get("limit", 50, type=int),
        offset=args.get("offset", 0, type=int),
    )
    for p in items:
        p["price"] = float(p["price"])
        p["avg_rating"] = round(float(p["avg_rating"]), 2)
    return jsonify({"products": items})


@products_bp.get("/categories")
def categories():
    return jsonify({"categories": ProductModel.categories()})


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    p = ProductModel.get(product_id)
    if not p:
        return jsonify({"error": "Product not found"}), 404
    p["price"] = float(p["price"])
    p["avg_rating"] = round(float(p["avg_rating"]), 2)
    p["reviews"] = ReviewModel.list_for_product(product_id)
    return jsonify({"product": p})
