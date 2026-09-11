"""Comprehensive End-to-End Forensic Demonstration Script."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.algorithms.verification import verify_recovery, verify_sanitization
from app.recovery import carve_bytes, carve_file
from app.sanitization import dod_5220_22_m, quick_zero_fill


def run_demo():
    print("==================================================================")
    print("  AEGIS FORENSICS: SECURE SANITIZATION & RECOVERY DEMONSTRATION   ")
    print("==================================================================")

    # 1. Forensic Carving Demo
    print("\n[STAGE 1] Signature-Based Forensic Carving")
    disk_path = ROOT_DIR / "data" / "sandbox" / "forensic_disk_image.raw"
    if not disk_path.is_file():
        # Generate sandbox first
        import urllib.request
        from app.api.algorithm_api import generate_sandbox_samples
        from flask import Flask
        app = Flask("demo_init")
        with app.app_context():
            generate_sandbox_samples()

    print(f"Analyzing disk image: {disk_path} ({disk_path.stat().st_size} bytes)")
    artifacts = carve_file(disk_path, output_dir=ROOT_DIR / "data" / "recovered")
    print(f"Extracted {len(artifacts)} carved artifact(s):")
    for a in artifacts:
        print(f"  - [{a.file_type.upper()}] Offset: {a.offset} (0x{a.offset:X}) | Length: {a.length} bytes | File: {a.recovered_path.name if a.recovered_path else 'memory'}")

    # 2. Recovery Verification Demo
    print("\n[STAGE 2] Independent Recovery Integrity Verification")
    png_artifact = next((a for a in artifacts if a.file_type == "png"), None)
    if png_artifact and png_artifact.recovered_path:
        evidence_badge = ROOT_DIR / "data" / "sandbox" / "evidence_badge.png"
        import hashlib
        baseline = hashlib.sha256(evidence_badge.read_bytes()).hexdigest() if evidence_badge.is_file() else None

        rec_result = verify_recovery(png_artifact.recovered_path, baseline_hash=baseline)
        print(f"Verified Artifact: {png_artifact.recovered_path.name}")
        print(f"  - Confidence Score: {rec_result.confidence_score}%")
        print(f"  - Verdict: {rec_result.details.get('verdict')}")
        print(f"  - Structural Valid: {rec_result.details.get('structural_valid')}")
        print(f"  - Magic Valid: {rec_result.details.get('magic_valid')}")
        print(f"  - Parser Smoke Test: {rec_result.details.get('parser_valid')}")

    # 3. Sanitization Demo
    print("\n[STAGE 3] Military DoD 5220.22-M 3-Pass Sanitization")
    target_demo = ROOT_DIR / "data" / "sandbox" / "classified_mission_brief.txt"
    if target_demo.is_file():
        initial_size = target_demo.stat().st_size
        print(f"Target: {target_demo.name} ({initial_size} bytes)")
        wipe_res = dod_5220_22_m(target_demo, confirm=True, nullify_metadata=True)
        print(f"  - Overwritten: {wipe_res.bytes_overwritten} bytes")
        print(f"  - Shannon Entropy: {wipe_res.entropy} / 8.0")
        print(f"  - Sanitized Status: {wipe_res.is_sanitized}")
        print(f"  - Confidence Score: {wipe_res.confidence_score}%")
        print(f"  - Verdict: {wipe_res.details.get('verdict')}")

    print("\n==================================================================")
    print("  DEMO COMPLETE! Launch the web dashboard: python run.py          ")
    print("  URL: http://127.0.0.1:5000                                      ")
    print("==================================================================")


if __name__ == "__main__":
    run_demo()
