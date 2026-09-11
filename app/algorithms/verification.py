"""Independent post-operation verification for recovery and sanitization."""

from __future__ import annotations

import hashlib
import math
import struct
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

from app.algorithms.confidence import recovery_confidence, sanitization_confidence
from app.models import RecoveryResult, SanitizationResult
from app.recovery.carving import SIGNATURES, carve_bytes


def _read(source: str | Path | bytes | bytearray) -> bytes:
    return bytes(source) if isinstance(source, (bytes, bytearray)) else Path(source).read_bytes()


def digest(source: str | Path | bytes | bytearray, algorithm: str = "sha256") -> str:
    hasher = hashlib.new(algorithm)
    if isinstance(source, (bytes, bytearray)):
        hasher.update(source)
    else:
        with Path(source).open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(block)
    return hasher.hexdigest()


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    size = len(data)
    return -sum((count / size) * math.log2(count / size) for count in Counter(data).values())


def _expected_kind(method: str) -> str:
    return {"zero": "zero", "nist_clear": "zero", "random": "random", "dod_5220_22_m": "random",
            "nist_purge": "random", "ones": "ones"}.get(method.lower(), "unknown")


def verify_sanitization(
    source: str | Path | bytes | bytearray,
    *,
    method: str = "zero",
    metadata_destroyed: bool = False,
) -> SanitizationResult:
    """Assess an accessible wiped range; deleted paths must be verified pre-unlink."""
    try:
        data = _read(source)
    except (OSError, ValueError) as exc:
        return SanitizationResult(method, 0, None, False, 0.0, {"error": str(exc)})
    kind = _expected_kind(method)
    entropy = shannon_entropy(data)
    if kind == "zero":
        pattern = 1.0 if not data or all(byte == 0 for byte in data) else 0.0
        entropy_score = 1.0 if entropy == 0.0 else 0.0
    elif kind == "ones":
        pattern = 1.0 if not data or all(byte == 0xFF for byte in data) else 0.0
        entropy_score = 1.0 if entropy == 0.0 else 0.0
    elif kind == "random":
        # Entropy is the primary defensible random-wipe indicator. A normalized
        # distribution score exposes weak random sources without pretending it is proof.
        entropy_score = max(0.0, min(1.0, (entropy - 7.5) / 0.4)) if len(data) >= 256 else entropy / 8
        counts = Counter(data)
        expected = len(data) / 256 if data else 0
        max_deviation = max((abs(count - expected) / expected for count in counts.values()), default=0.0) if expected else 0.0
        pattern = min(1.0, entropy / 8) if max_deviation < 2.0 else 0.0
    else:
        pattern, entropy_score = 0.0, 0.0

    signatures = [name for name, header, _ in SIGNATURES if header in data]
    artifacts = carve_bytes(data)
    negative_carving = not artifacts
    confidence = sanitization_confidence({
        "pattern_uniformity": pattern,
        "negative_carving": negative_carving,
        "entropy_compliance": entropy_score,
        "metadata_destruction": metadata_destroyed,
    })
    sanitized = bool(pattern >= 0.95 and entropy_score >= 0.95 and not signatures and negative_carving)
    return SanitizationResult(method, len(data), round(entropy, 5), sanitized, confidence.score, {
        "verdict": confidence.verdict,
        "confidence_components": confidence.components,
        "detected_signatures": signatures,
        "carved_artifacts": len(artifacts),
        "expected_pattern": kind,
        "pattern_uniformity": pattern,
        "entropy_compliance": entropy_score,
        "metadata_destroyed": metadata_destroyed,
    })


def _extension_magic(data: bytes, suffix: str) -> bool:
    suffix = suffix.lower()
    expected = {".jpg": b"\xff\xd8\xff", ".jpeg": b"\xff\xd8\xff", ".png": b"\x89PNG\r\n\x1a\n",
                ".pdf": b"%PDF-", ".zip": b"PK\x03\x04", ".mp4": b"ftyp"}
    marker = expected.get(suffix)
    return True if marker is None and suffix in {".txt", ".text"} else (marker in data[:32] if marker else False)


def _valid_png(data: bytes) -> bool:
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return False
    offset, seen_iend = 8, False
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            return False
        if kind == b"IEND":
            seen_iend = length == 0 and end == len(data)
            break
        offset = end
    return seen_iend


def _structural_valid(data: bytes, suffix: str) -> tuple[bool, str | None]:
    suffix = suffix.lower()
    if suffix == ".png":
        return _valid_png(data), None
    if suffix in {".jpg", ".jpeg"}:
        return data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"), None
    if suffix == ".pdf":
        return data.startswith(b"%PDF-") and b"%%EOF" in data[-2048:], None
    if suffix == ".zip":
        return data.startswith(b"PK") and b"PK\x05\x06" in data[-65557:], None
    if suffix in {".txt", ".text"}:
        try:
            data.decode("utf-8")
            return True, None
        except UnicodeDecodeError as exc:
            return False, str(exc)
    return _extension_magic(data, suffix), None


def _parser_test(path: Path, suffix: str) -> tuple[bool, str | None]:
    try:
        if suffix == ".zip":
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                if bad:
                    return False, f"CRC error in {bad}"
        elif suffix == ".pdf":
            try:
                from pypdf import PdfReader  # type: ignore[import-not-found]
            except ImportError:
                return True, "pypdf unavailable; structural check used"
            PdfReader(str(path))
        elif suffix in {".png", ".jpg", ".jpeg"}:
            try:
                from PIL import Image  # type: ignore[import-not-found]
            except ImportError:
                return True, "Pillow unavailable; structural check used"
            with Image.open(path) as image:
                image.verify()
        return True, None
    except Exception as exc:  # parser libraries expose many format-specific errors
        return False, f"{type(exc).__name__}: {exc}"


def verify_recovery(
    recovered_path: str | Path,
    *,
    baseline_hash: str | None = None,
    hash_algorithm: str = "sha256",
    expected_size: int | None = None,
) -> RecoveryResult:
    """Verify a recovered file's hash, structure, parser load, and completeness."""
    path = Path(recovered_path)
    try:
        data = path.read_bytes()
        recovered_hash = digest(data, hash_algorithm)
    except (OSError, ValueError) as exc:
        return RecoveryResult("verification", path, baseline_hash, None, False, 0.0, {"error": str(exc)})
    magic = _extension_magic(data, path.suffix)
    structural, structural_error = _structural_valid(data, path.suffix)
    parser_ok, parser_error = _parser_test(path, path.suffix.lower())
    # Without an original digest, hash integrity is unknown rather than falsely
    # presented as a match. Structural evidence still supports a useful score.
    hash_metric: float | None = None if baseline_hash is None else float(recovered_hash.lower() == baseline_hash.lower())
    completeness = 1.0 if expected_size is None else min(1.0, len(data) / expected_size) if expected_size else 1.0
    confidence = recovery_confidence({"hash_integrity": hash_metric, "structural_validation": structural and magic,
                                      "parser_load": parser_ok, "completeness": completeness})
    valid = bool(structural and magic and parser_ok and (baseline_hash is None or hash_metric == 1.0))
    return RecoveryResult("verification", path, baseline_hash, recovered_hash, valid, confidence.score, {
        "verdict": confidence.verdict,
        "confidence_components": confidence.components,
        "magic_valid": magic,
        "structural_valid": structural,
        "structural_error": structural_error,
        "parser_valid": parser_ok,
        "parser_message": parser_error,
        "size": len(data), "expected_size": expected_size,
    })
