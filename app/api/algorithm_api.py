"""REST API endpoints for algorithm testing, confidence calculations, and demo sandbox generation."""

from __future__ import annotations

import hashlib
import io
import os
import struct
import zipfile
from collections import Counter
from pathlib import Path
from flask import Blueprint, jsonify, request

from app.algorithms.confidence import recovery_confidence, sanitization_confidence
from app.algorithms.verification import digest, shannon_entropy

algorithm_bp = Blueprint("algorithm", __name__, url_prefix="/api/algorithm")

SANDBOX_DIR = Path("data/sandbox").resolve()


def _ensure_sandbox() -> Path:
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return SANDBOX_DIR


@algorithm_bp.route("/confidence/sanitization", methods=["POST"])
def calc_sanitization_confidence():
    """Calculate sanitization confidence score and verdict given metrics."""
    data = request.get_json(silent=True) or {}
    metrics = {
        "pattern_uniformity": data.get("pattern_uniformity"),
        "negative_carving": data.get("negative_carving"),
        "entropy_compliance": data.get("entropy_compliance"),
        "metadata_destruction": data.get("metadata_destruction"),
    }
    result = sanitization_confidence(metrics)
    return jsonify({
        "success": True,
        "score": result.score,
        "verdict": result.verdict,
        "components": result.components,
    })


@algorithm_bp.route("/confidence/recovery", methods=["POST"])
def calc_recovery_confidence():
    """Calculate recovery confidence score and verdict given metrics."""
    data = request.get_json(silent=True) or {}
    metrics = {
        "hash_integrity": data.get("hash_integrity"),
        "structural_validation": data.get("structural_validation"),
        "parser_load": data.get("parser_load"),
        "completeness": data.get("completeness"),
    }
    result = recovery_confidence(metrics)
    return jsonify({
        "success": True,
        "score": result.score,
        "verdict": result.verdict,
        "components": result.components,
    })


@algorithm_bp.route("/entropy", methods=["POST"])
def calculate_entropy_api():
    """Calculate Shannon entropy and byte frequency distribution."""
    if "file" in request.files:
        data = request.files["file"].read()
    else:
        payload = request.get_json(silent=True) or request.form
        target = payload.get("target")
        if target and Path(target).is_file():
            data = Path(target).read_bytes()
        else:
            text = payload.get("text", "")
            data = text.encode("utf-8")

    entropy = shannon_entropy(data)
    size = len(data)
    counts = Counter(data)
    top_bytes = [{"byte": f"0x{b:02X}", "count": c, "percentage": round(c / size * 100, 2)}
                 for b, c in counts.most_common(8)] if size else []

    return jsonify({
        "success": True,
        "size": size,
        "entropy": round(entropy, 5),
        "entropy_normalized": round(entropy / 8.0, 4),
        "top_bytes": top_bytes,
        "sha256": digest(data, "sha256") if size else None,
    })


@algorithm_bp.route("/sandbox/files", methods=["GET"])
def list_sandbox_files():
    """List available sandbox test files."""
    box = _ensure_sandbox()
    files = []
    for entry in box.iterdir():
        if entry.is_file():
            stat = entry.stat()
            files.append({
                "name": entry.name,
                "path": str(entry),
                "size": stat.st_size,
                "sha256": digest(entry, "sha256"),
                "modified": stat.st_mtime,
            })
    return jsonify({"success": True, "sandbox_dir": str(box), "files": sorted(files, key=lambda x: x["name"])})


@algorithm_bp.route("/sandbox/generate", methods=["POST"])
def generate_sandbox_samples():
    """Generate sample test files and a forensic synthetic disk image."""
    box = _ensure_sandbox()

    # 1. Sample text file
    txt_file = box / "classified_mission_brief.txt"
    txt_content = (
        "CONFIDENTIAL OPERATION REPORT\n"
        "Date: 2026-09-11\n"
        "Security Level: TOP SECRET // FORENSIC VERIFICATION\n"
        "Payload: Quantum encryption keys and distributed recovery protocols.\n"
        "All extents must be sanitized according to DoD 5220.22-M standards.\n"
    )
    txt_file.write_text(txt_content, encoding="utf-8")

    # 2. Sample valid PNG file
    png_file = box / "evidence_badge.png"
    # Minimal 1x1 valid PNG
    png_data = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    png_file.write_bytes(png_data)

    # 3. Sample valid PDF file
    pdf_file = box / "incident_report.pdf"
    pdf_data = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n190\n%%EOF"
    )
    pdf_file.write_bytes(pdf_data)

    # 4. Sample valid ZIP archive
    zip_file = box / "archived_logs.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("audit.log", "System integrity verified at 2026-09-11 14:00:00 UTC\n")
    zip_data = buf.getvalue()
    zip_file.write_bytes(zip_data)

    # 5. Damaged/Corrupted PNG sample (to test parser smoke test rejection)
    corrupt_file = box / "corrupted_leak.png"
    corrupt_file.write_bytes(b"\x89PNG\r\n\x1a\nGARBAGE_DATA_WITHOUT_IEND_OR_CHUNKS")

    # 6. Forensic Raw Disk Image with embedded files & padding for Carving Demo
    disk_file = box / "forensic_disk_image.raw"
    padding = b"\x00" * 512
    junk = b"\x55\xAA" * 256
    disk_data = (
        b"MBR_HEADER_SECTOR_0" + padding[:493] +
        png_data + junk +
        pdf_data + padding +
        b"\x00" * 10 + b"Restored analyst notes: Secret token is 99882244." * 2 + b"\x00" * 10 +
        zip_data + padding
    )
    disk_file.write_bytes(disk_data)

    return jsonify({
        "success": True,
        "message": "Sample sandbox files created successfully",
        "files": [
            {"name": txt_file.name, "sha256": digest(txt_file, "sha256"), "size": len(txt_content)},
            {"name": png_file.name, "sha256": digest(png_file, "sha256"), "size": len(png_data)},
            {"name": pdf_file.name, "sha256": digest(pdf_file, "sha256"), "size": len(pdf_data)},
            {"name": zip_file.name, "sha256": digest(zip_file, "sha256"), "size": len(zip_data)},
            {"name": corrupt_file.name, "sha256": digest(corrupt_file, "sha256"), "size": corrupt_file.stat().st_size},
            {"name": disk_file.name, "sha256": digest(disk_file, "sha256"), "size": len(disk_data)},
        ],
    })
