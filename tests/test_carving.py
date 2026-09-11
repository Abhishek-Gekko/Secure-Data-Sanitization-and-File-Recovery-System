from app.recovery.carving import carve_bytes


def test_carves_complete_pdf():
    payload = b"noise%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOFtrailing"
    artifacts = carve_bytes(payload)
    pdf = next(item for item in artifacts if item.file_type == "pdf")
    assert pdf.data.endswith(b"%%EOF")
    assert pdf.complete
