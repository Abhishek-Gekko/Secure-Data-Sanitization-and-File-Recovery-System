"""Helpers for controlled fragmented-file reassembly."""

from __future__ import annotations

from collections.abc import Iterable


def reassemble_fragments(fragments: Iterable[bytes], *, header: bytes | None = None, footer: bytes | None = None) -> tuple[bytes, bool]:
    """Join analyst-selected clusters and report whether expected boundaries fit."""
    data = b"".join(fragments)
    valid = bool(data) and (header is None or data.startswith(header)) and (footer is None or data.endswith(footer))
    return data, valid
