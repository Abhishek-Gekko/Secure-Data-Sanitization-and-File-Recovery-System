"""Portable metadata recovery abstractions.

Python cannot safely inspect deleted MFT/inode entries without a filesystem
parser. This module restores files from analyst-supplied extents, which is the
same final step used after such a parser identifies clusters.
"""

from __future__ import annotations

from pathlib import Path


def restore_from_extents(image: str | Path, extents: list[tuple[int, int]], destination: str | Path) -> Path:
    source, output = Path(image), Path(destination)
    if any(offset < 0 or length <= 0 for offset, length in extents):
        raise ValueError("extents must contain non-negative offsets and positive lengths")
    with source.open("rb") as input_handle, output.open("wb") as output_handle:
        for offset, length in extents:
            input_handle.seek(offset)
            block = input_handle.read(length)
            if len(block) != length:
                raise ValueError("extent extends beyond image")
            output_handle.write(block)
    return output
