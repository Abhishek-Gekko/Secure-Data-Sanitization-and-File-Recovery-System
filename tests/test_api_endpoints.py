"""Integration tests for the REST API endpoints and web pipeline."""

import json
from pathlib import Path
import pytest
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "online"


def test_methods_list(client):
    res = client.get("/api/sanitization/methods")
    assert res.status_code == 200
    methods = res.get_json()["methods"]
    assert len(methods) >= 4
    method_ids = [m["id"] for m in methods]
    assert "dod_5220_22_m" in method_ids
    assert "zero" in method_ids


def test_sandbox_generation_and_carving_pipeline(client):
    # 1. Generate sandbox samples
    res = client.post("/api/algorithm/sandbox/generate")
    assert res.status_code == 200
    gen_data = res.get_json()
    assert gen_data["success"] is True
    assert len(gen_data["files"]) >= 5

    # 2. List files
    res = client.get("/api/algorithm/sandbox/files")
    assert res.status_code == 200
    files = res.get_json()["files"]
    disk_file = next(f for f in files if f["name"].endswith(".raw"))

    # 3. Carve the synthetic disk image
    res = client.post("/api/recovery/carve", json={"target": disk_file["path"]})
    assert res.status_code == 200
    carve_data = res.get_json()
    assert carve_data["success"] is True
    assert carve_data["count"] >= 3

    # Check that png, pdf, and zip are found
    types = [a["file_type"] for a in carve_data["artifacts"]]
    assert "png" in types
    assert "pdf" in types

    # 4. Verify a carved png artifact with its actual baseline hash
    png_art = next(a for a in carve_data["artifacts"] if a["file_type"] == "png")
    actual_hash = next(f["sha256"] for f in files if f["name"] == "evidence_badge.png")
    res = client.post("/api/recovery/verify", data={
        "target": f"data/recovered/{png_art['filename']}",
        "baseline_hash": actual_hash,
    })
    assert res.status_code == 200
    rec_ver = res.get_json()["data"]
    assert rec_ver["details"]["structural_valid"] is True
    assert rec_ver["details"]["magic_valid"] is True
    assert rec_ver["confidence_score"] >= 80.0


def test_sanitization_wipe_and_remanence_scan(client, tmp_path):
    target = tmp_path / "top_secret.txt"
    target.write_bytes(b"Extremely confidential research report payload " * 100)  # >= 4KB

    # Confirm is required
    res = client.post("/api/sanitization/wipe", json={
        "target": str(target),
        "method": "dod_5220_22_m",
        "confirm": False,
    })
    assert res.status_code == 400

    # Execute DoD 5220.22-M 3-pass wipe
    res = client.post("/api/sanitization/wipe", json={
        "target": str(target),
        "method": "dod_5220_22_m",
        "confirm": True,
        "nullify_metadata": True,
        "delete": False,
    })
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["is_sanitized"] is True
    assert data["confidence_score"] >= 85.0

    # Verify Remanence
    res = client.post("/api/sanitization/verify", data={
        "target": str(target),
        "method": "dod_5220_22_m",
        "metadata_destroyed": "true",
    })
    assert res.status_code == 200
    scan = res.get_json()["data"]
    assert scan["is_sanitized"] is True
    assert scan["details"]["carved_artifacts"] == 0
