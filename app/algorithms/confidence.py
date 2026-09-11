"""Deterministic, explainable confidence scoring."""

from __future__ import annotations

from collections.abc import Mapping

from app.models import ConfidenceResult

SANITIZATION_WEIGHTS = {
    "pattern_uniformity": 0.35,
    "negative_carving": 0.30,
    "entropy_compliance": 0.25,
    "metadata_destruction": 0.10,
}
RECOVERY_WEIGHTS = {
    "hash_integrity": 0.40,
    "structural_validation": 0.30,
    "parser_load": 0.20,
    "completeness": 0.10,
}


def _value(value: float | bool | None) -> float:
    if value is True:
        return 1.0
    if value is False or value is None:
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _verdict(score: float) -> str:
    if score >= 90:
        return "CONFIRMED"
    if score >= 70:
        return "PROBABLE"
    if score >= 40:
        return "UNCERTAIN"
    return "FAILED"


def score(metrics: Mapping[str, float | bool | None], weights: Mapping[str, float]) -> ConfidenceResult:
    """Score named 0..1 metrics. Missing metrics deliberately count as zero."""
    components = {name: round(_value(metrics.get(name)) * weight * 100, 2) for name, weight in weights.items()}
    final = round(sum(components.values()), 2)
    return ConfidenceResult(score=final, verdict=_verdict(final), components=components)


def sanitization_confidence(metrics: Mapping[str, float | bool | None]) -> ConfidenceResult:
    return score(metrics, SANITIZATION_WEIGHTS)


def recovery_confidence(metrics: Mapping[str, float | bool | None]) -> ConfidenceResult:
    return score(metrics, RECOVERY_WEIGHTS)
