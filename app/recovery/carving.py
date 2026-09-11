"""Signature-based carving from byte buffers or forensic image files."""

from __future__ import annotations

from pathlib import Path

from app.models import CarvedArtifact

# (name, header, footer). MP4 has no universal footer; its extent runs to the
# next recognized header or end of input and is marked incomplete when needed.
SIGNATURES: tuple[tuple[str, bytes, bytes | None], ...] = (
    ("jpeg", b"\xff\xd8\xff", b"\xff\xd9"),
    ("png", b"\x89PNG\r\n\x1a\n", b"IEND\xaeB`\x82"),
    ("pdf", b"%PDF-", b"%%EOF"),
    ("zip", b"PK\x03\x04", b"PK\x05\x06"),
    ("mp4", b"ftyp", None),
)
EXTENSIONS = {"jpeg": ".jpg", "png": ".png", "pdf": ".pdf", "zip": ".zip", "mp4": ".mp4", "txt": ".txt"}


def _next_signature(data: bytes, start: int) -> int:
    hits = [data.find(header, start) for _, header, _ in SIGNATURES if data.find(header, start) >= 0]
    return min(hits) if hits else len(data)


def _zip_end(data: bytes, start: int) -> int | None:
    """Find EOCD and honor its optional comment length."""
    marker = data.find(b"PK\x05\x06", start)
    if marker < 0 or marker + 22 > len(data):
        return None
    comment_length = int.from_bytes(data[marker + 20: marker + 22], "little")
    end = marker + 22 + comment_length
    return end if end <= len(data) else None


def carve_bytes(data: bytes, *, minimum_text_length: int = 32) -> list[CarvedArtifact]:
    """Return recoverable contiguous artifacts without writing to disk."""
    artifacts: list[CarvedArtifact] = []
    for file_type, header, footer in SIGNATURES:
        offset = 0
        while (found := data.find(header, offset)) >= 0:
            start = found - 4 if file_type == "mp4" and found >= 4 else found
            if file_type == "zip":
                end = _zip_end(data, found + len(header))
            elif footer:
                footer_at = data.find(footer, found + len(header))
                end = footer_at + len(footer) if footer_at >= 0 else None
            else:
                end = _next_signature(data, found + len(header))
            complete = end is not None
            endpoint = end if end is not None else _next_signature(data, found + len(header))
            artifacts.append(CarvedArtifact(file_type, start, endpoint - start, data[start:endpoint], complete=complete))
            offset = max(found + len(header), endpoint)

    # Text has no magic bytes. Preserve only sizeable printable/UTF-8-ish runs
    # delimited by NUL bytes, avoiding arbitrary binary false positives.
    for segment_start, segment in _nul_segments(data):
        if len(segment) >= minimum_text_length and _is_text(segment):
            artifacts.append(CarvedArtifact("txt", segment_start, len(segment), segment))
    return sorted(artifacts, key=lambda artifact: artifact.offset)


def _nul_segments(data: bytes):
    cursor = 0
    for part in data.split(b"\x00"):
        yield cursor, part
        cursor += len(part) + 1


def _is_text(value: bytes) -> bool:
    try:
        value.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return bool(value) and sum(byte >= 32 or byte in (9, 10, 13) for byte in value) / len(value) >= 0.95


def carve_file(image_path: str | Path, output_dir: str | Path | None = None) -> list[CarvedArtifact]:
    """Carve an image and optionally persist each extraction to ``output_dir``."""
    source = Path(image_path)
    artifacts = carve_bytes(source.read_bytes())
    if output_dir is not None:
        destination = Path(output_dir)
        destination.mkdir(parents=True, exist_ok=True)
        for number, artifact in enumerate(artifacts, 1):
            output = destination / f"carved_{number:04d}_{artifact.offset}{EXTENSIONS[artifact.file_type]}"
            output.write_bytes(artifact.data)
            artifact.recovered_path = output
    return artifacts
