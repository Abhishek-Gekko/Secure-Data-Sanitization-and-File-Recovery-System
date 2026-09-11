"""File-level sanitization operations.

These routines intentionally only accept regular files.  They do not write raw
devices, which avoids silently destroying an entire mounted volume.
"""

from __future__ import annotations

import os
import secrets
import string
import sys
from pathlib import Path
from typing import Callable

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.algorithms.verification import shannon_entropy, verify_sanitization
from app.models import SanitizationResult

CHUNK_SIZE = 1024 * 1024
METHODS = {"zero", "random", "dod_5220_22_m", "nist_clear", "nist_purge"}


def _random_name(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _writer(kind: str) -> Callable[[int], bytes]:
    if kind == "zero":
        return lambda size: b"\x00" * size
    if kind == "ones":
        return lambda size: b"\xff" * size
    return os.urandom


def _overwrite(path: Path, generator: Callable[[int], bytes], chunk_size: int) -> int:
    total = 0
    with path.open("r+b", buffering=0) as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            handle.seek(-len(block), os.SEEK_CUR)
            handle.write(generator(len(block)))
            total += len(block)
        handle.flush()
        os.fsync(handle.fileno())
    return total


def sanitize_file(
    target: str | Path,
    method: str = "zero",
    *,
    confirm: bool = False,
    delete: bool = False,
    nullify_metadata: bool = False,
    chunk_size: int = CHUNK_SIZE,
) -> SanitizationResult:
    """Overwrite a regular file and verify it.

    ``confirm=True`` is required because overwriting cannot be undone.  For
    deletion workflows also pass ``delete=True``; otherwise the wiped file is
    retained for audit and independent verification.
    """
    path = Path(target)
    method = method.lower()
    if method not in METHODS:
        raise ValueError(f"unknown sanitization method: {method}")
    if not confirm:
        raise PermissionError("destructive overwrite requires confirm=True")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if path.is_symlink() or not path.is_file():
        raise ValueError("target must be an existing non-symlink regular file")

    passes = {"zero": ["zero"], "random": ["random"], "dod_5220_22_m": ["zero", "ones", "random"],
              "nist_clear": ["zero"], "nist_purge": ["random"]}[method]
    bytes_overwritten = 0
    try:
        for pass_kind in passes:
            bytes_overwritten += _overwrite(path, _writer(pass_kind), chunk_size)

        # The final state is assessed before optional unlinking.
        verification = verify_sanitization(path, method=method)
        details = dict(verification.details)
        details.update({"passes": passes, "metadata_nullified": False, "deleted": False})
        if nullify_metadata:
            os.utime(path, (0, 0))
            details["metadata_nullified"] = True
        if delete:
            if not nullify_metadata:
                os.utime(path, (0, 0))
                details["metadata_nullified"] = True
            renamed = path.with_name(_random_name() + path.suffix)
            path.rename(renamed)
            renamed.unlink()
            details["deleted"] = True
            details["renamed_before_deletion"] = True
        return SanitizationResult(method, bytes_overwritten, verification.entropy, verification.is_sanitized,
                                  verification.confidence_score, details)
    except (OSError, PermissionError) as exc:
        return SanitizationResult(method, bytes_overwritten, None, False, 0.0,
                                  {"error": str(exc), "target": str(path)})


def quick_zero_fill(target: str | Path, **kwargs: object) -> SanitizationResult:
    return sanitize_file(target, "zero", **kwargs)


def pseudorandom_wipe(target: str | Path, **kwargs: object) -> SanitizationResult:
    return sanitize_file(target, "random", **kwargs)


def dod_5220_22_m(target: str | Path, **kwargs: object) -> SanitizationResult:
    return sanitize_file(target, "dod_5220_22_m", **kwargs)


def nist_800_88(target: str | Path, level: str = "clear", **kwargs: object) -> SanitizationResult:
    if level not in {"clear", "purge"}:
        raise ValueError("NIST level must be 'clear' or 'purge'")
    return sanitize_file(target, f"nist_{level}", **kwargs)


if __name__ == "__main__":
    import tempfile
    print("==================================================================")
    print("  AEGIS FORENSICS: File Sanitization Module (Direct Execution)     ")
    print("==================================================================")
    print("Supported methods:", list(METHODS))
    with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
        tf.write(b"TOP SECRET INTEL " * 256)
        temp_path = Path(tf.name)
    print(f"\nCreated temporary test target: {temp_path} ({temp_path.stat().st_size} bytes)")
    print("Executing DoD 5220.22-M 3-pass wipe (confirm=True)...")
    res = dod_5220_22_m(temp_path, confirm=True)
    print(f"Sanitized: {res.is_sanitized}")
    print(f"Bytes Overwritten: {res.bytes_overwritten}")
    print(f"Confidence Score: {res.confidence_score}%")
    print(f"Details: {res.details}")
    temp_path.unlink(missing_ok=True)
    print("\nTo launch the complete Web UI, run: python run.py")
