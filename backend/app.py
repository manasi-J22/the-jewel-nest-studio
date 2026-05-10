"""Flask application factory."""
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_session import Session

from config import Config
from extensions import init_db_pool
from utils.logger import setup_logger
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.reviews import reviews_bp
from routes.admin import admin_bp
from routes.expenses import expenses_bp

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,
        static_url_path="",
    )
    app.config.from_object(Config)

    setup_logger(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": Config.CORS_ORIGIN}},
        supports_credentials=True,
    )
    Session(app)

    try:
        init_db_pool()
        app.logger.info("DB connection pool initialized")
    except Exception as e:
        app.logger.error(f"DB pool init failed: {e}")

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(expenses_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/") or request.path.startswith("/uploads/"):
            return jsonify({"error": "Resource not found"}), 404
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large"}), 413

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs("flask_session", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_DEBUG") == "1")
