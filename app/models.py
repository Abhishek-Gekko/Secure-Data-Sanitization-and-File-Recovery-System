"""Public result models used by the sanitization and recovery engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SanitizationResult:
    method: str
    bytes_overwritten: int = 0
    entropy: float | None = None
    is_sanitized: bool = False
    confidence_score: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RecoveryResult:
    method: str
    recovered_path: Path | None = None
    original_hash: str | None = None
    recovered_hash: str | None = None
    is_valid: bool = False
    confidence_score: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConfidenceResult:
    score: float
    verdict: str
    components: dict[str, float]


@dataclass(slots=True)
class CarvedArtifact:
    file_type: str
    offset: int
    length: int
    data: bytes
    recovered_path: Path | None = None
    complete: bool = True
