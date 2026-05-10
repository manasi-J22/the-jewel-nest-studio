"""Authentication endpoints."""
from flask import Blueprint, request, jsonify, session, current_app
from services.auth_service import AuthService
from utils.validators import RegisterSchema, LoginSchema, validate_payload
from utils.decorators import login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data, errs = validate_payload(RegisterSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    user_id, err = AuthService.register(
        data["name"], data["email"], data["password"], data.get("phone")
    )
    if err:
        return jsonify({"error": err}), 409

    session.clear()
    session["user_id"] = user_id
    session["role"] = "user"
    session["name"] = data["name"]
    current_app.logger.info(f"User registered: {data['email']} (id={user_id})")
    return jsonify({
        "message": "Registered",
        "user": {"id": user_id, "name": data["name"],
                 "email": data["email"], "role": "user"},
    }), 201


@auth_bp.post("/login")
def login():
    data, errs = validate_payload(LoginSchema, request.get_json(silent=True) or {})
    if errs:
        return jsonify({"error": "Validation failed", "details": errs}), 400

    user, err = AuthService.authenticate(data["email"], data["password"])
    if err:
        current_app.logger.warning(f"Failed login attempt: {data['email']}")
        return jsonify({"error": err}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session["name"] = user["name"]
    current_app.logger.info(f"User logged in: {user['email']}")
    return jsonify({
        "message": "Logged in",
        "user": {
            "id": user["id"], "name": user["name"],
            "email": user["email"], "role": user["role"],
        },
    })


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@auth_bp.get("/me")
@login_required
def me():
    return jsonify({
        "user": {
            "id": session["user_id"],
            "name": session.get("name"),
            "role": session.get("role"),
        }
    })
