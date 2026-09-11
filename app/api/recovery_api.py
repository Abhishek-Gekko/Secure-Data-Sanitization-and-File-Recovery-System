"""REST API endpoints for file recovery, carving, and integrity verification."""

from __future__ import annotations

import os
from pathlib import Path
from flask import Blueprint, current_app, jsonify, request, send_file
from werkzeug.utils import secure_filename

from app.algorithms.verification import verify_recovery
from app.recovery.carving import EXTENSIONS, carve_bytes, carve_file
from app.recovery.deleted_files import DeletedFileRecord, recover_from_metadata
from app.recovery.filesystem import restore_from_extents

recovery_bp = Blueprint("recovery", __name__, url_prefix="/api/recovery")

RECOVERED_DIR = Path("data/recovered").resolve()


def _ensure_recovered_dir() -> Path:
    RECOVERED_DIR.mkdir(parents=True, exist_ok=True)
    return RECOVERED_DIR


@recovery_bp.route("/carve", methods=["POST"])
def carve():
    """Carve files from an uploaded disk image or a target path on disk."""
    out_dir = _ensure_recovered_dir()
    artifacts_data = []

    if "file" in request.files:
        uploaded = request.files["file"]
        if not uploaded.filename:
            return jsonify({"success": False, "error": "No file selected for upload"}), 400
        
        content = uploaded.read()
        artifacts = carve_bytes(content)
        
        # Save artifacts to recovered dir
        for num, art in enumerate(artifacts, 1):
            filename = f"carved_{num:04d}_{art.offset}{EXTENSIONS.get(art.file_type, '.bin')}"
            save_path = out_dir / filename
            save_path.write_bytes(art.data)
            
            # Text preview if txt
            preview = ""
            if art.file_type == "txt":
                try:
                    preview = art.data[:200].decode("utf-8", errors="replace")
                except Exception:
                    preview = ""

            art_result = verify_recovery(save_path)
            artifacts_data.append({
                "id": num,
                "file_type": art.file_type,
                "offset": art.offset,
                "length": art.length,
                "complete": art.complete,
                "filename": filename,
                "download_url": f"/api/recovery/artifacts/{filename}",
                "preview": preview,
                "confidence_score": art_result.confidence_score,
                "is_valid": art_result.is_valid,
                "verdict": art_result.details.get("verdict", "UNCERTAIN"),
                "structural_valid": art_result.details.get("structural_valid", False),
                "magic_valid": art_result.details.get("magic_valid", False),
                "parser_valid": art_result.details.get("parser_valid", False),
            })
    else:
        payload = request.get_json(silent=True) or request.form
        target = payload.get("target")
        if not target:
            return jsonify({"success": False, "error": "Provide either 'file' upload or 'target' path"}), 400
        
        target_path = Path(target).resolve()
        if not target_path.is_file():
            return jsonify({"success": False, "error": f"Target file not found: {target}"}), 404
        
        artifacts = carve_file(target_path, output_dir=out_dir)
        for num, art in enumerate(artifacts, 1):
            filename = art.recovered_path.name if art.recovered_path else f"carved_{num:04d}_{art.offset}.bin"
            preview = ""
            if art.file_type == "txt":
                try:
                    preview = art.data[:200].decode("utf-8", errors="replace")
                except Exception:
                    preview = ""

            art_path = art.recovered_path or (out_dir / filename)
            art_result = verify_recovery(art_path)
            artifacts_data.append({
                "id": num,
                "file_type": art.file_type,
                "offset": art.offset,
                "length": art.length,
                "complete": art.complete,
                "filename": filename,
                "download_url": f"/api/recovery/artifacts/{filename}",
                "preview": preview,
                "confidence_score": art_result.confidence_score,
                "is_valid": art_result.is_valid,
                "verdict": art_result.details.get("verdict", "UNCERTAIN"),
                "structural_valid": art_result.details.get("structural_valid", False),
                "magic_valid": art_result.details.get("magic_valid", False),
                "parser_valid": art_result.details.get("parser_valid", False),
            })

    # Calculate overall disk recovery metrics and confidence score
    total_count = len(artifacts_data)
    if total_count > 0:
        avg_score = round(sum(a["confidence_score"] for a in artifacts_data) / total_count, 1)
        complete_count = sum(1 for a in artifacts_data if a["complete"])
        struct_count = sum(1 for a in artifacts_data if a["structural_valid"])
        parser_count = sum(1 for a in artifacts_data if a["parser_valid"])
        verdict = "CONFIRMED" if avg_score >= 80 else ("PROBABLE" if avg_score >= 60 else ("UNCERTAIN" if avg_score >= 40 else "FAILED"))
    else:
        avg_score = 0.0
        complete_count = 0
        struct_count = 0
        parser_count = 0
        verdict = "NO_ARTIFACTS"

    overall_data = {
        "score": avg_score,
        "verdict": verdict,
        "total_artifacts": total_count,
        "complete_count": complete_count,
        "complete_percentage": round(complete_count / total_count * 100, 1) if total_count else 0,
        "struct_count": struct_count,
        "struct_percentage": round(struct_count / total_count * 100, 1) if total_count else 0,
        "parser_count": parser_count,
        "parser_percentage": round(parser_count / total_count * 100, 1) if total_count else 0,
    }

    return jsonify({
        "success": True,
        "count": total_count,
        "artifacts": artifacts_data,
        "overall": overall_data,
        "output_directory": str(out_dir),
    })


@recovery_bp.route("/artifacts/<filename>", methods=["GET"])
def download_artifact(filename: str):
    """Download a carved artifact."""
    safe_name = secure_filename(filename)
    path = RECOVERED_DIR / safe_name
    if not path.is_file():
        return jsonify({"success": False, "error": "Artifact file not found"}), 404
    return send_file(path, as_attachment=True)


@recovery_bp.route("/restore-extents", methods=["POST"])
def restore_extents_api():
    """Restore file from image given cluster/byte extents [(offset, length)]."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"success": False, "error": "JSON payload required"}), 400

    image = payload.get("image")
    extents = payload.get("extents")
    dest_name = payload.get("destination_name", "restored_extent.bin")

    if not image or not extents:
        return jsonify({"success": False, "error": "Missing 'image' or 'extents'"}), 400

    image_path = Path(image).resolve()
    if not image_path.is_file():
        return jsonify({"success": False, "error": f"Image file not found: {image}"}), 404

    dest_path = _ensure_recovered_dir() / secure_filename(dest_name)

    try:
        parsed_extents = [(int(e[0]), int(e[1])) for e in extents]
        output = restore_from_extents(image_path, parsed_extents, dest_path)
        return jsonify({
            "success": True,
            "restored_path": str(output),
            "size": output.stat().st_size,
            "filename": output.name,
            "download_url": f"/api/recovery/artifacts/{output.name}",
        })
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@recovery_bp.route("/verify", methods=["POST"])
def verify_recovered():
    """Verify recovered file against baseline hash, structure, and parser load."""
    baseline_hash = request.form.get("baseline_hash") or None
    if baseline_hash:
        baseline_hash = baseline_hash.strip()
    
    hash_algorithm = request.form.get("hash_algorithm", "sha256")
    expected_size_raw = request.form.get("expected_size")
    expected_size = int(expected_size_raw) if expected_size_raw and expected_size_raw.isdigit() else None

    target_path: Path | None = None
    temp_file = False

    if "file" in request.files:
        upload = request.files["file"]
        if not upload.filename:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        out_dir = _ensure_recovered_dir()
        target_path = out_dir / f"temp_verify_{secure_filename(upload.filename)}"
        upload.save(target_path)
        temp_file = True
    else:
        payload = request.get_json(silent=True) or request.form
        target = payload.get("target")
        if not target:
            return jsonify({"success": False, "error": "Provide either 'file' upload or 'target' path"}), 400
        target_path = Path(target).resolve()
        if not target_path.is_file():
            # Check in recovered dir
            in_rec = RECOVERED_DIR / secure_filename(target)
            if in_rec.is_file():
                target_path = in_rec
            else:
                return jsonify({"success": False, "error": f"File not found: {target}"}), 404
        if not baseline_hash and payload.get("baseline_hash"):
            baseline_hash = payload.get("baseline_hash").strip()

    try:
        res = verify_recovery(
            target_path,
            baseline_hash=baseline_hash,
            hash_algorithm=hash_algorithm,
            expected_size=expected_size,
        )

        return jsonify({
            "success": True,
            "data": {
                "method": res.method,
                "recovered_path": str(res.recovered_path),
                "filename": res.recovered_path.name if res.recovered_path else None,
                "original_hash": res.original_hash,
                "recovered_hash": res.recovered_hash,
                "is_valid": res.is_valid,
                "confidence_score": res.confidence_score,
                "details": res.details,
            },
        })
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400
