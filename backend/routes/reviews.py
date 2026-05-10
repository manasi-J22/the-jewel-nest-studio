"""Review endpoints."""
from flask import Blueprint, request, jsonify, session
from models.review import ReviewModel
from utils.validators import ReviewSchema, validate_payload
from utils.decorators import login_required

reviews_bp = Blueprint("reviews", __name__, url_prefix="/api/reviews")


@reviews_bp.post("")
@login_required
def create_review():
    data, errs = validate_payload(ReviewSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    ReviewModel.create(
        session["user_id"], data["product_id"],
        data["rating"], data.get("comment"),
    )
    return jsonify({"message": "Review submitted"}), 201


@reviews_bp.get("/product/<int:product_id>")
def list_for_product(product_id):
    return jsonify({"reviews": ReviewModel.list_for_product(product_id)})
