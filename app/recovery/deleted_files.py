"""Metadata-record driven restoration after an examiner identifies extents."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .filesystem import restore_from_extents


@dataclass(frozen=True, slots=True)
class DeletedFileRecord:
    """Filesystem-parser-neutral representation of a deleted MFT/inode record."""

    name: str
    extents: tuple[tuple[int, int], ...]
    allocated_size: int | None = None
    filesystem: str | None = None


def recover_from_metadata(image: str | Path, record: DeletedFileRecord, destination: str | Path) -> Path:
    """Restore data referenced by a deleted-record's known cluster extents."""
    output = restore_from_extents(image, list(record.extents), destination)
    if record.allocated_size is not None and output.stat().st_size != record.allocated_size:
        raise ValueError("reassembled extent length differs from metadata allocated_size")
    return output
