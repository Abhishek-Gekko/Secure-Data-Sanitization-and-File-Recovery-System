"""Recovered-file validation and compatibility interface."""

from __future__ import annotations

import os
from pathlib import Path

from app.algorithms.verification import verify_recovery


class FileValidator:
    """Validates recovered files using structural checks and forensic signatures."""

    def __init__(self, recovered_dir: str = "recovered"):
        self.recovered_dir = recovered_dir

    def validate_file(self, filepath: str) -> str:
        res = verify_recovery(filepath)
        if res.is_valid:
            return "VALID"
        if res.details.get("structural_valid") or res.details.get("magic_valid"):
            return "PARTIAL"
        return "INVALID"

    def validate_all(self):
        print(f"[*] Starting validation on '{self.recovered_dir}' directory...")
        p = Path(self.recovered_dir)
        if not p.exists():
            return
        for file in sorted(p.iterdir()):
            if file.is_file():
                status = self.validate_file(str(file))
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f" -> {file.name} ({size_mb:.2f} MB): {status}")


__all__ = ["verify_recovery", "FileValidator"]
