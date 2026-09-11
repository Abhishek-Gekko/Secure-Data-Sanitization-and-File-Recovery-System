"""Main entrypoint for the Secure Data Sanitization & Recovery System Web Server."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from flask import Flask, send_from_directory, jsonify, request

from app.api.algorithm_api import algorithm_bp
from app.api.recovery_api import recovery_bp
from app.api.sanitization_api import sanitization_bp
from app.recovery.validator import FileValidator

FRONTEND_DIR = BASE_DIR / "frontend"


def create_app() -> Flask:
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="",
    )

    # Configuration
    app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024  # 128 MB max upload
    app.config["JSON_SORT_KEYS"] = False

    # Register Blueprints
    app.register_blueprint(sanitization_bp)
    app.register_blueprint(recovery_bp)
    app.register_blueprint(algorithm_bp)

    # Compatibility endpoint for /api/recover
    @app.route("/api/recover", methods=["POST"])
    def run_recovery_compatibility():
        payload = request.get_json(silent=True) or request.form
        method = payload.get("method", "carving").lower()
        if method not in ["filesystem", "carving"]:
            return jsonify({"status": "error", "detail": "Invalid recovery method selected."}), 400

        recovered_dir = BASE_DIR / "data" / "recovered"
        validator = FileValidator(str(recovered_dir))
        recovered_files_data = []

        if recovered_dir.exists():
            for entry in sorted(recovered_dir.iterdir()):
                if entry.is_file():
                    status = validator.validate_file(str(entry))
                    size_mb = round(entry.stat().st_size / (1024 * 1024), 2)
                    recovered_files_data.append({
                        "filename": entry.name,
                        "size_mb": size_mb,
                        "status": status,
                    })

        return jsonify({
            "status": "success",
            "method_used": method,
            "total_recovered": len(recovered_files_data),
            "files": recovered_files_data,
        })

    # Frontend Route
    @app.route("/")
    def index():
        return send_from_directory(str(FRONTEND_DIR), "index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "online", "system": "Forensic-Data-Sanitization-and-Recovery"})

    # Error handling
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    print("==================================================================")
    print("  SECURE DATA SANITIZATION & FORENSIC FILE RECOVERY WEB SYSTEM    ")
    print("  Server listening on: http://127.0.0.1:5000                     ")
    print("==================================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
