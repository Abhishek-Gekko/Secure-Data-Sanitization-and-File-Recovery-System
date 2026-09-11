from app.sanitization import dod_5220_22_m, quick_zero_fill


def test_zero_fill_requires_explicit_confirmation(tmp_path):
    target = tmp_path / "secret.bin"
    target.write_bytes(b"secret data" * 100)
    try:
        quick_zero_fill(target)
    except PermissionError:
        pass
    else:
        raise AssertionError("confirmation must be required")
    result = quick_zero_fill(target, confirm=True)
    assert target.read_bytes() == b"\x00" * 1100
    assert result.is_sanitized
    assert result.bytes_overwritten == 1100


def test_dod_performs_three_passes(tmp_path):
    target = tmp_path / "secret.bin"
    target.write_bytes(b"x" * 4096)
    result = dod_5220_22_m(target, confirm=True)
    assert result.bytes_overwritten == 4096 * 3
    assert result.is_sanitized
