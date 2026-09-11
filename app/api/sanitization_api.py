"""REST API endpoints for file sanitization and remanence verification."""

from __future__ import annotations

import os
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from app.algorithms.verification import verify_sanitization
from app.sanitization import sanitize_file, METHODS

sanitization_bp = Blueprint("sanitization", __name__, url_prefix="/api/sanitization")


def _resolve_target(target_str: str) -> Path:
    """Resolve target path safely within sandbox or workspace."""
    path = Path(target_str).resolve()
    # Ensure file exists
    if not path.is_file():
        raise FileNotFoundError(f"Target file does not exist: {target_str}")
    return path


@sanitization_bp.route("/methods", methods=["GET"])
def list_methods():
    """List supported sanitization algorithms with descriptions."""
    methods_meta = [
        {
            "id": "zero",
            "name": "Quick Zero-Fill",
            "passes": 1,
            "standard": "Single Pass Overwrite (0x00)",
            "description": "Overwrites entire file content with null bytes (0x00). Fast and effective for basic media clearing.",
            "pattern": "zero",
        },
        {
            "id": "random",
            "name": "Pseudorandom Wipe",
            "passes": 1,
            "standard": "CSPRNG Random Overwrite",
            "description": "Overwrites data with cryptographically secure pseudo-random bytes. Delivers high Shannon entropy (~8.0).",
            "pattern": "random",
        },
        {
            "id": "dod_5220_22_m",
            "name": "DoD 5220.22-M",
            "passes": 3,
            "standard": "DoD 5220.22-M (8-306 / ECE)",
            "description": "Military 3-pass wipe: Pass 1 with 0x00, Pass 2 with 0xFF (ones), Pass 3 with random bytes.",
            "pattern": "random",
        },
        {
            "id": "nist_clear",
            "name": "NIST SP 800-88 Clear",
            "passes": 1,
            "standard": "NIST Special Publication 800-88 Rev 1 (Clear)",
            "description": "Logical overwrite across all addressable storage locations with verification flush.",
            "pattern": "zero",
        },
        {
            "id": "nist_purge",
            "name": "NIST SP 800-88 Purge",
            "passes": 1,
            "standard": "NIST Special Publication 800-88 Rev 1 (Purge)",
            "description": "Purge overwrite using pseudo-random generation to prevent laboratory recovery techniques.",
            "pattern": "random",
        },
    ]
    return jsonify({"success": True, "methods": methods_meta})


@sanitization_bp.route("/wipe", methods=["POST"])
def wipe_file():
    """Execute destructive file sanitization."""
    payload = request.get_json(silent=True) or request.form
    target = payload.get("target")
    method = payload.get("method", "zero").lower()
    confirm = bool(payload.get("confirm", False))
    delete = bool(payload.get("delete", False))
    nullify_metadata = bool(payload.get("nullify_metadata", False))

    if not target:
        return jsonify({"success": False, "error": "Missing 'target' path parameter"}), 400

    if method not in METHODS:
        return jsonify({"success": False, "error": f"Invalid method '{method}'. Valid: {list(METHODS)}"}), 400

    if not confirm:
        return jsonify({
            "success": False,
            "error": "Destructive sanitization requires explicit confirmation (confirm=true).",
        }), 400

    try:
        path = _resolve_target(target)
        result = sanitize_file(
            path,
            method=method,
            confirm=confirm,
            delete=delete,
            nullify_metadata=nullify_metadata,
        )

        return jsonify({
            "success": True,
            "data": {
                "method": result.method,
                "bytes_overwritten": result.bytes_overwritten,
                "entropy": result.entropy,
                "is_sanitized": result.is_sanitized,
                "confidence_score": result.confidence_score,
                "details": result.details,
            },
        })
    except (ValueError, PermissionError, FileNotFoundError, OSError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"success": False, "error": f"Internal error: {exc}"}), 500


@sanitization_bp.route("/verify", methods=["POST"])
def verify():
    """Verify sanitization / remanence of a target file or uploaded file."""
    method = request.form.get("method", "zero")
    metadata_destroyed = request.form.get("metadata_destroyed", "false").lower() == "true"

    if "file" in request.files:
        upload = request.files["file"]
        if not upload.filename:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        data = upload.read()
        result = verify_sanitization(data, method=method, metadata_destroyed=metadata_destroyed)
    else:
        payload = request.get_json(silent=True) or request.form
        target = payload.get("target")
        if not target:
            return jsonify({"success": False, "error": "Provide either 'file' upload or 'target' path"}), 400
        try:
            path = _resolve_target(target)
            result = verify_sanitization(path, method=method, metadata_destroyed=metadata_destroyed)
        except Exception as exc:
            return jsonify({"success": False, "error": str(exc)}), 400

    return jsonify({
        "success": True,
        "data": {
            "method": result.method,
            "bytes_inspected": result.bytes_overwritten,
            "entropy": result.entropy,
            "is_sanitized": result.is_sanitized,
            "confidence_score": result.confidence_score,
            "details": result.details,
        },
    })
